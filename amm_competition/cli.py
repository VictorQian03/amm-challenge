"""Command-line interface for running AMM simulations and hill climbing."""

import argparse
from dataclasses import asdict, is_dataclass
import json
import sys
from pathlib import Path
from typing import Any, cast

from amm_sim_rs import SimulationConfig
from amm_competition.competition.match import MatchRunner, HyperparameterVariance
from amm_competition.competition.protected_surface import ProtectedSurfaceChecker
from amm_competition.evm.adapter import EVMStrategyAdapter
from amm_competition.evm.baseline import load_vanilla_strategy
from amm_competition.evm.compiler import SolidityCompiler
from amm_competition.evm.validator import SolidityValidator
from amm_competition.hill_climb.harness import (
    DEFAULT_ACTIVE_STRATEGY_PATH,
    HillClimbHarness,
    HillClimbHarnessError,
)
from amm_competition.hill_climb.stages import HILL_CLIMB_STAGES

from amm_competition.competition.config import (
    BASELINE_SETTINGS,
    BASELINE_VARIANCE,
    baseline_nominal_retail_rate,
    baseline_nominal_retail_size,
    baseline_nominal_sigma,
    resolve_n_workers,
)


def _validate_active_hill_climb_strategy_path(strategy_path: Path) -> Path:
    expected_path = DEFAULT_ACTIVE_STRATEGY_PATH.resolve()
    resolved_path = strategy_path.resolve()
    if resolved_path != expected_path:
        raise HillClimbHarnessError(
            "Hill-climb eval only supports the documented active strategy path "
            f"{DEFAULT_ACTIVE_STRATEGY_PATH}. Copy your candidate there before evaluating."
        )
    return resolved_path


def _compiled_bytecode_or_raise(compilation, *, context: str) -> bytes:
    if compilation.bytecode is None:
        raise RuntimeError(f"{context} succeeded without deployment bytecode")
    return compilation.bytecode


def _print_warnings(warnings: list[str]) -> None:
    for warning in warnings:
        print(f"Warning: {warning}")


def _json_default(value: object) -> object:
    if isinstance(value, Path):
        return str(value)
    if is_dataclass(value) and not isinstance(value, type):
        return asdict(cast(Any, value))
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def _print_json(payload: object) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True, default=_json_default))


def _parse_float_pairs(
    pairs: list[str] | None, *, field_name: str
) -> dict[str, float] | None:
    if not pairs:
        return None
    payload: dict[str, float] = {}
    for raw_pair in pairs:
        if "=" not in raw_pair:
            raise HillClimbHarnessError(
                f"Expected {field_name} entry in key=value form, found {raw_pair!r}"
            )
        key, raw_value = raw_pair.split("=", 1)
        key = key.strip()
        if not key:
            raise HillClimbHarnessError(
                f"Expected non-empty key in {field_name} entry {raw_pair!r}"
            )
        if key in payload:
            raise HillClimbHarnessError(
                f"Duplicate {field_name} metric {key!r} is not allowed"
            )
        try:
            payload[key] = float(raw_value)
        except ValueError as exc:
            raise HillClimbHarnessError(
                f"Expected finite numeric value for {field_name} metric {key!r}, found {raw_value!r}"
            ) from exc
    return payload


def _parse_json_object(
    raw_payload: str | None, *, field_name: str
) -> dict[str, object] | None:
    if raw_payload is None:
        return None
    try:
        payload = json.loads(raw_payload)
    except json.JSONDecodeError as exc:
        raise HillClimbHarnessError(
            f"Expected {field_name} to be a JSON object, found invalid JSON: {exc.msg}"
        ) from exc
    if not isinstance(payload, dict):
        raise HillClimbHarnessError(f"Expected {field_name} to be a JSON object")
    return payload


def _profile_slot_input(
    *,
    label: str,
    eval_id: str | None,
    source_path: str | None,
    required: bool,
) -> tuple[str | None, str | None]:
    if eval_id and source_path:
        raise HillClimbHarnessError(
            f"Choose either --{label}-eval-id or --{label}-source, not both"
        )
    if required and eval_id is None and source_path is None:
        raise HillClimbHarnessError(
            f"Provide one of --{label}-eval-id or --{label}-source"
        )
    return eval_id, source_path


def _add_json_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit a machine-readable JSON payload instead of human text",
    )


def run_match_command(args: argparse.Namespace) -> int:
    """Run simulations for a strategy and report its score."""
    strategy_path = Path(args.strategy)
    if not strategy_path.exists():
        print(f"Error: Strategy file not found: {strategy_path}")
        return 1

    # Read Solidity source
    source_code = strategy_path.read_text()

    # Validate
    print("Validating strategy...")
    validator = SolidityValidator()
    validation = validator.validate(source_code)
    if not validation.valid:
        print("Validation failed:")
        for error in validation.errors:
            print(f"  - {error}")
        return 1

    # Compile
    print("Compiling strategy...")
    compiler = SolidityCompiler()
    compilation = compiler.compile(source_code)
    if not compilation.success:
        print("Compilation failed:")
        for error in compilation.errors or []:
            print(f"  - {error}")
        return 1

    # Create strategy adapter
    user_strategy = EVMStrategyAdapter(
        bytecode=_compiled_bytecode_or_raise(compilation, context="Compilation"),
        abi=compilation.abi,
    )
    strategy_name = user_strategy.get_name()
    print(f"Strategy: {strategy_name}")

    # Load default 30bps strategy (used as the other AMM in simulation)
    default_strategy = load_vanilla_strategy()

    # Configure simulation
    n_steps = args.steps if args.steps is not None else BASELINE_SETTINGS.n_steps
    initial_price = (
        args.initial_price
        if args.initial_price is not None
        else BASELINE_SETTINGS.initial_price
    )
    initial_x = (
        args.initial_x if args.initial_x is not None else BASELINE_SETTINGS.initial_x
    )
    initial_y = (
        args.initial_y if args.initial_y is not None else BASELINE_SETTINGS.initial_y
    )
    gbm_sigma = (
        args.volatility if args.volatility is not None else baseline_nominal_sigma()
    )
    retail_rate = (
        args.retail_rate
        if args.retail_rate is not None
        else baseline_nominal_retail_rate()
    )
    retail_size = (
        args.retail_size
        if args.retail_size is not None
        else baseline_nominal_retail_size()
    )
    retail_size_sigma = (
        args.retail_size_sigma
        if args.retail_size_sigma is not None
        else BASELINE_SETTINGS.retail_size_sigma
    )

    config = SimulationConfig(
        n_steps=n_steps,
        initial_price=initial_price,
        initial_x=initial_x,
        initial_y=initial_y,
        gbm_mu=BASELINE_SETTINGS.gbm_mu,
        gbm_sigma=gbm_sigma,
        gbm_dt=BASELINE_SETTINGS.gbm_dt,
        retail_arrival_rate=retail_rate,
        retail_mean_size=retail_size,
        retail_size_sigma=retail_size_sigma,
        retail_buy_prob=BASELINE_SETTINGS.retail_buy_prob,
        seed=None,
    )

    # Run simulations
    n_simulations = (
        args.simulations
        if args.simulations is not None
        else BASELINE_SETTINGS.n_simulations
    )
    print(f"\nRunning {n_simulations} simulations...")
    variance = HyperparameterVariance(
        retail_mean_size_min=retail_size
        if args.retail_size is not None
        else BASELINE_VARIANCE.retail_mean_size_min,
        retail_mean_size_max=retail_size
        if args.retail_size is not None
        else BASELINE_VARIANCE.retail_mean_size_max,
        vary_retail_mean_size=False
        if args.retail_size is not None
        else BASELINE_VARIANCE.vary_retail_mean_size,
        retail_arrival_rate_min=retail_rate
        if args.retail_rate is not None
        else BASELINE_VARIANCE.retail_arrival_rate_min,
        retail_arrival_rate_max=retail_rate
        if args.retail_rate is not None
        else BASELINE_VARIANCE.retail_arrival_rate_max,
        vary_retail_arrival_rate=False
        if args.retail_rate is not None
        else BASELINE_VARIANCE.vary_retail_arrival_rate,
        gbm_sigma_min=gbm_sigma
        if args.volatility is not None
        else BASELINE_VARIANCE.gbm_sigma_min,
        gbm_sigma_max=gbm_sigma
        if args.volatility is not None
        else BASELINE_VARIANCE.gbm_sigma_max,
        vary_gbm_sigma=False
        if args.volatility is not None
        else BASELINE_VARIANCE.vary_gbm_sigma,
    )

    runner = MatchRunner(
        n_simulations=n_simulations,
        config=config,
        n_workers=resolve_n_workers(),
        variance=variance,
    )
    result = runner.run_match(user_strategy, default_strategy)

    # Display score (only the user's strategy Edge)
    avg_edge = result.total_edge_a / n_simulations
    print(f"\n{strategy_name} Edge: {avg_edge:.2f}")

    return 0


