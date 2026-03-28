"""Utility to load the default 30bps strategy used as the normalizer AMM."""

from pathlib import Path
from typing import Optional, Tuple

from amm_competition.evm.adapter import EVMStrategyAdapter
from amm_competition.evm.compiler import SolidityCompiler

_CACHED_CONTRACTS: dict[tuple[str, str], tuple[bytes, list]] = {}
_CACHED_FIXED_FEES: dict[tuple[int, int], tuple[bytes, list]] = {}


def _contracts_dir() -> Path:
    return Path(__file__).parent.parent.parent / "contracts" / "src"


def _compile_contract_source(source: str, *, contract_name: str) -> tuple[bytes, list]:
    compiler = SolidityCompiler()
    result = compiler.compile(source, contract_name=contract_name)
    if not result.success:
        raise RuntimeError(f"Failed to compile {contract_name}: {result.errors}")
    if result.bytecode is None or result.abi is None:
        raise RuntimeError(f"{contract_name} compiled without bytecode or ABI")
    return result.bytecode, result.abi


def _get_contract_bytecode_and_abi(
    filename: str, *, contract_name: str
) -> tuple[bytes, list]:
    cache_key = (filename, contract_name)
    cached = _CACHED_CONTRACTS.get(cache_key)
    if cached is not None:
        return cached

    source = (_contracts_dir() / filename).read_text()
    compiled = _compile_contract_source(source, contract_name=contract_name)
    _CACHED_CONTRACTS[cache_key] = compiled
    return compiled


def get_vanilla_bytecode_and_abi() -> Tuple[bytes, list]:
    """Compile VanillaStrategy.sol once and cache.

    Returns:
        Tuple of (bytecode, abi) for the VanillaStrategy contract.

    Raises:
        RuntimeError: If compilation fails.
    """
    return _get_contract_bytecode_and_abi(
        "VanillaStrategy.sol",
        contract_name="VanillaStrategy",
    )


def get_starter_bytecode_and_abi() -> Tuple[bytes, list]:
    """Compile StarterStrategy.sol once and cache."""
    return _get_contract_bytecode_and_abi(
        "StarterStrategy.sol",
        contract_name="Strategy",
    )


def load_vanilla_strategy() -> EVMStrategyAdapter:
    """Load the default 30bps strategy used as the normalizer AMM.

    The normalizer AMM prevents degenerate strategies (like extreme fees)
    from appearing profitable by providing competition for retail flow.

    Returns:
        EVMStrategyAdapter wrapping the compiled VanillaStrategy.sol (30 bps).
    """
    bytecode, abi = get_vanilla_bytecode_and_abi()
    return EVMStrategyAdapter(bytecode=bytecode, abi=abi)


def load_starter_strategy() -> EVMStrategyAdapter:
    """Load the fixed 50 bps starter strategy."""
    bytecode, abi = get_starter_bytecode_and_abi()
    return EVMStrategyAdapter(bytecode=bytecode, abi=abi)


def fixed_fee_strategy_name(bid_fee_bps: int, ask_fee_bps: int) -> str:
    """Return a stable name for a generated fixed-fee strategy."""
    if bid_fee_bps == ask_fee_bps:
        return f"Fixed_{bid_fee_bps}bps"
    return f"Fixed_{bid_fee_bps}x{ask_fee_bps}bps"


def build_fixed_fee_source(bid_fee_bps: int, ask_fee_bps: int) -> str:
    """Build Solidity source for a generated fixed-fee strategy."""
    if bid_fee_bps < 0 or ask_fee_bps < 0:
        raise ValueError("Fixed-fee benchmark bps must be non-negative")

    strategy_name = fixed_fee_strategy_name(bid_fee_bps, ask_fee_bps)
    return f"""// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {{AMMStrategyBase}} from "./AMMStrategyBase.sol";
import {{IAMMStrategy, TradeInfo}} from "./IAMMStrategy.sol";

contract FixedFeeStrategy is AMMStrategyBase {{
    uint256 public constant BID_FEE = {bid_fee_bps} * BPS;
    uint256 public constant ASK_FEE = {ask_fee_bps} * BPS;

    function afterInitialize(uint256, uint256) external pure override returns (uint256, uint256) {{
        return (BID_FEE, ASK_FEE);
    }}

    function afterSwap(TradeInfo calldata) external pure override returns (uint256, uint256) {{
        return (BID_FEE, ASK_FEE);
    }}

    function getName() external pure override returns (string memory) {{
        return "{strategy_name}";
    }}
}}
"""


def get_fixed_fee_bytecode_and_abi(
    bid_fee_bps: int, ask_fee_bps: int
) -> Tuple[bytes, list]:
    """Compile a generated fixed-fee strategy and cache by fee pair."""
    cache_key = (bid_fee_bps, ask_fee_bps)
    cached = _CACHED_FIXED_FEES.get(cache_key)
    if cached is not None:
        return cached

    source = build_fixed_fee_source(bid_fee_bps, ask_fee_bps)
    compiled = _compile_contract_source(source, contract_name="FixedFeeStrategy")
    _CACHED_FIXED_FEES[cache_key] = compiled
    return compiled


def load_fixed_fee_strategy(
    bid_fee_bps: int,
    ask_fee_bps: int,
    *,
    name: Optional[str] = None,
) -> EVMStrategyAdapter:
    """Load a generated fixed-fee strategy without adding a source file."""
    bytecode, abi = get_fixed_fee_bytecode_and_abi(bid_fee_bps, ask_fee_bps)
    return EVMStrategyAdapter(
        bytecode=bytecode,
        abi=abi,
        name=name or fixed_fee_strategy_name(bid_fee_bps, ask_fee_bps),
    )
