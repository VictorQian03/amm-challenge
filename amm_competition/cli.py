"""Command-line interface for simulations and the thin hill-climb harness."""

import argparse
from dataclasses import asdict, is_dataclass
import json
import sys
from pathlib import Path
from typing import Any, cast

import amm_sim_rs

from amm_competition.competition.config import (
    BASELINE_SETTINGS,
    BASELINE_VARIANCE,
    baseline_nominal_retail_rate,
    baseline_nominal_retail_size,
    baseline_nominal_sigma,
    resolve_n_workers,
)
from amm_competition.competition.match import HyperparameterVariance, MatchRunner
from amm_competition.evm.adapter import EVMStrategyAdapter
from amm_competition.evm.baseline import load_vanilla_strategy
from amm_competition.evm.compiler import SolidityCompiler
from amm_competition.evm.validator import SolidityValidator
from amm_competition.hill_climb.harness import (
    DEFAULT_ARTIFACT_ROOT,
    DEFAULT_STRATEGY_PATH,
    HillClimbHarness,
    HillClimbHarnessError,
)
from amm_competition.hill_climb.stages import HILL_CLIMB_STAGES


def _compiled_bytecode_or_raise(compilation: Any, *, context: str) -> bytes:
    if compilation.bytecode is None:
        raise RuntimeError(f"{context} succeeded without deployment bytecode")
    return compilation.bytecode


def _json_default(value: object) -> object:
    if isinstance(value, Path):
        return str(value)
    if is_dataclass(value) and not isinstance(value, type):
        return asdict(cast(Any, value))
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def _print_json(payload: object) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True, default=_json_default))


def _add_json_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit a machine-readable JSON payload instead of human text",
    )


def _add_read_only_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--read-only",
        action="store_true",
        help="Allow read surfaces to inspect runs pinned to an older protected evaluator fingerprint",
    )


def _format_metric(value: Any) -> str:
    if isinstance(value, bool):
        return "n/a"
    if isinstance(value, (int, float)):
        return f"{float(value):.6f}"
    return "n/a"


def _print_profile(name: str, payload: dict[str, Any]) -> None:
    print(f"{name}:")
    if "eval_id" in payload and payload.get("eval_id") is not None:
        print(f"  Eval ID: {payload['eval_id']}")
    if "source_path" in payload and payload.get("source_path") is not None:
        print(f"  Source: {payload['source_path']}")
    print(f"  Mean Edge: {_format_metric(payload.get('mean_edge'))}")
    profile = payload.get("profile", {})
    for metric in (
        "retail_edge",
        "arb_edge",
        "arb_loss_to_retail_gain",
        "quote_selectivity_ratio",
        "time_weighted_mean_fee",
        "max_fee_jump",
        "low_decile_mean_edge",
        "low_retail_mean_edge",
    ):
        print(f"  {metric}: {_format_metric(profile.get(metric))}")


