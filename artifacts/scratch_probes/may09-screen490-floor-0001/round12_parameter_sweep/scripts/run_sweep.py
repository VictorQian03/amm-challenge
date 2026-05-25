"""Generate and run the Round 12 screen-capped parameter sweep."""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
import json
import os
from pathlib import Path
import subprocess
from typing import Any, Iterable, cast


REPO_ROOT = Path(__file__).resolve().parents[5]
ROUND_ROOT = (
    REPO_ROOT
    / "artifacts/scratch_probes/may09-screen490-floor-0001/round12_parameter_sweep"
)
SOURCE_ROOT = ROUND_ROOT / "sources"
RESULT_ROOT = ROUND_ROOT / "results"
SUMMARY_ROOT = ROUND_ROOT / "summaries"
CURRENT_BASE = REPO_ROOT / "contracts/src/StarterStrategy.sol"
PREDECESSOR_BASE = (
    REPO_ROOT / "artifacts/hill_climb/may09-screen490-floor-0001/snapshots/"
    "5b991499242d9fe200416a7c3f7c541c97fd9d65eb3502b0c87eab7588a31f83.sol"
)


@dataclass(frozen=True)
class Variant:
    name: str
    family: str
    base: Path
    replacements: tuple[tuple[str, str], ...]
    rationale: str


def _replace_once(source: str, old: str, new: str, *, variant: str) -> str:
    count = source.count(old)
    if count != 1:
        raise ValueError(
            f"{variant}: expected one occurrence of {old!r}, found {count}"
        )
    return source.replace(old, new, 1)


def _current(
    name: str,
    family: str,
    old: str,
    new: str,
    rationale: str,
) -> Variant:
    return Variant(name, family, CURRENT_BASE, ((old, new),), rationale)


def _paired(
    name: str,
    family: str,
    changes: Iterable[tuple[str, str]],
    rationale: str,
    *,
    base: Path = CURRENT_BASE,
) -> Variant:
    return Variant(name, family, base, tuple(changes), rationale)


def variants() -> list[Variant]:
    output = [
        Variant(
            "base_flow_dir_280",
            "control",
            CURRENT_BASE,
            (),
            "Current retained screen_0005 baseline.",
        ),
        Variant(
            "base_trade_tox_6500",
            "control",
            PREDECESSOR_BASE,
            (),
            "Closest retained predecessor control.",
        ),
    ]
    protection_lines = (
        "        uint256 bidProtection = wmul(bidRiskSignal, 5400 * BPS);\n"
        "        uint256 askProtection = wmul(askRiskSignal, 5400 * BPS);"
    )
    opportunity_lines = (
        "            bidProtection + wmul(baselineFlex, 1200 * BPS)\n"
        "        );\n"
        "        askOpportunityCut = clamp(\n"
        "            askOpportunityCut,\n"
        "            0,\n"
        "            askProtection + wmul(baselineFlex, 1200 * BPS)"
    )
    refill_lines = (
        "        uint256 refillAuctionCut =\n"
        "            wmul(refillAuctionBudget, gap >= 4 ? 420 * BPS : 260 * BPS) +\n"
        "            wmul(wmul(refillAuctionBudget, passiveRecaptureMemory), 220 * BPS);"
    )
    flow_risk_line = (
        "                flowDirectionalRisk = wmul(toxicFlowSignal, 280 * BPS);"
    )
    for reserve in (2500, 5000, 7500, 10000):
        output.append(
            _paired(
                f"flow_reserve_{reserve}",
                "protected_flow_reserve",
                (
                    (
                        protection_lines,
                        protection_lines
                        + "\n"
                        + f"        uint256 bidFlowReserve = wmul(wmul(bidFlowRisk, 5400 * BPS), {reserve} * BPS);\n"
                        + f"        uint256 askFlowReserve = wmul(wmul(askFlowRisk, 5400 * BPS), {reserve} * BPS);",
                    ),
                    (
                        opportunity_lines,
                        "            (bidProtection > bidFlowReserve ? bidProtection - bidFlowReserve : 0) + wmul(baselineFlex, 1200 * BPS)\n"
                        "        );\n"
                        "        askOpportunityCut = clamp(\n"
                        "            askOpportunityCut,\n"
                        "            0,\n"
                        "            (askProtection > askFlowReserve ? askProtection - askFlowReserve : 0) + wmul(baselineFlex, 1200 * BPS)",
                    ),
                ),
                "Reserve part of newly added aligned-flow protection from same-quote opportunity spend-back.",
            )
        )
    for scale in (0, 2500, 5000, 7500):
        output.append(
            _paired(
                f"flow_offset_scale_{scale}",
                "flow_optional_offset_gate",
                (
                    (
                        refill_lines,
                        refill_lines
                        + "\n"
                        + "        if ((toxicBidSide && askFlowRisk > 0) || (!toxicBidSide && bidFlowRisk > 0)) {\n"
                        + f"            healingRebate = wmul(healingRebate, {scale} * BPS);\n"
                        + f"            refillAuctionCut = wmul(refillAuctionCut, {scale} * BPS);\n"
                        + "        }",
                    ),
                ),
                "Scale only optional healing/refill offsets while an aligned flow-risk charge is active.",
            )
        )
    for surcharge in (20, 40, 60, 80):
        output.append(
            _paired(
                f"extension_tail_surcharge_{surcharge}",
                "extension_tail_risk",
                (
                    (
                        flow_risk_line,
                        flow_risk_line
                        + "\n"
                        + "                if (extensionSignal > 6 * BPS) {\n"
                        + f"                    flowDirectionalRisk += wmul(extensionSignal - 6 * BPS, {surcharge} * BPS);\n"
                        + "                }",
                    ),
                ),
                "Restore protection only beyond an extreme extension tail while leaving the winning base regime fixed.",
            )
        )
    for surcharge in (20, 40, 60, 80):
        output.append(
            _paired(
                f"tail_reserve_surcharge_{surcharge}",
                "tail_protected_reserve",
                (
                    (
                        flow_risk_line,
                        flow_risk_line
                        + "\n"
                        + "                if (extensionSignal > 6 * BPS) {\n"
                        + f"                    flowDirectionalRisk += wmul(extensionSignal - 6 * BPS, {surcharge} * BPS);\n"
                        + "                }",
                    ),
                    (
                        protection_lines,
                        protection_lines
                        + "\n"
                        + f"        uint256 bidFlowReserve = wmul(wmul(bidFlowRisk, 5400 * BPS), {surcharge * 100} * BPS);\n"
                        + f"        uint256 askFlowReserve = wmul(wmul(askFlowRisk, 5400 * BPS), {surcharge * 100} * BPS);",
                    ),
                    (
                        opportunity_lines,
                        "            (bidProtection > bidFlowReserve ? bidProtection - bidFlowReserve : 0) + wmul(baselineFlex, 1200 * BPS)\n"
                        "        );\n"
                        "        askOpportunityCut = clamp(\n"
                        "            askOpportunityCut,\n"
                        "            0,\n"
                        "            (askProtection > askFlowReserve ? askProtection - askFlowReserve : 0) + wmul(baselineFlex, 1200 * BPS)",
                    ),
                ),
                "Reserve only a bounded tail-conditioned flow-protection supplement from optional cut spending.",
            )
        )
    return output


