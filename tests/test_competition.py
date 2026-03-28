"""Tests for competition framework."""

import pytest
from decimal import Decimal
from types import SimpleNamespace

import amm_sim_rs

from amm_competition.competition.match import MatchRunner, HyperparameterVariance


class TestMatchRunner:
    def test_run_match(self, vanilla_bytecode_and_abi):
        from amm_competition.evm.adapter import EVMStrategyAdapter

        config = amm_sim_rs.SimulationConfig(
            n_steps=50,
            initial_price=100.0,
            initial_x=100.0,
            initial_y=10000.0,
            gbm_mu=0.0,
            gbm_sigma=0.001,
            gbm_dt=1.0,
            retail_arrival_rate=5.0,
            retail_mean_size=2.0,
            retail_size_sigma=0.7,
            retail_buy_prob=0.5,
            seed=42,
        )
        variance = HyperparameterVariance(
            retail_mean_size_min=2.0,
            retail_mean_size_max=2.0,
            vary_retail_mean_size=False,
            retail_arrival_rate_min=5.0,
            retail_arrival_rate_max=5.0,
            vary_retail_arrival_rate=False,
            gbm_sigma_min=0.001,
            gbm_sigma_max=0.001,
            vary_gbm_sigma=False,
        )
        runner = MatchRunner(
            n_simulations=5, config=config, n_workers=1, variance=variance
        )

        bytecode, abi = vanilla_bytecode_and_abi
        strategy_a = EVMStrategyAdapter(bytecode=bytecode, abi=abi)
        strategy_b = EVMStrategyAdapter(
            bytecode=bytecode, abi=abi, name="Vanilla_30bps"
        )

        result = runner.run_match(strategy_a, strategy_b)

        assert result.total_games == 5
        assert result.wins_a + result.wins_b + result.draws == 5
        assert result.strategy_a == "Vanilla_30bps"
        assert result.strategy_b == "Vanilla_30bps"

    def test_match_winner(self, vanilla_bytecode_and_abi):
        from amm_competition.evm.adapter import EVMStrategyAdapter

        config = amm_sim_rs.SimulationConfig(
            n_steps=50,
            initial_price=100.0,
            initial_x=100.0,
            initial_y=10000.0,
            gbm_mu=0.0,
            gbm_sigma=0.001,
            gbm_dt=1.0,
            retail_arrival_rate=5.0,
            retail_mean_size=2.0,
            retail_size_sigma=0.7,
            retail_buy_prob=0.5,
            seed=42,
        )
        variance = HyperparameterVariance(
            retail_mean_size_min=2.0,
            retail_mean_size_max=2.0,
            vary_retail_mean_size=False,
            retail_arrival_rate_min=5.0,
            retail_arrival_rate_max=5.0,
            vary_retail_arrival_rate=False,
            gbm_sigma_min=0.001,
            gbm_sigma_max=0.001,
            vary_gbm_sigma=False,
        )
        runner = MatchRunner(
            n_simulations=11, config=config, n_workers=1, variance=variance
        )

        bytecode, abi = vanilla_bytecode_and_abi
        strategy_a = EVMStrategyAdapter(bytecode=bytecode, abi=abi)
        strategy_b = EVMStrategyAdapter(bytecode=bytecode, abi=abi)

        result = runner.run_match(strategy_a, strategy_b)

        # Winner can be either, but total should be 11
        assert result.total_games == 11

    def test_pnl_accumulated(self, vanilla_bytecode_and_abi):
        from amm_competition.evm.adapter import EVMStrategyAdapter

        config = amm_sim_rs.SimulationConfig(
            n_steps=50,
            initial_price=100.0,
            initial_x=100.0,
            initial_y=10000.0,
            gbm_mu=0.0,
            gbm_sigma=0.001,
            gbm_dt=1.0,
            retail_arrival_rate=5.0,
            retail_mean_size=2.0,
            retail_size_sigma=0.7,
            retail_buy_prob=0.5,
            seed=42,
        )
        variance = HyperparameterVariance(
            retail_mean_size_min=2.0,
            retail_mean_size_max=2.0,
            vary_retail_mean_size=False,
            retail_arrival_rate_min=5.0,
            retail_arrival_rate_max=5.0,
            vary_retail_arrival_rate=False,
            gbm_sigma_min=0.001,
            gbm_sigma_max=0.001,
            vary_gbm_sigma=False,
        )
        runner = MatchRunner(
            n_simulations=5, config=config, n_workers=1, variance=variance
        )

        bytecode, abi = vanilla_bytecode_and_abi
        strategy_a = EVMStrategyAdapter(bytecode=bytecode, abi=abi)
        strategy_b = EVMStrategyAdapter(
            bytecode=bytecode, abi=abi, name="Vanilla_50bps"
        )

        result = runner.run_match(strategy_a, strategy_b)

        # PNL should be accumulated across simulations
        assert result.total_pnl_a != Decimal("0") or result.total_pnl_b != Decimal("0")

    def test_store_results(self, vanilla_bytecode_and_abi):
        from amm_competition.evm.adapter import EVMStrategyAdapter

        config = amm_sim_rs.SimulationConfig(
            n_steps=50,
            initial_price=100.0,
            initial_x=100.0,
            initial_y=10000.0,
            gbm_mu=0.0,
            gbm_sigma=0.001,
            gbm_dt=1.0,
            retail_arrival_rate=5.0,
            retail_mean_size=2.0,
            retail_size_sigma=0.7,
            retail_buy_prob=0.5,
            seed=42,
        )
        variance = HyperparameterVariance(
            retail_mean_size_min=2.0,
            retail_mean_size_max=2.0,
            vary_retail_mean_size=False,
            retail_arrival_rate_min=5.0,
            retail_arrival_rate_max=5.0,
            vary_retail_arrival_rate=False,
            gbm_sigma_min=0.001,
            gbm_sigma_max=0.001,
            vary_gbm_sigma=False,
        )
        runner = MatchRunner(
            n_simulations=3, config=config, n_workers=1, variance=variance
        )

        bytecode, abi = vanilla_bytecode_and_abi
        strategy_a = EVMStrategyAdapter(bytecode=bytecode, abi=abi)
        strategy_b = EVMStrategyAdapter(
            bytecode=bytecode, abi=abi, name="Vanilla_30bps"
        )

        result = runner.run_match(strategy_a, strategy_b, store_results=True)

        assert len(result.simulation_results) == 3

    def test_same_name_strategies_no_collision(self, vanilla_bytecode_and_abi):
        """Test that strategies with the same getName() don't cause HashMap collision."""
        from amm_competition.evm.adapter import EVMStrategyAdapter

        config = amm_sim_rs.SimulationConfig(
            n_steps=50,
            initial_price=100.0,
            initial_x=100.0,
            initial_y=10000.0,
            gbm_mu=0.0,
            gbm_sigma=0.001,
            gbm_dt=1.0,
            retail_arrival_rate=5.0,
            retail_mean_size=2.0,
            retail_size_sigma=0.7,
            retail_buy_prob=0.5,
            seed=42,
        )
        variance = HyperparameterVariance(
            retail_mean_size_min=2.0,
            retail_mean_size_max=2.0,
            vary_retail_mean_size=False,
            retail_arrival_rate_min=5.0,
            retail_arrival_rate_max=5.0,
            vary_retail_arrival_rate=False,
            gbm_sigma_min=0.001,
            gbm_sigma_max=0.001,
            vary_gbm_sigma=False,
        )
        runner = MatchRunner(
            n_simulations=5, config=config, n_workers=1, variance=variance
        )

        # Both strategies use same bytecode and will have same getName() return value
        # Without the fix, this would cause a HashMap key collision
        bytecode, abi = vanilla_bytecode_and_abi
        strategy_a = EVMStrategyAdapter(bytecode=bytecode, abi=abi)
        strategy_b = EVMStrategyAdapter(bytecode=bytecode, abi=abi)

        # Both should return "Vanilla_30bps" from get_name()
        assert strategy_a.get_name() == strategy_b.get_name() == "Vanilla_30bps"

        result = runner.run_match(strategy_a, strategy_b, store_results=True)

        # Should complete without errors and have valid results
        assert result.total_games == 5
        # Since both strategies are identical, results should be a draw or close
        # The important thing is that we get results for both, not zeros
        assert len(result.simulation_results) == 5
        # Check that simulation results contain data for both strategies
        first_sim = result.simulation_results[0]
        assert len(first_sim.pnl) == 2  # Should have PnL for both strategies

    def test_store_results_include_regime_metadata_and_explicit_seed_block(
        self,
        vanilla_bytecode_and_abi,
    ):
        from amm_competition.evm.adapter import EVMStrategyAdapter

        config = amm_sim_rs.SimulationConfig(
            n_steps=25,
            initial_price=100.0,
            initial_x=100.0,
            initial_y=10000.0,
            gbm_mu=0.0,
            gbm_sigma=0.001,
            gbm_dt=1.0,
            retail_arrival_rate=5.0,
            retail_mean_size=2.0,
            retail_size_sigma=0.7,
            retail_buy_prob=0.5,
            seed=None,
        )
        variance = HyperparameterVariance(
            retail_mean_size_min=2.0,
            retail_mean_size_max=2.0,
            vary_retail_mean_size=False,
            retail_arrival_rate_min=5.0,
            retail_arrival_rate_max=5.0,
            vary_retail_arrival_rate=False,
            gbm_sigma_min=0.001,
            gbm_sigma_max=0.001,
            vary_gbm_sigma=False,
        )
        runner = MatchRunner(
            n_simulations=3,
            config=config,
            n_workers=1,
            variance=variance,
            seed_block=(100, 101, 102),
        )

        bytecode, abi = vanilla_bytecode_and_abi
        strategy_a = EVMStrategyAdapter(bytecode=bytecode, abi=abi)
        strategy_b = EVMStrategyAdapter(
            bytecode=bytecode, abi=abi, name="Vanilla_30bps"
        )

        result = runner.run_match(strategy_a, strategy_b, store_results=True)

        assert [sim.seed for sim in result.simulation_results] == [100, 101, 102]
        first_sim = result.simulation_results[0]
        assert first_sim.gbm_sigma == pytest.approx(0.001)
        assert first_sim.retail_arrival_rate == pytest.approx(5.0)
        assert first_sim.retail_mean_size == pytest.approx(2.0)

    def test_seed_block_rejects_duplicates(self):
        config = amm_sim_rs.SimulationConfig(
            n_steps=10,
            initial_price=100.0,
            initial_x=100.0,
            initial_y=10000.0,
            gbm_mu=0.0,
            gbm_sigma=0.001,
            gbm_dt=1.0,
            retail_arrival_rate=5.0,
            retail_mean_size=2.0,
            retail_size_sigma=0.7,
            retail_buy_prob=0.5,
            seed=None,
        )
        variance = HyperparameterVariance(
            retail_mean_size_min=2.0,
            retail_mean_size_max=2.0,
            vary_retail_mean_size=False,
            retail_arrival_rate_min=5.0,
            retail_arrival_rate_max=5.0,
            vary_retail_arrival_rate=False,
            gbm_sigma_min=0.001,
            gbm_sigma_max=0.001,
            vary_gbm_sigma=False,
        )

        with pytest.raises(ValueError, match="duplicate seeds"):
            MatchRunner(
                n_simulations=2,
                config=config,
                n_workers=1,
                variance=variance,
                seed_block=(7, 7),
            )

    def test_store_results_rejects_missing_required_telemetry(
        self,
        vanilla_bytecode_and_abi,
        monkeypatch,
    ):
        config = amm_sim_rs.SimulationConfig(
            n_steps=10,
            initial_price=100.0,
            initial_x=100.0,
            initial_y=10000.0,
            gbm_mu=0.0,
            gbm_sigma=0.001,
            gbm_dt=1.0,
            retail_arrival_rate=1.0,
            retail_mean_size=2.0,
            retail_size_sigma=0.7,
            retail_buy_prob=0.5,
            seed=None,
        )
        variance = HyperparameterVariance(
            retail_mean_size_min=2.0,
            retail_mean_size_max=2.0,
            vary_retail_mean_size=False,
            retail_arrival_rate_min=1.0,
            retail_arrival_rate_max=1.0,
            vary_retail_arrival_rate=False,
            gbm_sigma_min=0.001,
            gbm_sigma_max=0.001,
            vary_gbm_sigma=False,
        )
        runner = MatchRunner(
            n_simulations=1,
            config=config,
            n_workers=1,
            variance=variance,
            seed_block=(7,),
        )

        rust_result = SimpleNamespace(
            seed=7,
            strategies=["submission", "normalizer"],
            pnl={"submission": 1.5, "normalizer": 1.0},
            edges={"submission": 1.5, "normalizer": 1.0},
            initial_fair_price=100.0,
            initial_reserves={
                "submission": (100.0, 10000.0),
                "normalizer": (100.0, 10000.0),
            },
            steps=[],
            arb_volume_y={"submission": 2.0, "normalizer": 1.0},
            retail_volume_y={"submission": 10.0, "normalizer": 5.0},
            average_fees={"submission": (0.0075, 0.0075), "normalizer": (0.003, 0.003)},
            retail_edge={"submission": 4.0, "normalizer": 1.0},
            arb_edge={"submission": -1.0, "normalizer": -0.5},
            retail_trade_count={"submission": 3, "normalizer": 2},
            arb_trade_count={"submission": 1, "normalizer": 1},
            max_fee_jump={"submission": 0.001, "normalizer": 0.0},
        )
        batch_result = SimpleNamespace(results=[rust_result])
        monkeypatch.setattr(
            "amm_competition.competition.match.amm_sim_rs.run_batch",
            lambda *_args, **_kwargs: batch_result,
        )

        from amm_competition.evm.adapter import EVMStrategyAdapter

        bytecode, abi = vanilla_bytecode_and_abi
        strategy_a = EVMStrategyAdapter(bytecode=bytecode, abi=abi)
        strategy_b = EVMStrategyAdapter(bytecode=bytecode, abi=abi)

        with pytest.raises(RuntimeError, match="time_weighted_fees"):
            runner.run_match(strategy_a, strategy_b, store_results=True)
