"""Command-line interface for running AMM simulations and hill climbing."""

import argparse
import sys
from pathlib import Path

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
        )
        state = (
            harness.get_run_state(run_id=args.run_id)
            if hasattr(harness, "get_run_state")
            else None
        )
    except (HillClimbHarnessError, RuntimeError, ValueError) as exc:
        print(f"Hill-climb evaluation failed: {exc}")
        return 1

    print(f"Run: {summary['run_id']}")
    print(f"Eval: {summary['eval_id']}")
    print(f"Stage: {summary['stage']}")
    print(f"Status: {summary['status']}")
    print(f"Mean Edge: {summary['mean_edge']:.6f}")
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
        status = harness.get_stage_status(
            run_id=args.run_id,
            stage=args.stage,
        )
        state = harness.get_run_state(run_id=args.run_id)
    except (HillClimbHarnessError, RuntimeError, ValueError) as exc:
        print(f"Hill-climb status failed: {exc}")
        return 1

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
    print(f"Next Hypothesis: {state.next_hypothesis or 'none'}")
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
    if args.next_hypothesis is not None and args.clear_next_hypothesis:
        print(
            "Hill-climb state update failed: choose either --next-hypothesis or --clear-next-hypothesis"
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
        next_hypothesis = args.next_hypothesis
        if args.clear_next_hypothesis:
            next_hypothesis = None
        stop_rules = None
        if any(
            value is not None
            for value in (args.refine_after, args.pivot_after, args.stop_after)
        ):
            existing = harness.get_run_state(run_id=args.run_id).stop_rules
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
            next_hypothesis=next_hypothesis,
            next_hypothesis_set=args.next_hypothesis is not None
            or args.clear_next_hypothesis,
            run_mode=args.run_mode,
            stop_rules=stop_rules,
            outcome_gate=outcome_gate,
            outcome_gate_set=args.breakout_stage is not None
            or args.clear_breakout_goal,
        )
    except (HillClimbHarnessError, RuntimeError, ValueError) as exc:
        print(f"Hill-climb state update failed: {exc}")
        return 1

    print(f"Run: {state.run_id}")
    print(f"Current Target Stage: {state.current_target_stage}")
    print(f"Run Mode: {state.run_mode}")
    print(f"Next Hypothesis: {state.next_hypothesis or 'none'}")
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

    print(f"Restored: {destination}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="AMM Design Competition - Simulate and score your strategy",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  amm-match run contracts/src/Strategy.sol
  amm-match run contracts/src/Strategy.sol --simulations 100
  amm-match validate contracts/src/Strategy.sol
  amm-match hill-climb eval contracts/src/Strategy.sol --run-id mar26 --stage screen
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
        "--next-hypothesis",
        default=None,
        help="Short note describing the next hypothesis to test",
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
    hill_climb_set_state_parser.set_defaults(func=hill_climb_set_state_command)

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