def validate_command(args: argparse.Namespace) -> int:
    """Validate a Solidity strategy file without running it."""
    strategy_path = Path(args.strategy)
    if not strategy_path.exists():
        print(f"Error: Strategy file not found: {strategy_path}")
        return 1

    source_code = strategy_path.read_text()

    # Validate
    print("Validating strategy...")
    validator = SolidityValidator()
    validation = validator.validate(source_code)
    if not validation.valid:
        print("Validation failed:")
        for error in validation.errors:
            print(f"  - {error}")
        return 1

    if validation.warnings:
        print("Warnings:")
        for warning in validation.warnings:
            print(f"  - {warning}")

    # Compile
    print("Compiling strategy...")
    compiler = SolidityCompiler()
    compilation = compiler.compile(source_code)
    if not compilation.success:
        print("Compilation failed:")
        for error in compilation.errors or []:
            print(f"  - {error}")
        return 1

    # Test deployment
    try:
        from decimal import Decimal

        strategy = EVMStrategyAdapter(
            bytecode=_compiled_bytecode_or_raise(compilation, context="Compilation"),
            abi=compilation.abi,
        )
        strategy.after_initialize(Decimal("100"), Decimal("10000"))
        print(f"Strategy '{strategy.get_name()}' validated successfully!")
        return 0
    except Exception as e:
        print(f"EVM execution failed: {e}")
        return 1


def hill_climb_eval_command(args: argparse.Namespace) -> int:
    """Evaluate a candidate inside the hill-climb harness."""
    try:
        strategy_path = _validate_active_hill_climb_strategy_path(Path(args.strategy))
        ProtectedSurfaceChecker.discover().ensure_runtime_eval_allowed()
        harness = HillClimbHarness(
            artifact_root=Path(args.artifact_root),
            n_workers=resolve_n_workers(),
        )
        summary = harness.evaluate(
            run_id=args.run_id,
            stage=args.stage,
            source_path=strategy_path,
            label=args.label,
            description=args.description,
            hypothesis_id=getattr(args, "hypothesis_id", None),
            parent_eval_id=getattr(args, "parent_eval_id", None),
            change_summary=getattr(args, "change_summary", None),
            research_refs=list(getattr(args, "research_refs", []) or []),
            replay_reason=getattr(args, "replay_reason", None),
        )
        state = (
            harness.get_run_state(run_id=args.run_id)
            if hasattr(harness, "get_run_state")
            else None
        )
    except (HillClimbHarnessError, RuntimeError, ValueError) as exc:
        print(f"Hill-climb evaluation failed: {exc}")
        return 1

    if getattr(args, "json", False):
        _print_json(
            {
                "summary": summary,
                "state": None if state is None else asdict(state),
            }
        )
        return 0

    print(f"Run: {summary['run_id']}")
    print(f"Eval: {summary['eval_id']}")
    print(f"Stage: {summary['stage']}")
    print(f"Status: {summary['status']}")
    print(f"Mean Edge: {summary['mean_edge']:.6f}")
    if summary.get("hypothesis_id"):
        print(f"Hypothesis: {summary['hypothesis_id']}")
    if summary.get("parent_eval_id"):
        print(f"Parent Eval: {summary['parent_eval_id']}")
    if summary.get("change_summary"):
        print(f"Change Summary: {summary['change_summary']}")
    if summary.get("research_refs"):
        print("Research Refs: " + ", ".join(summary["research_refs"]))
    if summary.get("replay_reason"):
        print(f"Replay Reason: {summary['replay_reason']}")
    selection = summary.get("selection", {})
    if selection.get("promotion_margin") is not None:
        print(f"Promotion Margin: {selection['promotion_margin']:.6f}")
    if selection.get("rationale"):
        print(f"Decision: {selection['rationale']}")
    if state is None or state.outcome_gate is None:
        print("Outcome Gate: none")
    else:
        print(f"Outcome Gate: {state.outcome_gate.message}")
    print(f"Artifacts: {Path(summary['snapshot_path']).parent}")
    return 0


def hill_climb_status_command(args: argparse.Namespace) -> int:
    """Report incumbent and latest evaluation for one run stage."""
    try:
        harness = HillClimbHarness(
            artifact_root=Path(args.artifact_root),
            n_workers=resolve_n_workers(),
        )
        warnings = harness.get_read_warnings(
            run_id=args.run_id,
            allow_protected_surface_drift=getattr(args, "read_only", False),
        )
        status = harness.get_stage_status(
            run_id=args.run_id,
            stage=args.stage,
            allow_protected_surface_drift=getattr(args, "read_only", False),
        )
        state = harness.get_run_state(
            run_id=args.run_id,
            allow_protected_surface_drift=getattr(args, "read_only", False),
        )
    except (HillClimbHarnessError, RuntimeError, ValueError) as exc:
        print(f"Hill-climb status failed: {exc}")
        return 1

    if getattr(args, "json", False):
        _print_json(
            {
                "warnings": warnings,
                "stage_status": asdict(status),
                "run_state": asdict(state),
            }
        )
        return 0

    _print_warnings(warnings)
    print(f"Run: {status.run_id}")
    print(f"Stage: {status.stage}")
    if status.incumbent is None:
        print("Incumbent: none")
    else:
        print(
            "Incumbent: "
            f"{status.incumbent['eval_id']} "
            f"({status.incumbent['mean_edge']:.6f}, {status.incumbent['status']})"
        )
    if status.latest is None:
        print("Latest: none")
    else:
        latest_mean_edge = status.latest["mean_edge"]
        latest_display = (
            "n/a" if latest_mean_edge is None else f"{latest_mean_edge:.6f}"
        )
        print(
            "Latest: "
            f"{status.latest['eval_id']} "
            f"({latest_display}, {status.latest['status']})"
        )
    print(f"Current Target Stage: {state.current_target_stage}")
    print(f"Run Mode: {state.run_mode}")
    if state.next_hypothesis_id is None:
        print("Next Hypothesis: none")
    elif state.next_hypothesis_note:
        print(
            f"Next Hypothesis: {state.next_hypothesis_id} ({state.next_hypothesis_note})"
        )
    else:
        print(f"Next Hypothesis: {state.next_hypothesis_id}")
    if state.outcome_gate is None:
        print("Outcome Gate: none")
    else:
        print(f"Outcome Gate: {state.outcome_gate.message}")
    print(
        "Stop Rules: "
        f"refine={state.stop_rules['refine_after_non_improving_iterations']}, "
        f"pivot={state.stop_rules['pivot_after_non_improving_iterations']}, "
        f"stop={state.stop_rules['stop_after_non_improving_iterations']}"
    )
    print(f"Target-Stage Non-Improving Streak: {state.guidance.non_improving_streak}")
    print(f"Stop-Rule Guidance: {state.guidance.message}")
    return 0


