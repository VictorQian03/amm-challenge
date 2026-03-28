"""Tests for the Solidity baseline module."""

from decimal import Decimal

from amm_competition.evm.baseline import (
    build_fixed_fee_source,
    fixed_fee_strategy_name,
    get_vanilla_bytecode_and_abi,
    load_fixed_fee_strategy,
    load_starter_strategy,
    load_vanilla_strategy,
)
from amm_competition.evm.adapter import EVMStrategyAdapter
from amm_competition.core.trade import TradeInfo


class TestGetVanillaBytecodeAndAbi:
    def test_returns_tuple(self, vanilla_bytecode_and_abi):
        """Verify return type is tuple of (bytes, list)."""
        bytecode, abi = vanilla_bytecode_and_abi
        assert isinstance(bytecode, bytes)
        assert isinstance(abi, list)

    def test_bytecode_not_empty(self, vanilla_bytecode_and_abi):
        """Verify bytecode has content."""
        bytecode, abi = vanilla_bytecode_and_abi
        assert len(bytecode) > 0

    def test_abi_contains_required_functions(self, vanilla_bytecode_and_abi):
        """Verify ABI contains afterInitialize, afterSwap, and getName."""
        bytecode, abi = vanilla_bytecode_and_abi
        function_names = {
            item.get("name") for item in abi if item.get("type") == "function"
        }
        assert "afterInitialize" in function_names
        assert "afterSwap" in function_names
        assert "getName" in function_names

    def test_caching_returns_same_objects(self):
        """Verify caching returns identical objects on repeated calls."""
        bytecode1, abi1 = get_vanilla_bytecode_and_abi()
        bytecode2, abi2 = get_vanilla_bytecode_and_abi()
        # Should be the same cached objects
        assert bytecode1 is bytecode2
        assert abi1 is abi2


class TestLoadVanillaStrategy:
    def test_creates_evm_strategy_adapter(self):
        """Verify load_vanilla_strategy returns an EVMStrategyAdapter."""
        strategy = load_vanilla_strategy()
        assert isinstance(strategy, EVMStrategyAdapter)

    def test_strategy_name_correct(self):
        """Verify getName returns 'Vanilla_30bps'."""
        strategy = load_vanilla_strategy()
        assert strategy.get_name() == "Vanilla_30bps"

    def test_strategy_fees_correct(self):
        """Verify afterInitialize returns 30 bps fees."""
        strategy = load_vanilla_strategy()
        fees = strategy.after_initialize(Decimal("100"), Decimal("10000"))
        assert fees.bid_fee == Decimal("0.003")
        assert fees.ask_fee == Decimal("0.003")

    def test_strategy_after_swap_returns_same_fees(self):
        """Verify afterSwap returns same 30 bps fees."""
        strategy = load_vanilla_strategy()
        strategy.after_initialize(Decimal("100"), Decimal("10000"))

        trade = TradeInfo(
            side="buy",
            amount_x=Decimal("10"),
            amount_y=Decimal("900"),
            timestamp=1,
            reserve_x=Decimal("110"),
            reserve_y=Decimal("9100"),
        )

        fees = strategy.after_swap(trade)
        assert fees.bid_fee == Decimal("0.003")
        assert fees.ask_fee == Decimal("0.003")

    def test_creates_fresh_instances(self):
        """Verify each call creates a new adapter instance."""
        strategy1 = load_vanilla_strategy()
        strategy2 = load_vanilla_strategy()
        # Should be different instances (though using same cached bytecode)
        assert strategy1 is not strategy2

    def test_strategy_can_reset(self):
        """Verify strategy reset works."""
        strategy = load_vanilla_strategy()
        strategy.after_initialize(Decimal("100"), Decimal("10000"))
        # Should not raise
        strategy.reset()
        # Can reinitialize after reset
        fees = strategy.after_initialize(Decimal("200"), Decimal("20000"))
        assert fees.bid_fee == Decimal("0.003")


class TestGeneratedFixedFeeStrategies:
    def test_fixed_fee_name_is_stable(self):
        assert fixed_fee_strategy_name(30, 30) == "Fixed_30bps"
        assert fixed_fee_strategy_name(20, 40) == "Fixed_20x40bps"

    def test_build_fixed_fee_source_embeds_name(self):
        source = build_fixed_fee_source(20, 40)
        assert "Fixed_20x40bps" in source
        assert "contract FixedFeeStrategy" in source

    def test_load_fixed_fee_strategy_returns_expected_fees(self):
        strategy = load_fixed_fee_strategy(20, 40)
        fees = strategy.after_initialize(Decimal("100"), Decimal("10000"))
        assert fees.bid_fee == Decimal("0.002")
        assert fees.ask_fee == Decimal("0.004")


class TestStarterStrategy:
    def test_load_starter_strategy_returns_expected_name(self):
        strategy = load_starter_strategy()
        assert strategy.get_name() == "StarterStrategy"

    def test_load_starter_strategy_returns_expected_fee(self):
        strategy = load_starter_strategy()
        fees = strategy.after_initialize(Decimal("100"), Decimal("10000"))
        assert fees.bid_fee == Decimal("0.005")
        assert fees.ask_fee == Decimal("0.005")