def write_sources(selected: list[Variant]) -> None:
    SOURCE_ROOT.mkdir(parents=True, exist_ok=True)
    metadata = []
    for variant in selected:
        source = variant.base.read_text()
        original_name_line = next(
            line for line in source.splitlines() if 'return "' in line
        )
        source = _replace_once(
            source,
            original_name_line,
            f'        return "R12{variant.name[:42]}";',
            variant=variant.name,
        )
        for old, new in variant.replacements:
            source = _replace_once(source, old, new, variant=variant.name)
        path = SOURCE_ROOT / f"{variant.name}.sol"
        path.write_text(source)
        metadata.append(
            {
                "name": variant.name,
                "family": variant.family,
                "base": variant.base.relative_to(REPO_ROOT).as_posix(),
                "path": path.relative_to(REPO_ROOT).as_posix(),
                "rationale": variant.rationale,
            }
        )
    SUMMARY_ROOT.mkdir(parents=True, exist_ok=True)
    (SUMMARY_ROOT / "variants.json").write_text(json.dumps(metadata, indent=2) + "\n")


def load_payload(path: Path) -> dict[str, Any]:
    payload: object = json.loads(path.read_text())
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return cast(dict[str, Any], payload)


def metric_row(
    name: str, family: str, stage: str, payload: dict[str, Any]
) -> dict[str, object]:
    analysis = cast(dict[str, Any], payload["derived_analysis"])
    profile = cast(dict[str, Any], analysis["profile"])
    return {
        "name": name,
        "family": family,
        "stage": stage,
        "mean_edge": payload["mean_edge"],
        "arb_loss_to_retail_gain": profile["arb_loss_to_retail_gain"],
        "quote_selectivity_ratio": profile["quote_selectivity_ratio"],
        "time_weighted_mean_fee": profile["time_weighted_mean_fee"],
        "low_decile_mean_edge": profile["low_decile_mean_edge"],
        "low_retail_mean_edge": profile["low_retail_mean_edge"],
        "low_volatility_mean_edge": profile["low_volatility_mean_edge"],
    }


def run_stage(stage: str, selected: list[Variant]) -> None:
    stage_root = RESULT_ROOT / stage
    stage_root.mkdir(parents=True, exist_ok=True)
    rows = []
    env = os.environ.copy()
    env["UV_CACHE_DIR"] = ".uv-cache"
    for index, variant in enumerate(selected, start=1):
        path = SOURCE_ROOT / f"{variant.name}.sol"
        print(f"[{index}/{len(selected)}] {stage}: {variant.name}", flush=True)
        command = [
            "uv",
            "run",
            "amm-match",
            "hill-climb",
            "probe",
            "--stage",
            stage,
            "--json",
            path.as_posix(),
        ]
        result = subprocess.run(
            command, cwd=REPO_ROOT, env=env, text=True, capture_output=True
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"{stage} failed for {variant.name}: {result.stdout}\n{result.stderr}"
            )
        output_path = stage_root / f"{variant.name}.json"
        output_path.write_text(result.stdout)
        rows.append(
            metric_row(variant.name, variant.family, stage, load_payload(output_path))
        )
    rows.sort(key=lambda row: float(row["mean_edge"]), reverse=True)
    SUMMARY_ROOT.mkdir(parents=True, exist_ok=True)
    with (SUMMARY_ROOT / f"{stage}_summary.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (SUMMARY_ROOT / f"{stage}_summary.json").write_text(
        json.dumps(rows, indent=2) + "\n"
    )


def select_variants(names: list[str] | None) -> list[Variant]:
    candidates = {variant.name: variant for variant in variants()}
    if not names:
        return list(candidates.values())
    missing = sorted(set(names) - candidates.keys())
    if missing:
        raise ValueError(f"Unknown variant names: {', '.join(missing)}")
    return [candidates[name] for name in names]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("generate", "smoke", "screen"))
    parser.add_argument("--names", nargs="*")
    args = parser.parse_args()
    selected = select_variants(args.names)
    write_sources(selected)
    if args.action in {"smoke", "screen"}:
        run_stage(args.action, selected)


if __name__ == "__main__":
    main()