def hill_climb_set_state_command(args: argparse.Namespace) -> int:
    """Persist explicit loop-state metadata for an existing run."""
    next_hypothesis_id_arg = getattr(args, "next_hypothesis_id", None)
    next_hypothesis_note_arg = getattr(args, "next_hypothesis_note", None)
    clear_next_hypothesis = getattr(args, "clear_next_hypothesis", False)
    if next_hypothesis_id_arg is not None and clear_next_hypothesis:
        print(
            "Hill-climb state update failed: choose either --next-hypothesis-id or --clear-next-hypothesis"
        )
        return 1
    if (args.breakout_stage is None) != (args.breakout_threshold is None):
        print(
            "Hill-climb state update failed: choose both --breakout-stage and --breakout-threshold"
        )
        return 1
    if (args.breakout_stage is not None or args.breakout_threshold is not None) and (
        args.clear_breakout_goal
    ):
        print(
            "Hill-climb state update failed: choose either a breakout goal or --clear-breakout-goal"
        )
        return 1

    try:
        harness = HillClimbHarness(
            artifact_root=Path(args.artifact_root),
            n_workers=resolve_n_workers(),
        )
        existing_state = harness.get_run_state(run_id=args.run_id)
        next_hypothesis_id = next_hypothesis_id_arg
        next_hypothesis_note = next_hypothesis_note_arg
        if clear_next_hypothesis:
            next_hypothesis_id = None
            next_hypothesis_note = None
        elif next_hypothesis_note is not None and next_hypothesis_id is None:
            next_hypothesis_id = existing_state.next_hypothesis_id
        stop_rules = None
        if any(
            value is not None
            for value in (args.refine_after, args.pivot_after, args.stop_after)
        ):
            existing = existing_state.stop_rules
            stop_rules = {
                "refine_after_non_improving_iterations": (
                    args.refine_after
                    if args.refine_after is not None
                    else existing["refine_after_non_improving_iterations"]
                ),
                "pivot_after_non_improving_iterations": (
                    args.pivot_after
                    if args.pivot_after is not None
                    else existing["pivot_after_non_improving_iterations"]
                ),
                "stop_after_non_improving_iterations": (
                    args.stop_after
                    if args.stop_after is not None
                    else existing["stop_after_non_improving_iterations"]
                ),
            }
        outcome_gate = None
        if args.breakout_stage is not None:
            outcome_gate = {
                "stage": args.breakout_stage,
                "minimum_mean_edge": float(args.breakout_threshold),
            }
        state = harness.update_run_state(
            run_id=args.run_id,
            current_target_stage=args.current_target_stage,
            next_hypothesis_id=next_hypothesis_id,
            next_hypothesis_id_set=next_hypothesis_id_arg is not None
            or clear_next_hypothesis,
            next_hypothesis_note=next_hypothesis_note,
            next_hypothesis_note_set=next_hypothesis_note_arg is not None
            or clear_next_hypothesis,
            run_mode=args.run_mode,
            stop_rules=stop_rules,
            outcome_gate=outcome_gate,
            outcome_gate_set=args.breakout_stage is not None
            or args.clear_breakout_goal,
        )
    except (HillClimbHarnessError, RuntimeError, ValueError) as exc:
        print(f"Hill-climb state update failed: {exc}")
        return 1

    if getattr(args, "json", False):
        _print_json(asdict(state))
        return 0

    print(f"Run: {state.run_id}")
    print(f"Current Target Stage: {state.current_target_stage}")
    print(f"Run Mode: {state.run_mode}")
    if state.next_hypothesis_id is None:
        print("Next Hypothesis: none")
    elif state.next_hypothesis_note:
        print(
            f"Next Hypothesis: {state.next_hypothesis_id} ({state.next_hypothesis_note})"
        )
    else:
        print(f"Next Hypothesis: {state.next_hypothesis_id}")
    if state.outcome_gate is None:
        print("Outcome Gate: none")
    else:
        print(f"Outcome Gate: {state.outcome_gate.message}")
    print(
        "Stop Rules: "
        f"refine={state.stop_rules['refine_after_non_improving_iterations']}, "
        f"pivot={state.stop_rules['pivot_after_non_improving_iterations']}, "
        f"stop={state.stop_rules['stop_after_non_improving_iterations']}"
    )
    print(f"Stop-Rule Guidance: {state.guidance.message}")
    return 0


def hill_climb_set_hypothesis_command(args: argparse.Namespace) -> int:
    """Create or update a run hypothesis record."""
    try:
        payload = HillClimbHarness(
            artifact_root=Path(args.artifact_root),
            n_workers=resolve_n_workers(),
        ).upsert_hypothesis(
            run_id=args.run_id,
            hypothesis_id=args.hypothesis_id,
            title=args.title,
            rationale=args.rationale,
            expected_effect=args.expected_effect,
            mutation_family=args.mutation_family,
            status=args.status,
            batch_id=getattr(args, "batch_id", None),
            parent_hypothesis_id=args.parent_hypothesis_id,
            seed_eval_id=args.seed_eval_id,
            research_refs=list(args.research_refs or []),
            target_metrics=_parse_float_pairs(
                getattr(args, "target_metrics", None),
                field_name="target_metrics",
            ),
            hard_guardrails=_parse_float_pairs(
                getattr(args, "hard_guardrails", None),
                field_name="hard_guardrails",
            ),
            expected_failure_mode=getattr(args, "expected_failure_mode", None),
            actual_failure_mode=getattr(args, "actual_failure_mode", None),
            novelty_coordinates=_parse_json_object(
                getattr(args, "novelty_coordinates", None),
                field_name="novelty_coordinates",
            ),
            synthesis_eligible=getattr(args, "synthesis_eligible", None),
            nearest_prior_failures=list(
                getattr(args, "nearest_prior_failures", []) or []
            ),
            nearest_prior_successes=list(
                getattr(args, "nearest_prior_successes", []) or []
            ),
            primary_layer_changed=getattr(args, "primary_layer_changed", None),
            layer_held_fixed=getattr(args, "layer_held_fixed", None),
            hidden_coupling_removed=getattr(args, "hidden_coupling_removed", None),
            why_not_coefficient_retune=getattr(
                args, "why_not_coefficient_retune", None
            ),
            expected_win_condition=getattr(args, "expected_win_condition", None),
            expected_failure_signature=getattr(
                args, "expected_failure_signature", None
            ),
            quote_topology=getattr(args, "quote_topology", None),
            is_topology_branch=getattr(args, "is_topology_branch", None),
        )
    except (HillClimbHarnessError, RuntimeError, ValueError) as exc:
        print(f"Hill-climb hypothesis update failed: {exc}")
        return 1

    if getattr(args, "json", False):
        _print_json(payload)
        return 0

    print(f"Run: {args.run_id}")
    print(f"Hypothesis: {payload['hypothesis_id']}")
    print(f"Status: {payload['status']}")
    print(f"Mutation Family: {payload['mutation_family']}")
    print(f"Eval Count: {len(payload['eval_ids'])}")
    return 0