def _print_delta_block(name: str, payload: dict[str, Any]) -> None:
    print(f"{name}:")
    for metric in (
        "mean_edge",
        "retail_edge",
        "arb_edge",
        "arb_loss_to_retail_gain",
        "quote_selectivity_ratio",
        "time_weighted_mean_fee",
        "max_fee_jump",
        "low_decile_mean_edge",
        "low_retail_mean_edge",
    ):
        print(f"  {metric}: {_format_metric(payload.get(metric))}")


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
        for error in (compilation.errors or []):
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
        args.initial_price if args.initial_price is not None else BASELINE_SETTINGS.initial_price
    )
    initial_x = args.initial_x if args.initial_x is not None else BASELINE_SETTINGS.initial_x
    initial_y = args.initial_y if args.initial_y is not None else BASELINE_SETTINGS.initial_y
    gbm_sigma = args.volatility if args.volatility is not None else baseline_nominal_sigma()
    retail_rate = (
        args.retail_rate if args.retail_rate is not None else baseline_nominal_retail_rate()
    )
    retail_size = (
        args.retail_size if args.retail_size is not None else baseline_nominal_retail_size()
    )
    retail_size_sigma = (
        args.retail_size_sigma
        if args.retail_size_sigma is not None
        else BASELINE_SETTINGS.retail_size_sigma
    )

    config = amm_sim_rs.SimulationConfig(
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
        args.simulations if args.simulations is not None else BASELINE_SETTINGS.n_simulations
    )
    print(f"\nRunning {n_simulations} simulations...")
    variance = HyperparameterVariance(
        retail_mean_size_min=retail_size if args.retail_size is not None else BASELINE_VARIANCE.retail_mean_size_min,
        retail_mean_size_max=retail_size if args.retail_size is not None else BASELINE_VARIANCE.retail_mean_size_max,
        vary_retail_mean_size=False if args.retail_size is not None else BASELINE_VARIANCE.vary_retail_mean_size,
        retail_arrival_rate_min=retail_rate if args.retail_rate is not None else BASELINE_VARIANCE.retail_arrival_rate_min,
        retail_arrival_rate_max=retail_rate if args.retail_rate is not None else BASELINE_VARIANCE.retail_arrival_rate_max,
        vary_retail_arrival_rate=False if args.retail_rate is not None else BASELINE_VARIANCE.vary_retail_arrival_rate,
        gbm_sigma_min=gbm_sigma if args.volatility is not None else BASELINE_VARIANCE.gbm_sigma_min,
        gbm_sigma_max=gbm_sigma if args.volatility is not None else BASELINE_VARIANCE.gbm_sigma_max,
        vary_gbm_sigma=False if args.volatility is not None else BASELINE_VARIANCE.vary_gbm_sigma,
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
        for error in (compilation.errors or []):
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
    """Evaluate a candidate inside the thin hill-climb harness."""
    try:
        harness = HillClimbHarness(artifact_root=args.artifact_root)
        summary = harness.evaluate(
            run_id=args.run_id,
            stage=args.stage,
            source_path=args.strategy,
            label=args.label,
            description=args.description,
            replay_reason=args.replay_reason,
        )
        if args.json:
            _print_json(summary)
            return 0

        print(f"Run ID: {summary['run_id']}")
        print(f"Eval ID: {summary['eval_id']}")
        print(f"Stage: {summary['stage']}")
        print(f"Status: {summary['status']}")
        if summary.get("strategy_name") is not None:
            print(f"Strategy: {summary['strategy_name']}")
        print(f"Mean Edge: {_format_metric(summary.get('mean_edge'))}")
        gate = summary.get("gate", {})
        print(f"Gate Passed: {bool(gate.get('passed'))}")
        failures = gate.get("failures", [])
        if failures:
            print("Gate Failures:")
            for failure in failures:
                print(f"  - {failure}")
        selection = summary.get("selection", {})
        print(f"Selection: {selection.get('rationale')}")
        return 0
    except (HillClimbHarnessError, RuntimeError) as exc:
        print(exc)
        return 1


def hill_climb_probe_command(args: argparse.Namespace) -> int:
    """Evaluate a candidate without persisting retained artifacts."""
    try:
        payload = HillClimbHarness().probe_source(
            stage=args.stage,
            source_path=args.strategy,
        )
        if args.json:
            _print_json(payload)
            return 0

        print("Mode: probe")
        print(f"Stage: {payload['stage']}")
        if payload.get("strategy_name") is not None:
            print(f"Strategy: {payload['strategy_name']}")
        print(f"Mean Edge: {_format_metric(payload.get('mean_edge'))}")
        gate = payload.get("gate", {})
        print(f"Gate Passed: {bool(gate.get('passed'))}")
        failures = gate.get("failures", [])
        if failures:
            print("Gate Failures:")
            for failure in failures:
                print(f"  - {failure}")
        selection = payload.get("selection", {})
        print(f"Selection: {selection.get('rationale')}")
        return 0
    except (HillClimbHarnessError, RuntimeError) as exc:
        print(exc)
        return 1


def hill_climb_runs_command(args: argparse.Namespace) -> int:
    """List retained hill-climb runs."""
    try:
        payload = HillClimbHarness(artifact_root=args.artifact_root).list_runs(
            allow_protected_surface_drift=args.read_only
        )
        if args.json:
            _print_json(payload)
            return 0

        print("Runs:")
        for entry in payload["runs"]:
            latest = entry.get("latest_eval_id") or "none"
            latest_status = entry.get("latest_status") or "n/a"
            print(
                f"  {entry['run_id']} [{entry['status']}] "
                f"latest={latest} latest_status={latest_status}"
            )
            for note in entry.get("notes", []):
                print(f"    note: {note}")
        return 0
    except (HillClimbHarnessError, RuntimeError) as exc:
        print(exc)
        return 1


def hill_climb_status_command(args: argparse.Namespace) -> int:
    """Show stage incumbents, best raw results, and latest evals for a run."""
    try:
        payload = HillClimbHarness(artifact_root=args.artifact_root).get_run_status(
            run_id=args.run_id,
            stage=args.stage,
            allow_protected_surface_drift=args.read_only,
        )
        if args.json:
            _print_json(payload)
            return 0

        print(f"Run ID: {payload['run_id']}")
        print(f"Created At: {payload['created_at']}")
        print(f"Updated At: {payload['updated_at']}")
        print(f"Evals: {payload['eval_count']}")
        print(f"Snapshots: {payload['snapshot_count']}")
        for warning in payload.get("warnings", []):
            print(f"Warning: {warning}")
        latest = payload.get("latest")
        if latest is not None:
            print(
                f"Latest: {latest['eval_id']} {latest['stage']} {latest['status']} "
                f"{_format_metric(latest.get('mean_edge'))}"
            )
        for stage_name, stage_payload in payload["stages"].items():
            print(f"{stage_name}:")
            incumbent = stage_payload.get("incumbent")
            best_raw = stage_payload.get("best_raw")
            current = stage_payload.get("latest")
            if incumbent is None:
                print("  Incumbent: none")
            else:
                print(
                    f"  Incumbent: {incumbent['eval_id']} {incumbent['status']} "
                    f"{_format_metric(incumbent.get('mean_edge'))}"
                )
            if best_raw is None:
                print("  Best Raw: none")
            else:
                print(
                    f"  Best Raw: {best_raw['eval_id']} {best_raw['status']} "
                    f"{_format_metric(best_raw.get('mean_edge'))}"
                )
            if current is None:
                print("  Latest: none")
            else:
                print(
                    f"  Latest: {current['eval_id']} {current['status']} "
                    f"{_format_metric(current.get('mean_edge'))}"
                )
        return 0
    except HillClimbHarnessError as exc:
        print(exc)
        return 1


def hill_climb_history_command(args: argparse.Namespace) -> int:
    """Show the compact append-only eval ledger for a run."""
    try:
        history = HillClimbHarness(artifact_root=args.artifact_root).get_history(
            run_id=args.run_id,
            allow_protected_surface_drift=args.read_only,
        )
        if args.json:
            _print_json(history)
            return 0

        print("eval_id\tstage\tstatus\tmean_edge\tdelta_vs_incumbent\tlabel\tprimary_failure_tag")
        for row in history:
            print(
                f"{row['eval_id']}\t{row['stage']}\t{row['status']}\t"
                f"{_format_metric(row.get('mean_edge'))}\t"
                f"{_format_metric(row.get('delta_vs_incumbent'))}\t"
                f"{row.get('label') or ''}\t{row.get('primary_failure_tag') or ''}"
            )
        return 0
    except HillClimbHarnessError as exc:
        print(exc)
        return 1


def hill_climb_show_eval_command(args: argparse.Namespace) -> int:
    """Show one stored eval with scorecard and derived profile data."""
    try:
        summary = HillClimbHarness(artifact_root=args.artifact_root).get_evaluation(
            run_id=args.run_id,
            eval_id=args.eval_id,
            allow_protected_surface_drift=args.read_only,
        )
        if args.json:
            _print_json(summary)
            return 0

        print(f"Eval ID: {summary['eval_id']}")
        print(f"Run ID: {summary['run_id']}")
        print(f"Stage: {summary['stage']}")
        print(f"Status: {summary['status']}")
        print(f"Source: {summary['source_path']}")
        print(f"Snapshot: {summary['snapshot_relpath']}")
        if summary.get("label"):
            print(f"Label: {summary['label']}")
        if summary.get("description"):
            print(f"Description: {summary['description']}")
        print(f"Mean Edge: {_format_metric(summary.get('mean_edge'))}")
        if summary.get("strategy_name"):
            print(f"Strategy: {summary['strategy_name']}")
        selection = summary.get("selection", {})
        print(f"Selection: {selection.get('rationale')}")
        derived = summary.get("derived_analysis", {})
        failure = derived.get("failure_signature", {})
        if failure.get("primary_tag"):
            print(f"Primary Failure Tag: {failure['primary_tag']}")
        profile = derived.get("profile", {})
        for metric in (
            "retail_edge",
            "arb_edge",
            "arb_loss_to_retail_gain",
            "quote_selectivity_ratio",
            "time_weighted_mean_fee",
            "max_fee_jump",
        ):
            print(f"{metric}: {_format_metric(profile.get(metric))}")
        return 0
    except HillClimbHarnessError as exc:
        print(exc)
        return 1


def hill_climb_pull_best_command(args: argparse.Namespace) -> int:
    """Restore the current stage incumbent to a working file."""
    try:
        destination = HillClimbHarness(artifact_root=args.artifact_root).pull_best(
            run_id=args.run_id,
            stage=args.stage,
            destination=args.destination,
            allow_protected_surface_drift=args.read_only,
        )
        payload = {"destination": destination}
        if args.json:
            _print_json(payload)
            return 0
        print(f"Restored incumbent to {destination}")
        return 0
    except HillClimbHarnessError as exc:
        print(exc)
        return 1


def hill_climb_compare_profiles_command(args: argparse.Namespace) -> int:
    """Compare stage-aligned profiles from stored evals or ad hoc source files."""
    try:
        baseline_eval_id, baseline_source = _profile_slot_input(
            label="baseline",
            eval_id=args.baseline_eval_id,
            source_path=args.baseline_source,
            required=True,
        )
        candidate_eval_id, candidate_source = _profile_slot_input(
            label="candidate",
            eval_id=args.candidate_eval_id,
            source_path=args.candidate_source,
            required=True,
        )
        anchor_eval_id, anchor_source = _profile_slot_input(
            label="anchor",
            eval_id=args.anchor_eval_id,
            source_path=args.anchor_source,
            required=False,
        )
        if any(value is not None for value in (baseline_eval_id, candidate_eval_id, anchor_eval_id)):
            if args.run_id is None:
                raise HillClimbHarnessError(
                    "--run-id is required when any stored eval id is used"
                )

        harness = HillClimbHarness(artifact_root=args.artifact_root)

        def load_summary(eval_id: str | None) -> dict[str, Any] | None:
            if eval_id is None:
                return None
            return harness.get_evaluation(
                run_id=args.run_id,
                eval_id=eval_id,
                allow_protected_surface_drift=args.read_only,
            )

        payload = harness.compare_profiles(
            stage=args.stage,
            baseline_summary=load_summary(baseline_eval_id),
            candidate_summary=load_summary(candidate_eval_id),
            anchor_summary=load_summary(anchor_eval_id),
            baseline_source_path=baseline_source,
            candidate_source_path=candidate_source,
            anchor_source_path=anchor_source,
        )
        if args.json:
            _print_json(payload)
            return 0

        print(f"Stage: {payload['stage']}")
        _print_profile("Baseline", payload["baseline"])
        _print_profile("Candidate", payload["candidate"])
        _print_delta_block("Candidate vs Baseline", payload["candidate_vs_baseline"])
        if "anchor" in payload:
            _print_profile("Anchor", payload["anchor"])
            _print_delta_block("Candidate vs Anchor", payload["candidate_vs_anchor"])
        return 0
    except HillClimbHarnessError as exc:
        print(exc)
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="AMM Design Competition - Simulate, score, and retain hill-climb evals",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  amm-match run my_strategy.sol
  amm-match run my_strategy.sol --simulations 1000 --steps 1000
  amm-match validate my_strategy.sol
  amm-match hill-climb eval --run-id apr21 --stage screen
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Run command
    run_parser = subparsers.add_parser("run", help="Run simulations and get your strategy's Edge score")
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
    validate_parser.add_argument("strategy", help="Path to Solidity strategy file (.sol)")
    validate_parser.set_defaults(func=validate_command)

    hill_climb_parser = subparsers.add_parser(
        "hill-climb",
        help="Use the thin append-only hill-climb harness",
    )
    hill_climb_subparsers = hill_climb_parser.add_subparsers(
        dest="hill_climb_command",
        help="Hill-climb commands",
    )

    hill_climb_eval_parser = hill_climb_subparsers.add_parser(
        "eval",
        help="Evaluate a strategy and append it to a retained run",
    )
    hill_climb_eval_parser.add_argument(
        "strategy",
        nargs="?",
        default=str(DEFAULT_STRATEGY_PATH),
        help=(
            "Path to Solidity strategy file (.sol); defaults to "
            "contracts/src/StarterStrategy.sol for fresh-run seeding"
        ),
    )
    hill_climb_eval_parser.add_argument("--run-id", required=True)
    hill_climb_eval_parser.add_argument(
        "--stage",
        required=True,
        choices=sorted(HILL_CLIMB_STAGES),
    )
    hill_climb_eval_parser.add_argument(
        "--artifact-root",
        default=str(DEFAULT_ARTIFACT_ROOT),
        help="Artifact root for hill-climb run outputs",
    )
    hill_climb_eval_parser.add_argument("--label", default=None)
    hill_climb_eval_parser.add_argument("--description", default=None)
    hill_climb_eval_parser.add_argument(
        "--replay-reason",
        default=None,
        help="Intentional replay reason when evaluating an identical source at the same stage",
    )
    _add_json_argument(hill_climb_eval_parser)
    hill_climb_eval_parser.set_defaults(func=hill_climb_eval_command)

    hill_climb_probe_parser = hill_climb_subparsers.add_parser(
        "probe",
        help="Evaluate a strategy without writing retained run artifacts",
    )
    hill_climb_probe_parser.add_argument(
        "strategy",
        nargs="?",
        default=str(DEFAULT_STRATEGY_PATH),
        help=(
            "Path to Solidity strategy file (.sol); defaults to "
            "contracts/src/StarterStrategy.sol"
        ),
    )
    hill_climb_probe_parser.add_argument(
        "--stage",
        required=True,
        choices=sorted(HILL_CLIMB_STAGES),
    )
    _add_json_argument(hill_climb_probe_parser)
    hill_climb_probe_parser.set_defaults(func=hill_climb_probe_command)

    hill_climb_runs_parser = hill_climb_subparsers.add_parser(
        "runs",
        help="List retained hill-climb runs",
    )
    hill_climb_runs_parser.add_argument(
        "--artifact-root",
        default=str(DEFAULT_ARTIFACT_ROOT),
        help="Artifact root for hill-climb run outputs",
    )
    _add_read_only_argument(hill_climb_runs_parser)
    _add_json_argument(hill_climb_runs_parser)
    hill_climb_runs_parser.set_defaults(func=hill_climb_runs_command)

    hill_climb_status_parser = hill_climb_subparsers.add_parser(
        "status",
        help="Show incumbents, best raw results, and latest evals for a run",
    )
    hill_climb_status_parser.add_argument("--run-id", required=True)
    hill_climb_status_parser.add_argument(
        "--stage",
        choices=sorted(HILL_CLIMB_STAGES),
        default=None,
    )
    hill_climb_status_parser.add_argument(
        "--artifact-root",
        default=str(DEFAULT_ARTIFACT_ROOT),
        help="Artifact root for hill-climb run outputs",
    )
    _add_read_only_argument(hill_climb_status_parser)
    _add_json_argument(hill_climb_status_parser)
    hill_climb_status_parser.set_defaults(func=hill_climb_status_command)

    hill_climb_history_parser = hill_climb_subparsers.add_parser(
        "history",
        help="Show the compact eval ledger for a run",
    )
    hill_climb_history_parser.add_argument("--run-id", required=True)
    hill_climb_history_parser.add_argument(
        "--artifact-root",
        default=str(DEFAULT_ARTIFACT_ROOT),
        help="Artifact root for hill-climb run outputs",
    )
    _add_read_only_argument(hill_climb_history_parser)
    _add_json_argument(hill_climb_history_parser)
    hill_climb_history_parser.set_defaults(func=hill_climb_history_command)

    hill_climb_show_eval_parser = hill_climb_subparsers.add_parser(
        "show-eval",
        help="Show one stored evaluation by id",
    )
    hill_climb_show_eval_parser.add_argument("--run-id", required=True)
    hill_climb_show_eval_parser.add_argument("--eval-id", required=True)
    hill_climb_show_eval_parser.add_argument(
        "--artifact-root",
        default=str(DEFAULT_ARTIFACT_ROOT),
        help="Artifact root for hill-climb run outputs",
    )
    _add_read_only_argument(hill_climb_show_eval_parser)
    _add_json_argument(hill_climb_show_eval_parser)
    hill_climb_show_eval_parser.set_defaults(func=hill_climb_show_eval_command)

    hill_climb_pull_parser = hill_climb_subparsers.add_parser(
        "pull-best",
        help="Restore the current stage incumbent to a destination file",
    )
    hill_climb_pull_parser.add_argument("--run-id", required=True)
    hill_climb_pull_parser.add_argument(
        "--stage",
        required=True,
        choices=sorted(HILL_CLIMB_STAGES),
    )
    hill_climb_pull_parser.add_argument(
        "--destination",
        required=True,
        help="Where to copy the stage incumbent source snapshot",
    )
    hill_climb_pull_parser.add_argument(
        "--artifact-root",
        default=str(DEFAULT_ARTIFACT_ROOT),
        help="Artifact root for hill-climb run outputs",
    )
    _add_read_only_argument(hill_climb_pull_parser)
    _add_json_argument(hill_climb_pull_parser)
    hill_climb_pull_parser.set_defaults(func=hill_climb_pull_best_command)

    hill_climb_compare_profiles_parser = hill_climb_subparsers.add_parser(
        "compare-profiles",
        help="Compare stage-aligned profiles from stored evals or source files",
    )
    hill_climb_compare_profiles_parser.add_argument(
        "--stage",
        required=True,
        choices=sorted(HILL_CLIMB_STAGES),
    )
    hill_climb_compare_profiles_parser.add_argument("--run-id", default=None)
    hill_climb_compare_profiles_parser.add_argument(
        "--artifact-root",
        default=str(DEFAULT_ARTIFACT_ROOT),
        help="Artifact root for hill-climb run outputs",
    )
    hill_climb_compare_profiles_parser.add_argument("--baseline-eval-id", default=None)
    hill_climb_compare_profiles_parser.add_argument("--candidate-eval-id", default=None)
    hill_climb_compare_profiles_parser.add_argument("--anchor-eval-id", default=None)
    hill_climb_compare_profiles_parser.add_argument("--baseline-source", default=None)
    hill_climb_compare_profiles_parser.add_argument("--candidate-source", default=None)
    hill_climb_compare_profiles_parser.add_argument("--anchor-source", default=None)
    _add_read_only_argument(hill_climb_compare_profiles_parser)
    _add_json_argument(hill_climb_compare_profiles_parser)
    hill_climb_compare_profiles_parser.set_defaults(
        func=hill_climb_compare_profiles_command
    )

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
