"""Generate and evaluate Round 13 variants against the screen_0005 raw baseline."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
import json
import os
from pathlib import Path
import subprocess
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[5]
ROUND_ROOT = (
    REPO_ROOT
    / "artifacts/scratch_probes/may09-screen490-floor-0001/round13_direct_screen_search"
)
SOURCE_ROOT = ROUND_ROOT / "sources"
RESULT_ROOT = ROUND_ROOT / "results"
SUMMARY_ROOT = ROUND_ROOT / "summaries"
BASE_SOURCE = (
    REPO_ROOT / "artifacts/hill_climb/may09-screen490-floor-0001/snapshots/"
    "8734ce7ce521f9b8e61e3ed1bda07c15ee29bf71a6dc771bc7fe66bbf876468a.sol"
)
BASELINE_SCREEN = 490.75833078204124
TARGET_SCREEN = BASELINE_SCREEN + 1.0


@dataclass(frozen=True)
class Candidate:
    name: str
    family: str
    values: dict[str, int]


SPECS: dict[str, tuple[str, str]] = {
    "alpha_flow": (
        "uint256 internal constant ALPHA_FLOW = 18 * BPS;",
        "uint256 internal constant ALPHA_FLOW = {value} * BPS;",
    ),
    "alpha_passive": (
        "uint256 internal constant ALPHA_PASSIVE = 18 * BPS;",
        "uint256 internal constant ALPHA_PASSIVE = {value} * BPS;",
    ),
    "flow_threshold": (
        "if (flowPressure > 500 * BPS) {",
        "if (flowPressure > {value} * BPS) {{",
    ),
    "extension_threshold": (
        "if (extensionSignal > 3 * BPS) {",
        "if (extensionSignal > {value} * BPS) {{",
    ),
    "extension_weight": (
        "flowPressure + wmul(extensionSignal, 2200 * BPS);",
        "flowPressure + wmul(extensionSignal, {value} * BPS);",
    ),
    "flow_risk": (
        "flowDirectionalRisk = wmul(toxicFlowSignal, 280 * BPS);",
        "flowDirectionalRisk = wmul(toxicFlowSignal, {value} * BPS);",
    ),
    "shared_vol": ("wmul(volMemory, 1800 * BPS) +", "wmul(volMemory, {value} * BPS) +"),
    "shared_hazard": (
        "wmul(hazardMemory, 1900 * BPS);",
        "wmul(hazardMemory, {value} * BPS);",
    ),
    "event_carry": (
        "uint256 eventCarry = wmul(eventSignal, 220 * BPS);",
        "uint256 eventCarry = wmul(eventSignal, {value} * BPS);",
    ),
    "burst_fee": (
        "directionalBurstFee = wmul(burstSignal, 1850 * BPS);",
        "directionalBurstFee = wmul(burstSignal, {value} * BPS);",
    ),
    "risk_protection": (
        "uint256 bidProtection = wmul(bidRiskSignal, 5400 * BPS);\n        uint256 askProtection = wmul(askRiskSignal, 5400 * BPS);",
        "uint256 bidProtection = wmul(bidRiskSignal, {value} * BPS);\n        uint256 askProtection = wmul(askRiskSignal, {value} * BPS);",
    ),
    "one_sided": (
        "uint256 oneSidedProtection = wmul(oneSidedFlow, 2800 * BPS);",
        "uint256 oneSidedProtection = wmul(oneSidedFlow, {value} * BPS);",
    ),
    "trade_boost": (
        "uint256 tradeBoost = wmul(clamp(tradeSize, 0, WAD / 5), 6500 * BPS);",
        "uint256 tradeBoost = wmul(clamp(tradeSize, 0, WAD / 5), {value} * BPS);",
    ),
    "opportunity_cut": (
        "uint256 bidOpportunityCut = wmul(bidOpportunitySignal, 8200 * BPS);\n        uint256 askOpportunityCut = wmul(askOpportunitySignal, 8200 * BPS);",
        "uint256 bidOpportunityCut = wmul(bidOpportunitySignal, {value} * BPS);\n        uint256 askOpportunityCut = wmul(askOpportunitySignal, {value} * BPS);",
    ),
    "passive_cut": (
        "uint256 passiveRecaptureCut = wmul(passiveRecaptureMemory, 1550 * BPS);",
        "uint256 passiveRecaptureCut = wmul(passiveRecaptureMemory, {value} * BPS);",
    ),
    "center_offset": (
        "            700 * BPS\n        );\n        uint256 centerCap",
        "            {value} * BPS\n        );\n        uint256 centerCap",
    ),
    "center_cap": (
        "            1400 * BPS\n        );\n        if (inventoryCenteringOffset",
        "            {value} * BPS\n        );\n        if (inventoryCenteringOffset",
    ),
    "flex_cut": (
        "bidProtection + wmul(baselineFlex, 1200 * BPS)\n        );\n        askOpportunityCut = clamp(\n            askOpportunityCut,\n            0,\n            askProtection + wmul(baselineFlex, 1200 * BPS)",
        "bidProtection + wmul(baselineFlex, {value} * BPS)\n        );\n        askOpportunityCut = clamp(\n            askOpportunityCut,\n            0,\n            askProtection + wmul(baselineFlex, {value} * BPS)",
    ),
    "refill_long": (
        "gap >= 4 ? 420 * BPS : 260 * BPS",
        "gap >= 4 ? {value} * BPS : 260 * BPS",
    ),
    "refill_short": (
        "gap >= 4 ? 420 * BPS : 260 * BPS",
        "gap >= 4 ? 420 * BPS : {value} * BPS",
    ),
}


def variants() -> list[Candidate]:
    output = [Candidate("base_flow_dir_280", "control", {})]
    singles = {
        "alpha_flow": (12, 14, 16, 20, 22, 24),
        "alpha_passive": (12, 14, 16, 20, 22, 24),
        "flow_threshold": (300, 350, 400, 450, 550, 600, 700),
        "extension_threshold": (1, 2, 4, 5, 6),
        "extension_weight": (1200, 1600, 1900, 2500, 2800, 3200),
        "flow_risk": (180, 220, 240, 260, 300, 320, 360),
        "shared_vol": (1500, 1650, 1950, 2100),
        "shared_hazard": (1600, 1750, 2050, 2200),
        "event_carry": (160, 190, 250, 280),
        "burst_fee": (1500, 1650, 2050, 2200),
        "risk_protection": (4800, 5000, 5200, 5600, 5800, 6000),
        "one_sided": (2200, 2500, 3100, 3400),
        "trade_boost": (5600, 6000, 7000, 7400),
        "opportunity_cut": (7000, 7600, 7900, 8500, 8800, 9200),
        "passive_cut": (1200, 1350, 1450, 1650, 1750, 1900),
        "center_offset": (450, 550, 850, 1000),
        "center_cap": (1000, 1200, 1600, 1800),
        "flex_cut": (800, 1000, 1400, 1600),
    }
    for key, values in singles.items():
        for value in values:
            output.append(Candidate(f"{key}_{value}", f"single_{key}", {key: value}))
    combos = [
        (
            "flow_fast_light",
            {"alpha_flow": 22, "flow_threshold": 400, "flow_risk": 240},
        ),
        (
            "flow_fast_strong",
            {"alpha_flow": 22, "flow_threshold": 400, "flow_risk": 320},
        ),
        (
            "flow_slow_light",
            {"alpha_flow": 14, "flow_threshold": 600, "flow_risk": 240},
        ),
        (
            "flow_ext_early_light",
            {"extension_threshold": 2, "extension_weight": 1600, "flow_risk": 240},
        ),
        (
            "flow_ext_early_strong",
            {"extension_threshold": 2, "extension_weight": 2500, "flow_risk": 300},
        ),
        (
            "flow_ext_late_strong",
            {"extension_threshold": 5, "extension_weight": 2800, "flow_risk": 320},
        ),
        (
            "protect_open",
            {"risk_protection": 5200, "opportunity_cut": 8500, "passive_cut": 1650},
        ),
        (
            "protect_tight",
            {"risk_protection": 5600, "opportunity_cut": 7900, "passive_cut": 1450},
        ),
        (
            "spread_open",
            {"shared_vol": 1650, "shared_hazard": 1750, "event_carry": 190},
        ),
        (
            "spread_tight",
            {"shared_vol": 1950, "shared_hazard": 2050, "event_carry": 250},
        ),
        (
            "burst_trade_open",
            {"burst_fee": 1650, "trade_boost": 6000, "opportunity_cut": 8500},
        ),
        (
            "burst_trade_tight",
            {"burst_fee": 2050, "trade_boost": 7000, "opportunity_cut": 7900},
        ),
        (
            "recapture_more",
            {
                "alpha_passive": 22,
                "passive_cut": 1750,
                "center_offset": 850,
                "center_cap": 1600,
            },
        ),
        (
            "recapture_less",
            {
                "alpha_passive": 14,
                "passive_cut": 1350,
                "center_offset": 550,
                "center_cap": 1200,
            },
        ),
        (
            "flow_open_combo",
            {
                "alpha_flow": 20,
                "flow_risk": 240,
                "risk_protection": 5200,
                "opportunity_cut": 8500,
            },
        ),
        (
            "flow_tight_combo",
            {
                "alpha_flow": 20,
                "flow_risk": 320,
                "risk_protection": 5600,
                "opportunity_cut": 7900,
            },
        ),
        (
            "stack_flow220_recapture",
            {
                "flow_risk": 220,
                "alpha_passive": 22,
                "passive_cut": 1750,
                "center_offset": 850,
                "center_cap": 1600,
            },
        ),
        (
            "stack_flow200_recapture",
            {
                "flow_risk": 200,
                "alpha_passive": 22,
                "passive_cut": 1750,
                "center_offset": 850,
                "center_cap": 1600,
            },
        ),
        (
            "stack_flow180_recapture",
            {
                "flow_risk": 180,
                "alpha_passive": 22,
                "passive_cut": 1750,
                "center_offset": 850,
                "center_cap": 1600,
            },
        ),
        ("stack_event160_flow220", {"event_carry": 160, "flow_risk": 220}),
        ("stack_event140_flow220", {"event_carry": 140, "flow_risk": 220}),
        ("stack_event180_flow220", {"event_carry": 180, "flow_risk": 220}),
        (
            "stack_event160_recapture",
            {
                "event_carry": 160,
                "alpha_passive": 22,
                "passive_cut": 1750,
                "center_offset": 850,
                "center_cap": 1600,
            },
        ),
        (
            "stack_event140_recapture",
            {
                "event_carry": 140,
                "alpha_passive": 22,
                "passive_cut": 1750,
                "center_offset": 850,
                "center_cap": 1600,
            },
        ),
        (
            "stack_event180_recapture",
            {
                "event_carry": 180,
                "alpha_passive": 22,
                "passive_cut": 1750,
                "center_offset": 850,
                "center_cap": 1600,
            },
        ),
        (
            "stack_event160_flow220_recapture",
            {
                "event_carry": 160,
                "flow_risk": 220,
                "alpha_passive": 22,
                "passive_cut": 1750,
                "center_offset": 850,
                "center_cap": 1600,
            },
        ),
        (
            "stack_event140_flow220_recapture",
            {
                "event_carry": 140,
                "flow_risk": 220,
                "alpha_passive": 22,
                "passive_cut": 1750,
                "center_offset": 850,
                "center_cap": 1600,
            },
        ),
        (
            "stack_event180_flow220_recapture",
            {
                "event_carry": 180,
                "flow_risk": 220,
                "alpha_passive": 22,
                "passive_cut": 1750,
                "center_offset": 850,
                "center_cap": 1600,
            },
        ),
        (
            "stack_event160_flow200_recapture",
            {
                "event_carry": 160,
                "flow_risk": 200,
                "alpha_passive": 22,
                "passive_cut": 1750,
                "center_offset": 850,
                "center_cap": 1600,
            },
        ),
        (
            "stack_event160_flow220_recap_soft",
            {
                "event_carry": 160,
                "flow_risk": 220,
                "alpha_passive": 22,
                "passive_cut": 1700,
                "center_offset": 800,
                "center_cap": 1500,
            },
        ),
        (
            "stack_event160_flow220_recap_strong",
            {
                "event_carry": 160,
                "flow_risk": 220,
                "alpha_passive": 24,
                "passive_cut": 1750,
                "center_offset": 900,
                "center_cap": 1700,
            },
        ),
        (
            "stack_event160_flow220_open",
            {
                "event_carry": 160,
                "flow_risk": 220,
                "alpha_passive": 22,
                "passive_cut": 1750,
                "center_offset": 850,
                "center_cap": 1600,
                "risk_protection": 5200,
                "opportunity_cut": 8500,
            },
        ),
    ]
    for name, values in combos:
        output.append(Candidate(name, "interaction", values))
    return output


def apply_values(source: str, candidate: Candidate) -> str:
    original_name = '        return "FlowDirectionalRisk280";'
    if source.count(original_name) != 1:
        raise ValueError("Baseline strategy name not found exactly once")
    source = source.replace(
        original_name, f'        return "R13{candidate.name[:38]}";', 1
    )
    for key, value in candidate.values.items():
        old, template = SPECS[key]
        if source.count(old) != 1:
            raise ValueError(
                f"{candidate.name}: {key} expected once, found {source.count(old)}"
            )
        source = source.replace(old, template.format(value=value), 1)
    return source


def generate(selected: list[Candidate]) -> None:
    SOURCE_ROOT.mkdir(parents=True, exist_ok=True)
    SUMMARY_ROOT.mkdir(parents=True, exist_ok=True)
    base = BASE_SOURCE.read_text()
    rows = []
    for candidate in selected:
        path = SOURCE_ROOT / f"{candidate.name}.sol"
        path.write_text(apply_values(base, candidate))
        rows.append(
            {
                "name": candidate.name,
                "family": candidate.family,
                "values": candidate.values,
                "source": str(path.relative_to(REPO_ROOT)),
            }
        )
    (SUMMARY_ROOT / "variants.json").write_text(json.dumps(rows, indent=2) + "\n")


def result_row(
    candidate: Candidate, stage: str, payload: dict[str, Any]
) -> dict[str, Any]:
    profile = payload["derived_analysis"]["profile"]
    return {
        "name": candidate.name,
        "family": candidate.family,
        "values": candidate.values,
        "stage": stage,
        "mean_edge": payload["mean_edge"],
        "delta_vs_best_raw": payload["mean_edge"] - BASELINE_SCREEN,
        "meets_target": payload["mean_edge"] >= TARGET_SCREEN,
        "arb_loss_to_retail_gain": profile["arb_loss_to_retail_gain"],
        "quote_selectivity_ratio": profile["quote_selectivity_ratio"],
        "time_weighted_mean_fee": profile["time_weighted_mean_fee"],
        "low_decile_mean_edge": profile["low_decile_mean_edge"],
        "low_retail_mean_edge": profile["low_retail_mean_edge"],
        "low_volatility_mean_edge": profile["low_volatility_mean_edge"],
    }


def run_one(stage: str, candidate: Candidate) -> dict[str, Any]:
    output_path = RESULT_ROOT / stage / f"{candidate.name}.json"
    if output_path.exists():
        return result_row(candidate, stage, json.loads(output_path.read_text()))
    env = os.environ.copy()
    env["UV_CACHE_DIR"] = ".uv-cache"
    command = [
        "uv",
        "run",
        "amm-match",
        "hill-climb",
        "probe",
        "--stage",
        stage,
        "--json",
        str(SOURCE_ROOT / f"{candidate.name}.sol"),
    ]
    result = subprocess.run(
        command, cwd=REPO_ROOT, env=env, text=True, capture_output=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"{candidate.name}: {result.stdout}\n{result.stderr}")
    output_path.write_text(result.stdout)
    return result_row(candidate, stage, json.loads(result.stdout))


def run_stage(
    stage: str, selected: list[Candidate], workers: int, tag: str | None
) -> None:
    (RESULT_ROOT / stage).mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(run_one, stage, candidate): candidate
            for candidate in selected
        }
        for index, future in enumerate(as_completed(futures), start=1):
            row = future.result()
            rows.append(row)
            print(
                f"[{index}/{len(selected)}] {stage}: {row['name']} = {row['mean_edge']:.9f} ({row['delta_vs_best_raw']:+.9f})",
                flush=True,
            )
    rows.sort(key=lambda row: row["mean_edge"], reverse=True)
    SUMMARY_ROOT.mkdir(parents=True, exist_ok=True)
    suffix = f"_{tag}" if tag else ""
    (SUMMARY_ROOT / f"{stage}{suffix}_summary.json").write_text(
        json.dumps(rows, indent=2) + "\n"
    )
    print(json.dumps(rows[:10], indent=2))


def choose(
    names: list[str] | None, from_stage: str | None, top: int | None
) -> list[Candidate]:
    all_candidates = {candidate.name: candidate for candidate in variants()}
    if from_stage:
        rows = json.loads((SUMMARY_ROOT / f"{from_stage}_summary.json").read_text())
        selected_names = [row["name"] for row in rows[: top or len(rows)]]
    elif names:
        selected_names = names
    else:
        return list(all_candidates.values())
    missing = sorted(set(selected_names) - all_candidates.keys())
    if missing:
        raise ValueError(f"Unknown candidates: {missing}")
    return [all_candidates[name] for name in selected_names]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("generate", "smoke", "screen"))
    parser.add_argument("--names", nargs="*")
    parser.add_argument("--from-stage", choices=("smoke", "screen"))
    parser.add_argument("--top", type=int)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--tag")
    args = parser.parse_args()
    selected = choose(args.names, args.from_stage, args.top)
    if args.action == "generate":
        generate(selected)
        print(f"generated {len(selected)} candidates under {SOURCE_ROOT}")
        return
    missing = [
        candidate
        for candidate in selected
        if not (SOURCE_ROOT / f"{candidate.name}.sol").exists()
    ]
    if missing:
        generate(selected)
    run_stage(args.action, selected, args.workers, args.tag)


if __name__ == "__main__":
    main()