def hill_climb_history_command(args: argparse.Namespace) -> int:
    """Show the compact history view for a run."""
    try:
        harness = HillClimbHarness(
            artifact_root=Path(args.artifact_root),
            n_workers=resolve_n_workers(),
        )
        warnings = harness.get_read_warnings(
            run_id=args.run_id,
            allow_protected_surface_drift=getattr(args, "read_only", False),
        )
        history = harness.get_history(
            run_id=args.run_id,
            allow_protected_surface_drift=getattr(args, "read_only", False),
        )
    except (HillClimbHarnessError, RuntimeError, ValueError) as exc:
        print(f"Hill-climb history failed: {exc}")
        return 1

    if getattr(args, "json", False):
        _print_json({"warnings": warnings, "history": history})
        return 0

    _print_warnings(warnings)
    print("eval_id\tstage\tstatus\tmean_edge\thypothesis_id\tparent_eval_id\tdecision")
    for entry in history:
        mean_edge = entry["mean_edge"]
        mean_edge_text = "n/a" if mean_edge is None else f"{mean_edge:.6f}"
        print(
            "\t".join(
                [
                    entry["eval_id"],
                    entry["stage"],
                    entry["status"],
                    mean_edge_text,
                    entry.get("hypothesis_id") or "",
                    entry.get("parent_eval_id") or "",
                    entry.get("decision_summary") or "",
                ]
            )
        )
    return 0


def hill_climb_show_eval_command(args: argparse.Namespace) -> int:
    """Show one evaluation with lineage metadata."""
    try:
        harness = HillClimbHarness(
            artifact_root=Path(args.artifact_root),
            n_workers=resolve_n_workers(),
        )
        warnings = harness.get_read_warnings(
            run_id=args.run_id,
            allow_protected_surface_drift=getattr(args, "read_only", False),
        )
        summary = harness.get_evaluation(
            run_id=args.run_id,
            eval_id=args.eval_id,
            allow_protected_surface_drift=getattr(args, "read_only", False),
        )
    except (HillClimbHarnessError, RuntimeError, ValueError) as exc:
        print(f"Hill-climb show-eval failed: {exc}")
        return 1

    if getattr(args, "json", False):
        _print_json({"warnings": warnings, "evaluation": summary})
        return 0

    _print_warnings(warnings)
    print(f"Run: {summary['run_id']}")
    print(f"Eval: {summary['eval_id']}")
    print(f"Stage: {summary['stage']}")
    print(f"Status: {summary['status']}")
    print(f"Label: {summary.get('label') or 'none'}")
    print(f"Hypothesis: {summary.get('hypothesis_id') or 'none'}")
    print(f"Parent Eval: {summary.get('parent_eval_id') or 'none'}")
    print(f"Parent Source: {summary.get('parent_source_sha256') or 'none'}")
    print(f"Change Summary: {summary.get('change_summary') or 'none'}")
    print("Research Refs: " + (", ".join(summary.get("research_refs", [])) or "none"))
    mean_edge = summary.get("mean_edge")
    print(f"Mean Edge: {'n/a' if mean_edge is None else f'{mean_edge:.6f}'}")
    selection = summary.get("selection", {})
    print(f"Decision: {selection.get('rationale') or summary.get('error') or 'none'}")
    failure = summary.get("derived_analysis", {}).get("failure_signature", {})
    print("Failure Tags: " + (", ".join(failure.get("tags", [])) or "none"))
    return 0


def hill_climb_show_hypothesis_command(args: argparse.Namespace) -> int:
    """Show one hypothesis and its linked evaluations."""
    try:
        harness = HillClimbHarness(
            artifact_root=Path(args.artifact_root),
            n_workers=resolve_n_workers(),
        )
        warnings = harness.get_read_warnings(
            run_id=args.run_id,
            allow_protected_surface_drift=getattr(args, "read_only", False),
        )
        payload = harness.get_hypothesis(
            run_id=args.run_id,
            hypothesis_id=args.hypothesis_id,
            allow_protected_surface_drift=getattr(args, "read_only", False),
        )
    except (HillClimbHarnessError, RuntimeError, ValueError) as exc:
        print(f"Hill-climb show-hypothesis failed: {exc}")
        return 1

    if getattr(args, "json", False):
        _print_json({"warnings": warnings, "hypothesis": payload})
        return 0

    _print_warnings(warnings)
    print(f"Run: {args.run_id}")
    print(f"Hypothesis: {payload['hypothesis_id']}")
    print(f"Title: {payload['title']}")
    print(f"Status: {payload['status']}")
    print(f"Mutation Family: {payload['mutation_family']}")
    print(f"Batch: {payload.get('batch_id') or 'none'}")
    print(f"Expected Effect: {payload['expected_effect']}")
    print(f"Rationale: {payload['rationale']}")
    print(f"Parent Hypothesis: {payload.get('parent_hypothesis_id') or 'none'}")
    print(f"Seed Eval: {payload.get('seed_eval_id') or 'none'}")
    print("Eval IDs: " + (", ".join(payload.get("eval_ids", [])) or "none"))
    print("Research Refs: " + (", ".join(payload.get("research_refs", [])) or "none"))
    print(
        "Target Metrics: "
        + json.dumps(payload.get("target_metrics", {}), sort_keys=True)
    )
    print(
        "Hard Guardrails: "
        + json.dumps(payload.get("hard_guardrails", {}), sort_keys=True)
    )
    print(
        "Novelty Coordinates: "
        + json.dumps(payload.get("novelty_coordinates", {}), sort_keys=True)
    )
    print(
        f"Synthesis Eligible: {'yes' if payload.get('synthesis_eligible', True) else 'no'}"
    )
    print(
        f"Primary Layer Changed: {payload.get('primary_layer_changed') or 'none'}"
    )
    print(f"Layer Held Fixed: {payload.get('layer_held_fixed') or 'none'}")
    print(
        "Hidden Coupling Removed: "
        + (payload.get("hidden_coupling_removed") or "none")
    )
    print(
        "Why Not Coefficient Retune: "
        + (payload.get("why_not_coefficient_retune") or "none")
    )
    print(
        "Expected Win Condition: "
        + (payload.get("expected_win_condition") or "none")
    )
    print(
        "Expected Failure Signature: "
        + (payload.get("expected_failure_signature") or "none")
    )
    print(f"Quote Topology: {payload.get('quote_topology') or 'none'}")
    topology_branch = payload.get("is_topology_branch")
    print(
        "Topology Branch: "
        + (
            "yes"
            if topology_branch is True
            else "no"
            if topology_branch is False
            else "unknown"
        )
    )
    print(f"Expected Failure Mode: {payload.get('expected_failure_mode') or 'none'}")
    print(f"Actual Failure Mode: {payload.get('actual_failure_mode') or 'none'}")
    return 0


def hill_climb_summarize_run_command(args: argparse.Namespace) -> int:
    """Show an agent-facing summary for a run."""
    try:
        summary = HillClimbHarness(
            artifact_root=Path(args.artifact_root),
            n_workers=resolve_n_workers(),
        ).summarize_run(
            run_id=args.run_id,
            allow_protected_surface_drift=getattr(args, "read_only", False),
        )
    except (HillClimbHarnessError, RuntimeError, ValueError) as exc:
        print(f"Hill-climb summarize-run failed: {exc}")
        return 1

    if getattr(args, "json", False):
        _print_json(summary)
        return 0

    _print_warnings(summary.get("warnings", []))
    print(f"Run: {summary['run_id']}")
    print(f"Current Target Stage: {summary['current_target_stage']}")
    outcome_gate = summary.get("outcome_gate")
    if outcome_gate is None:
        print("Outcome Gate: none")
    else:
        print(f"Outcome Gate: {outcome_gate['message']}")
    print("Incumbent Chain:")
    for entry in summary["incumbent_chain"]:
        mean_edge = entry["mean_edge"]
        mean_edge_text = "n/a" if mean_edge is None else f"{mean_edge:.6f}"
        print(
            f"  {entry['eval_id']} {entry['stage']} {entry['status']} {mean_edge_text}"
        )
    print("Abandoned Families: " + (", ".join(summary["abandoned_families"]) or "none"))
    print(
        "Frontier Bank: "
        + ", ".join(entry["eval_id"] for entry in summary["frontier_bank"]["best_raw"])
    )
    print(
        "Decomposition Gaps: "
        + (", ".join(summary["decomposition_gaps"]) or "none")
    )
    batch_diversity = summary["batch_diversity"]
    print(
        "Batch Diversity: "
        f"{batch_diversity['distinct_primary_layer_count']} primary layers, "
        + (
            "topology branch present"
            if batch_diversity["has_topology_branch"]
            else "topology branch missing"
        )
    )
    print("Portfolio Gaps: " + (", ".join(summary["portfolio_gaps"]) or "none"))
    print("Structural Recommendations:")
    for entry in summary["structural_recommendations"]:
        covered = "covered" if entry["covered"] else "missing"
        print(f"  {entry['kind']} [{covered}] {entry['reason']}")
    print("Unresolved Hypotheses:")
    for payload in summary["unresolved_hypotheses"]:
        print(
            f"  {payload['hypothesis_id']} {payload['status']} {payload['mutation_family']}"
        )
    print("Recommended Next Batch:")
    for entry in summary["recommended_next_batch"]:
        covered = "covered" if entry["covered"] else "missing"
        print(f"  {entry['intent']} [{covered}] {entry['reason']}")
    print("Notable Failures:")
    for entry in summary["notable_failures"]:
        print(
            f"  {entry['eval_id']} {entry['status']} {entry.get('decision_summary') or ''}"
        )
    return 0


def hill_climb_analyze_run_command(args: argparse.Namespace) -> int:
    """Show structured phenotype and frontier analysis for a run."""
    try:
        payload = HillClimbHarness(
            artifact_root=Path(args.artifact_root),
            n_workers=resolve_n_workers(),
        ).analyze_run(
            run_id=args.run_id,
            allow_protected_surface_drift=getattr(args, "read_only", False),
        )
    except (HillClimbHarnessError, RuntimeError, ValueError) as exc:
        print(f"Hill-climb analyze-run failed: {exc}")
        return 1

    if getattr(args, "json", False):
        _print_json(payload)
        return 0

    _print_warnings(payload.get("warnings", []))
    print(f"Run: {payload['run_id']}")
    print("Failure Clusters:")
    for tag, count in sorted(payload["failure_clusters"].items()):
        print(f"  {tag}: {count}")
    print(
        "Decomposition Gaps: "
        + (", ".join(payload["decomposition_gaps"]) or "none")
    )
    print("Decomposition Coverage:")
    for layer, coverage in payload["decomposition_coverage"].items():
        open_ids = coverage["open_hypothesis_ids"]
        print(f"  {layer}: " + (", ".join(open_ids) or "none"))
    batch_diversity = payload["batch_diversity"]
    print(
        "Batch Diversity: "
        f"{batch_diversity['distinct_primary_layer_count']} primary layers, "
        + (
            "topology branch present"
            if batch_diversity["has_topology_branch"]
            else "topology branch missing"
        )
    )
    for issue in batch_diversity["issues"]:
        print(f"  Issue: {issue}")
    print("Portfolio Gaps: " + (", ".join(payload["portfolio_gaps"]) or "none"))
    print("Intent Coverage:")
    for intent, coverage in payload["intent_coverage"].items():
        open_ids = coverage["open_hypothesis_ids"]
        print(f"  {intent}: " + (", ".join(open_ids) or "none"))
    print("Structural Recommendations:")
    for entry in payload["structural_recommendations"]:
        covered = "covered" if entry["covered"] else "missing"
        print(f"  {entry['kind']} [{covered}] {entry['reason']}")
    print("Best Raw Frontier:")
    for entry in payload["frontier_bank"]["best_raw"]:
        print(f"  {entry['eval_id']} {entry['stage']} {entry['mean_edge']:.6f}")
    print("Recommended Next Batch:")
    for entry in payload["recommended_next_batch"]:
        covered = "covered" if entry["covered"] else "missing"
        print(f"  {entry['intent']} [{covered}] {entry['reason']}")
    return 0


def hill_climb_compare_profiles_command(args: argparse.Namespace) -> int:
    """Compare profile deltas between baseline, candidate, and optional anchor."""
    try:
        _profile_slot_input(
            label="baseline",
            eval_id=args.baseline_eval_id,
            source_path=args.baseline_source,
            required=True,
        )
        _profile_slot_input(
            label="candidate",
            eval_id=args.candidate_eval_id,
            source_path=args.candidate_source,
            required=True,
        )
        _profile_slot_input(
            label="anchor",
            eval_id=args.anchor_eval_id,
            source_path=args.anchor_source,
            required=False,
        )
        stored_eval_ids = [
            eval_id
            for eval_id in (
                args.baseline_eval_id,
                args.candidate_eval_id,
                args.anchor_eval_id,
            )
            if eval_id is not None
        ]
        if stored_eval_ids and not args.run_id:
            raise HillClimbHarnessError(
                "--run-id is required when comparing stored eval ids"
            )
        harness = HillClimbHarness(
            artifact_root=Path(args.artifact_root),
            n_workers=resolve_n_workers(),
        )
        warnings: list[str] = []
        if args.run_id:
            warnings = harness.get_read_warnings(
                run_id=args.run_id,
                allow_protected_surface_drift=getattr(args, "read_only", False),
            )
        baseline_summary = None
        candidate_summary = None
        anchor_summary = None
        if args.run_id and args.baseline_eval_id:
            baseline_summary = harness.get_evaluation(
                run_id=args.run_id,
                eval_id=args.baseline_eval_id,
                allow_protected_surface_drift=getattr(args, "read_only", False),
            )
        if args.run_id and args.candidate_eval_id:
            candidate_summary = harness.get_evaluation(
                run_id=args.run_id,
                eval_id=args.candidate_eval_id,
                allow_protected_surface_drift=getattr(args, "read_only", False),
            )
        if args.run_id and args.anchor_eval_id:
            anchor_summary = harness.get_evaluation(
                run_id=args.run_id,
                eval_id=args.anchor_eval_id,
                allow_protected_surface_drift=getattr(args, "read_only", False),
            )
        payload = harness.compare_profiles(
            stage=args.stage,
            baseline_summary=baseline_summary,
            candidate_summary=candidate_summary,
            baseline_source_path=args.baseline_source,
            candidate_source_path=args.candidate_source,
            anchor_summary=anchor_summary,
            anchor_source_path=args.anchor_source,
        )
    except (
        HillClimbHarnessError,
        RuntimeError,
        ValueError,
        json.JSONDecodeError,
    ) as exc:
        print(f"Hill-climb compare-profiles failed: {exc}")
        return 1

    if getattr(args, "json", False):
        _print_json({"warnings": warnings, **payload})
        return 0

    _print_warnings(warnings)
    print(f"Stage: {payload['stage']}")
    baseline_label = payload["baseline"].get("eval_id") or payload["baseline"].get(
        "source_path"
    )
    candidate_label = payload["candidate"].get("eval_id") or payload["candidate"].get(
        "source_path"
    )
    print(f"Baseline: {baseline_label}")
    print(f"Candidate: {candidate_label}")
    print("Candidate vs Baseline:")
    for key, value in sorted(payload["candidate_vs_baseline"].items()):
        if value is not None:
            print(f"  {key}: {value:.6f}")
    if "candidate_vs_anchor" in payload:
        anchor_label = payload["anchor"].get("eval_id") or payload["anchor"].get(
            "source_path"
        )
        print(f"Anchor: {anchor_label}")
        print("Candidate vs Anchor:")
        for key, value in sorted(payload["candidate_vs_anchor"].items()):
            if value is not None:
                print(f"  {key}: {value:.6f}")
    if "baseline_vs_anchor" in payload:
        print("Baseline vs Anchor:")
        for key, value in sorted(payload["baseline_vs_anchor"].items()):
            if value is not None:
                print(f"  {key}: {value:.6f}")
    return 0


def hill_climb_pull_best_command(args: argparse.Namespace) -> int:
    """Restore the incumbent snapshot into an editable strategy file."""
    try:
        destination = HillClimbHarness(
            artifact_root=Path(args.artifact_root),
            n_workers=resolve_n_workers(),
        ).pull_best(
            run_id=args.run_id,
            stage=args.stage,
            destination=Path(args.destination),
        )
    except (HillClimbHarnessError, RuntimeError, ValueError) as exc:
        print(f"Hill-climb restore failed: {exc}")
        return 1

    if getattr(args, "json", False):
        _print_json({"destination": str(destination)})
        return 0

    print(f"Restored: {destination}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="AMM Design Competition - Simulate and score your strategy",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  uv run amm-match run contracts/src/Strategy.sol
  uv run amm-match run contracts/src/Strategy.sol --simulations 100
  uv run amm-match validate contracts/src/Strategy.sol
  uv run amm-match hill-climb eval contracts/src/Strategy.sol --run-id mar26 --stage screen
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Run command
    run_parser = subparsers.add_parser(
        "run", help="Run simulations and get your strategy's Edge score"
    )
    run_parser.add_argument("strategy", help="Path to Solidity strategy file (.sol)")
    run_parser.add_argument(
        "--simulations",
        type=int,
        default=None,
        help="Number of simulations per match (defaults to shared baseline config)",
    )
    run_parser.add_argument(
        "--steps",
        type=int,
        default=None,
        help="Steps per simulation (defaults to shared baseline config)",
    )
    run_parser.add_argument(
        "--initial-price",
        type=float,
        default=None,
        help="Initial price (defaults to shared baseline config)",
    )
    run_parser.add_argument(
        "--initial-x",
        type=float,
        default=None,
        help="Initial X reserves (defaults to shared baseline config)",
    )
    run_parser.add_argument(
        "--initial-y",
        type=float,
        default=None,
        help="Initial Y reserves (defaults to shared baseline config)",
    )
    run_parser.add_argument(
        "--volatility",
        type=float,
        default=None,
        help="Annualized volatility (defaults to shared baseline config)",
    )
    run_parser.add_argument(
        "--retail-rate",
        type=float,
        default=None,
        help="Retail arrival rate per step (defaults to shared baseline config)",
    )
    run_parser.add_argument(
        "--retail-size",
        type=float,
        default=None,
        help="Mean retail trade size in Y (defaults to shared baseline config)",
    )
    run_parser.add_argument(
        "--retail-size-sigma",
        type=float,
        default=None,
        help="Lognormal sigma for retail sizes (defaults to shared baseline config)",
    )
    run_parser.set_defaults(func=run_match_command)

    # Validate command
    validate_parser = subparsers.add_parser(
        "validate", help="Validate a Solidity strategy without running"
    )
    validate_parser.add_argument(
        "strategy", help="Path to Solidity strategy file (.sol)"
    )
    validate_parser.set_defaults(func=validate_command)

    hill_climb_parser = subparsers.add_parser(
        "hill-climb",
        help="Run the mean-edge hill-climbing harness",
    )
    hill_climb_subparsers = hill_climb_parser.add_subparsers(
        dest="hill_climb_command",
        help="Hill-climb commands",
    )

    hill_climb_eval_parser = hill_climb_subparsers.add_parser(
        "eval",
        help="Evaluate a strategy source and record keep/discard status",
    )
    hill_climb_eval_parser.add_argument(
        "strategy", help="Path to the active Solidity strategy"
    )
    hill_climb_eval_parser.add_argument(
        "--run-id", required=True, help="Stable run identifier"
    )
    hill_climb_eval_parser.add_argument(
        "--stage",
        choices=list(HILL_CLIMB_STAGES.keys()),
        default="screen",
        help="Hill-climb stage preset",
    )
    hill_climb_eval_parser.add_argument(
        "--artifact-root",
        default="artifacts/hill_climb",
        help="Artifact root for hill-climb run outputs",
    )
    hill_climb_eval_parser.add_argument(
        "--label",
        default=None,
        help="Short label for the evaluation snapshot",
    )
    hill_climb_eval_parser.add_argument(
        "--description",
        default=None,
        help="Longer experiment note recorded with the evaluation",
    )
    hill_climb_eval_parser.add_argument(
        "--hypothesis-id",
        default=None,
        help="Registered hypothesis linked to this evaluation",
    )
    hill_climb_eval_parser.add_argument(
        "--parent-eval-id",
        default=None,
        help="Explicit parent evaluation for lineage tracking",
    )
    hill_climb_eval_parser.add_argument(
        "--change-summary",
        default=None,
        help="Short description of what changed relative to the parent",
    )
    hill_climb_eval_parser.add_argument(
        "--research-refs",
        action="append",
        default=[],
        help="Repeatable research or plan reference linked to this evaluation",
    )
    hill_climb_eval_parser.add_argument(
        "--replay-reason",
        default=None,
        help="Required when intentionally replaying the same stage/source snapshot",
    )
    _add_json_argument(hill_climb_eval_parser)
    hill_climb_eval_parser.set_defaults(func=hill_climb_eval_command)

    hill_climb_status_parser = hill_climb_subparsers.add_parser(
        "status",
        help="Show the incumbent and latest result for a run stage",
    )
    hill_climb_status_parser.add_argument(
        "--run-id", required=True, help="Stable run identifier"
    )
    hill_climb_status_parser.add_argument(
        "--stage",
        choices=list(HILL_CLIMB_STAGES.keys()),
        default="screen",
        help="Hill-climb stage preset",
    )
    hill_climb_status_parser.add_argument(
        "--artifact-root",
        default="artifacts/hill_climb",
        help="Artifact root for hill-climb run outputs",
    )
    hill_climb_status_parser.add_argument(
        "--read-only",
        action="store_true",
        help="Allow read-only inspection even if the protected surface fingerprint drifted",
    )
    _add_json_argument(hill_climb_status_parser)
    hill_climb_status_parser.set_defaults(func=hill_climb_status_command)

    hill_climb_set_state_parser = hill_climb_subparsers.add_parser(
        "set-state",
        help="Update loop-control metadata for an existing run",
    )
    hill_climb_set_state_parser.add_argument(
        "--run-id", required=True, help="Stable run identifier"
    )
    hill_climb_set_state_parser.add_argument(
        "--artifact-root",
        default="artifacts/hill_climb",
        help="Artifact root for hill-climb run outputs",
    )
    hill_climb_set_state_parser.add_argument(
        "--current-target-stage",
        choices=list(HILL_CLIMB_STAGES.keys()),
        default=None,
        help="Declared target stage for the active search plan",
    )
    hill_climb_set_state_parser.add_argument(
        "--next-hypothesis-id",
        default=None,
        help="Registered hypothesis id queued for the next move",
    )
    hill_climb_set_state_parser.add_argument(
        "--next-hypothesis-note",
        default=None,
        help="Optional short note for the queued hypothesis",
    )
    hill_climb_set_state_parser.add_argument(
        "--clear-next-hypothesis",
        action="store_true",
        help="Clear any recorded next hypothesis",
    )
    hill_climb_set_state_parser.add_argument(
        "--run-mode",
        choices=["foreground", "background"],
        default=None,
        help="Operator execution mode for this loop",
    )
    hill_climb_set_state_parser.add_argument(
        "--refine-after",
        type=int,
        default=None,
        help="Non-improving target-stage streak that should trigger refinement",
    )
    hill_climb_set_state_parser.add_argument(
        "--pivot-after",
        type=int,
        default=None,
        help="Non-improving target-stage streak that should trigger a pivot",
    )
    hill_climb_set_state_parser.add_argument(
        "--stop-after",
        type=int,
        default=None,
        help="Non-improving target-stage streak that should stop the current line",
    )
    hill_climb_set_state_parser.add_argument(
        "--breakout-stage",
        choices=list(HILL_CLIMB_STAGES.keys()),
        default=None,
        help="Stage whose incumbent must clear the breakout threshold",
    )
    hill_climb_set_state_parser.add_argument(
        "--breakout-threshold",
        type=float,
        default=None,
        help="Required mean_edge threshold for the declared breakout stage",
    )
    hill_climb_set_state_parser.add_argument(
        "--clear-breakout-goal",
        action="store_true",
        help="Clear any recorded breakout outcome gate",
    )
    _add_json_argument(hill_climb_set_state_parser)
    hill_climb_set_state_parser.set_defaults(func=hill_climb_set_state_command)

    hill_climb_set_hypothesis_parser = hill_climb_subparsers.add_parser(
        "set-hypothesis",
        help="Create or update a first-class hypothesis record for a run",
    )
    hill_climb_set_hypothesis_parser.add_argument(
        "--run-id", required=True, help="Stable run identifier"
    )
    hill_climb_set_hypothesis_parser.add_argument(
        "--artifact-root",
        default="artifacts/hill_climb",
        help="Artifact root for hill-climb run outputs",
    )
    hill_climb_set_hypothesis_parser.add_argument(
        "--hypothesis-id", required=True, help="Stable hypothesis identifier"
    )
    hill_climb_set_hypothesis_parser.add_argument("--title", default=None)
    hill_climb_set_hypothesis_parser.add_argument("--rationale", default=None)
    hill_climb_set_hypothesis_parser.add_argument(
        "--expected-effect",
        default=None,
        help="Expected user-visible or score-visible effect",
    )
    hill_climb_set_hypothesis_parser.add_argument(
        "--mutation-family",
        default=None,
        help="Design family or mutation bucket for clustering history",
    )
    hill_climb_set_hypothesis_parser.add_argument(
        "--batch-id",
        default=None,
        help="Explicit batch identifier used for batch-scoped diversity checks",
    )
    hill_climb_set_hypothesis_parser.add_argument(
        "--status",
        choices=[
            "planned",
            "queued",
            "active",
            "promoted",
            "invalidated",
            "abandoned",
            "completed",
        ],
        default=None,
    )
    hill_climb_set_hypothesis_parser.add_argument(
        "--parent-hypothesis-id",
        default=None,
        help="Optional parent hypothesis for lineage tracking",
    )
    hill_climb_set_hypothesis_parser.add_argument(
        "--seed-eval-id",
        default=None,
        help="Optional seed evaluation already linked to this hypothesis",
    )
    hill_climb_set_hypothesis_parser.add_argument(
        "--research-refs",
        action="append",
        default=[],
        help="Repeatable research or plan reference linked to this hypothesis",
    )
    hill_climb_set_hypothesis_parser.add_argument(
        "--target-metrics",
        action="append",
        default=[],
        help="Repeatable key=value target metric for this experiment object",
    )
    hill_climb_set_hypothesis_parser.add_argument(
        "--hard-guardrails",
        action="append",
        default=[],
        help="Repeatable key=value hard guardrail for this experiment object",
    )
    hill_climb_set_hypothesis_parser.add_argument(
        "--expected-failure-mode",
        default=None,
        help="Expected machine-readable failure signature for this experiment",
    )
    hill_climb_set_hypothesis_parser.add_argument(
        "--actual-failure-mode",
        default=None,
        help="Optional explicit actual failure mode override",
    )
    hill_climb_set_hypothesis_parser.add_argument(
        "--novelty-coordinates",
        default=None,
        help="JSON object describing novelty axes for batch planning",
    )
    hill_climb_set_hypothesis_parser.add_argument(
        "--synthesis-eligible",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Whether this hypothesis remains eligible for synthesis",
    )
    hill_climb_set_hypothesis_parser.add_argument(
        "--nearest-prior-failures",
        action="append",
        default=[],
        help="Repeatable nearest prior failure hypothesis id",
    )
    hill_climb_set_hypothesis_parser.add_argument(
        "--nearest-prior-successes",
        action="append",
        default=[],
        help="Repeatable nearest prior success hypothesis id",
    )
    hill_climb_set_hypothesis_parser.add_argument(
        "--primary-layer-changed",
        choices=["state", "risk_budget", "opportunity_budget", "quote_map"],
        default=None,
        help="Primary decomposition layer changed by this hypothesis",
    )
    hill_climb_set_hypothesis_parser.add_argument(
        "--layer-held-fixed",
        choices=["state", "risk_budget", "opportunity_budget", "quote_map"],
        default=None,
        help="Layer intentionally held fixed while testing this branch",
    )
    hill_climb_set_hypothesis_parser.add_argument(
        "--hidden-coupling-removed",
        default=None,
        help="Single hidden coupling this hypothesis is trying to break",
    )
    hill_climb_set_hypothesis_parser.add_argument(
        "--why-not-coefficient-retune",
        default=None,
        help="Why this branch is structurally different from a coefficient retune",
    )
    hill_climb_set_hypothesis_parser.add_argument(
        "--expected-win-condition",
        default=None,
        help="Expected user-visible or score-visible win condition",
    )
    hill_climb_set_hypothesis_parser.add_argument(
        "--expected-failure-signature",
        default=None,
        help="Expected textual failure signature for this branch",
    )
    hill_climb_set_hypothesis_parser.add_argument(
        "--quote-topology",
        default=None,
        help="Short label for the quote-assembly topology this branch belongs to",
    )
    hill_climb_set_hypothesis_parser.add_argument(
        "--topology-branch",
        dest="is_topology_branch",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Whether this branch changes how the quote is assembled",
    )
    _add_json_argument(hill_climb_set_hypothesis_parser)
    hill_climb_set_hypothesis_parser.set_defaults(
        func=hill_climb_set_hypothesis_command
    )

    hill_climb_history_parser = hill_climb_subparsers.add_parser(
        "history",
        help="Show the compact derived history for a run",
    )
    hill_climb_history_parser.add_argument(
        "--run-id", required=True, help="Stable run identifier"
    )
    hill_climb_history_parser.add_argument(
        "--artifact-root",
        default="artifacts/hill_climb",
        help="Artifact root for hill-climb run outputs",
    )
    hill_climb_history_parser.add_argument(
        "--read-only",
        action="store_true",
        help="Allow read-only inspection even if the protected surface fingerprint drifted",
    )
    _add_json_argument(hill_climb_history_parser)
    hill_climb_history_parser.set_defaults(func=hill_climb_history_command)

    hill_climb_show_eval_parser = hill_climb_subparsers.add_parser(
        "show-eval",
        help="Show one evaluation record with lineage metadata",
    )
    hill_climb_show_eval_parser.add_argument(
        "--run-id", required=True, help="Stable run identifier"
    )
    hill_climb_show_eval_parser.add_argument(
        "--eval-id", required=True, help="Evaluation identifier"
    )
    hill_climb_show_eval_parser.add_argument(
        "--artifact-root",
        default="artifacts/hill_climb",
        help="Artifact root for hill-climb run outputs",
    )
    hill_climb_show_eval_parser.add_argument(
        "--read-only",
        action="store_true",
        help="Allow read-only inspection even if the protected surface fingerprint drifted",
    )
    _add_json_argument(hill_climb_show_eval_parser)
    hill_climb_show_eval_parser.set_defaults(func=hill_climb_show_eval_command)

    hill_climb_show_hypothesis_parser = hill_climb_subparsers.add_parser(
        "show-hypothesis",
        help="Show one hypothesis record and its linked evaluations",
    )
    hill_climb_show_hypothesis_parser.add_argument(
        "--run-id", required=True, help="Stable run identifier"
    )
    hill_climb_show_hypothesis_parser.add_argument(
        "--hypothesis-id", required=True, help="Hypothesis identifier"
    )
    hill_climb_show_hypothesis_parser.add_argument(
        "--artifact-root",
        default="artifacts/hill_climb",
        help="Artifact root for hill-climb run outputs",
    )
    hill_climb_show_hypothesis_parser.add_argument(
        "--read-only",
        action="store_true",
        help="Allow read-only inspection even if the protected surface fingerprint drifted",
    )
    _add_json_argument(hill_climb_show_hypothesis_parser)
    hill_climb_show_hypothesis_parser.set_defaults(
        func=hill_climb_show_hypothesis_command
    )

    hill_climb_summarize_run_parser = hill_climb_subparsers.add_parser(
        "summarize-run",
        help="Show an agent-facing summary of the run state and history",
    )
    hill_climb_summarize_run_parser.add_argument(
        "--run-id", required=True, help="Stable run identifier"
    )
    hill_climb_summarize_run_parser.add_argument(
        "--artifact-root",
        default="artifacts/hill_climb",
        help="Artifact root for hill-climb run outputs",
    )
    hill_climb_summarize_run_parser.add_argument(
        "--read-only",
        action="store_true",
        help="Allow read-only inspection even if the protected surface fingerprint drifted",
    )
    _add_json_argument(hill_climb_summarize_run_parser)
    hill_climb_summarize_run_parser.set_defaults(func=hill_climb_summarize_run_command)

    hill_climb_analyze_run_parser = hill_climb_subparsers.add_parser(
        "analyze-run",
        help="Show structured phenotype clusters and frontier-bank analysis",
    )
    hill_climb_analyze_run_parser.add_argument(
        "--run-id", required=True, help="Stable run identifier"
    )
    hill_climb_analyze_run_parser.add_argument(
        "--artifact-root",
        default="artifacts/hill_climb",
        help="Artifact root for hill-climb run outputs",
    )
    hill_climb_analyze_run_parser.add_argument(
        "--read-only",
        action="store_true",
        help="Allow read-only inspection even if the protected surface fingerprint drifted",
    )
    _add_json_argument(hill_climb_analyze_run_parser)
    hill_climb_analyze_run_parser.set_defaults(func=hill_climb_analyze_run_command)

    hill_climb_compare_profiles_parser = hill_climb_subparsers.add_parser(
        "compare-profiles",
        help="Compare incumbent/candidate/anchor phenotype profiles on one stage",
    )
    hill_climb_compare_profiles_parser.add_argument(
        "--run-id",
        default=None,
        help="Optional run id when referencing stored eval ids",
    )
    hill_climb_compare_profiles_parser.add_argument(
        "--stage",
        choices=list(HILL_CLIMB_STAGES.keys()),
        required=True,
        help="Hill-climb stage preset",
    )
    hill_climb_compare_profiles_parser.add_argument(
        "--artifact-root",
        default="artifacts/hill_climb",
        help="Artifact root for hill-climb run outputs",
    )
    hill_climb_compare_profiles_parser.add_argument("--baseline-eval-id", default=None)
    hill_climb_compare_profiles_parser.add_argument("--candidate-eval-id", default=None)
    hill_climb_compare_profiles_parser.add_argument("--anchor-eval-id", default=None)
    hill_climb_compare_profiles_parser.add_argument("--baseline-source", default=None)
    hill_climb_compare_profiles_parser.add_argument("--candidate-source", default=None)
    hill_climb_compare_profiles_parser.add_argument("--anchor-source", default=None)
    hill_climb_compare_profiles_parser.add_argument(
        "--read-only",
        action="store_true",
        help="Allow read-only inspection even if the protected surface fingerprint drifted",
    )
    _add_json_argument(hill_climb_compare_profiles_parser)
    hill_climb_compare_profiles_parser.set_defaults(
        func=hill_climb_compare_profiles_command
    )

    hill_climb_pull_parser = hill_climb_subparsers.add_parser(
        "pull-best",
        help="Restore the incumbent strategy snapshot into a destination file",
    )
    hill_climb_pull_parser.add_argument(
        "--run-id", required=True, help="Stable run identifier"
    )
    hill_climb_pull_parser.add_argument(
        "--stage",
        choices=list(HILL_CLIMB_STAGES.keys()),
        default="screen",
        help="Hill-climb stage preset",
    )
    hill_climb_pull_parser.add_argument(
        "--artifact-root",
        default="artifacts/hill_climb",
        help="Artifact root for hill-climb run outputs",
    )
    hill_climb_pull_parser.add_argument(
        "--destination",
        default=str(DEFAULT_ACTIVE_STRATEGY_PATH),
        help="Destination Solidity file to overwrite with the incumbent snapshot",
    )
    _add_json_argument(hill_climb_pull_parser)
    hill_climb_pull_parser.set_defaults(func=hill_climb_pull_best_command)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 1
    if args.command == "hill-climb" and args.hill_climb_command is None:
        hill_climb_parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
