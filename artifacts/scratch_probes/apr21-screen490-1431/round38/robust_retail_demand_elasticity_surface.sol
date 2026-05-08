// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {AMMStrategyBase} from "./AMMStrategyBase.sol";
import {TradeInfo} from "./IAMMStrategy.sol";

/// @title Robust Retail Demand Elasticity Surface
/// @notice Builds the quote from robust retail demand-elasticity bins and hold-only adverse protection.
contract Strategy is AMMStrategyBase {
    uint256 internal constant BASE_FEE = 18 * BPS;

    uint256 internal constant DECAY_FAST = 8850 * BPS;
    uint256 internal constant DECAY_FLOW = 8680 * BPS;
    uint256 internal constant DECAY_SLOW = 9250 * BPS;
    uint256 internal constant DECAY_DEMAND = 9050 * BPS;

    uint256 internal constant ALPHA_SPOT = 12 * BPS;
    uint256 internal constant ALPHA_VOL = 25 * BPS;
    uint256 internal constant ALPHA_ADVERSE = 29 * BPS;
    uint256 internal constant ALPHA_FLOW = 18 * BPS;
    uint256 internal constant ALPHA_DEMAND = 21 * BPS;
    uint256 internal constant ALPHA_HOLD = 16 * BPS;

    function afterInitialize(uint256 initialX, uint256 initialY)
        external
        override
        returns (uint256 bidFee, uint256 askFee)
    {
        uint256 spot = wdiv(initialY, initialX);

        slots[0] = spot; // latent fair spot
        slots[1] = 0; // volatility label
        slots[2] = 0; // buy-flow label
        slots[3] = 0; // sell-flow label
        slots[4] = 0; // adverse-evidence label
        slots[5] = 0; // robust elastic-demand label
        slots[6] = spot; // last observed spot
        slots[7] = 0; // last timestamp
        slots[8] = 0; // robust inelastic-demand label
        slots[9] = 0; // flow-skew label
        slots[10] = 0; // hold-only adverse inelastic label

        return (BASE_FEE, BASE_FEE);
    }

    function afterSwap(TradeInfo calldata trade)
        external
        override
        returns (uint256 bidFee, uint256 askFee)
    {
        uint256 currentSpot = wdiv(trade.reserveY, trade.reserveX);
        uint256 latentSpot = _blend(slots[0], currentSpot, ALPHA_SPOT);
        uint256 gap = trade.timestamp > slots[7] ? trade.timestamp - slots[7] : 0;

        uint256 tradeSize = _max(
            wdiv(trade.amountX, trade.reserveX),
            wdiv(trade.amountY, trade.reserveY)
        );
        uint256 spotJump = slots[6] == 0 ? 0 : wdiv(absDiff(currentSpot, slots[6]), slots[6]);
        uint256 divergence = latentSpot == 0 ? 0 : wdiv(absDiff(currentSpot, latentSpot), latentSpot);
        uint256 gapShort = _gapRatio(gap, 3);
        uint256 gapLong = _gapRatio(gap, 9);

        uint256 volLabel = wmul(slots[1], _gapAdjustedDecay(DECAY_FAST, gapShort, 1350 * BPS));
        uint256 buyFlow = wmul(slots[2], _gapAdjustedDecay(DECAY_FLOW, gapShort, 2150 * BPS));
        uint256 sellFlow = wmul(slots[3], _gapAdjustedDecay(DECAY_FLOW, gapShort, 2150 * BPS));
        uint256 adverseLabel = wmul(slots[4], _gapAdjustedDecay(DECAY_FAST, gapShort, 1600 * BPS));
        uint256 elasticDemand = wmul(slots[5], _gapAdjustedDecay(DECAY_DEMAND, gapLong, 850 * BPS));
        uint256 inelasticDemand = wmul(slots[8], _gapAdjustedDecay(DECAY_DEMAND, gapLong, 650 * BPS));
        uint256 flowSkew = wmul(slots[9], _gapAdjustedDecay(DECAY_SLOW, gapShort, 900 * BPS));
        uint256 holdOnlyLabel = wmul(slots[10], _gapAdjustedDecay(DECAY_SLOW, gapLong, 500 * BPS));

        uint256 convexJump = spotJump;
        if (spotJump > 6 * BPS) {
            convexJump += wmul(spotJump - 6 * BPS, spotJump);
        }
        uint256 convexDivergence = divergence;
        if (divergence > 6 * BPS) {
            convexDivergence += wmul(divergence - 6 * BPS, divergence);
        }

        uint256 volObservation = _max(tradeSize, _max(convexJump, convexDivergence));
        uint256 clusterObservation = wmul(volObservation, _oneMinus(gapShort));
        uint256 adverseObservation = _max(
            convexDivergence,
            volObservation + wmul(clusterObservation, 6200 * BPS)
        );

        volLabel = _blend(volLabel, volObservation, ALPHA_VOL);
        adverseLabel = _blend(adverseLabel, adverseObservation, ALPHA_ADVERSE);

        uint256 flowPulse = tradeSize + wmul(volObservation, 4100 * BPS);
        uint256 crossPulse = wmul(flowPulse, 1900 * BPS);
        if (trade.isBuy) {
            buyFlow = clamp(buyFlow + flowPulse, 0, WAD);
            sellFlow = clamp(sellFlow + crossPulse, 0, WAD);
        } else {
            sellFlow = clamp(sellFlow + flowPulse, 0, WAD);
            buyFlow = clamp(buyFlow + crossPulse, 0, WAD);
        }

        uint256 totalFlow = buyFlow + sellFlow;
        uint256 flowImbalance = totalFlow == 0 ? 0 : wdiv(absDiff(buyFlow, sellFlow), totalFlow);
        flowSkew = _blend(flowSkew, flowImbalance, ALPHA_FLOW);

        uint256 moveIntensity = _max(convexJump, convexDivergence);
        uint256 demandDenominator = tradeSize + moveIntensity + 1;
        uint256 sizeShare = wdiv(tradeSize, demandDenominator);
        uint256 moveShare = wdiv(moveIntensity, demandDenominator);

        uint256 thinDemandPenalty = _oneMinus(clamp(tradeSize * 24, 0, WAD));
        uint256 slowConfirmation = wmul(gapLong, _oneMinus(clamp(volObservation * 8, 0, WAD)));
        uint256 elasticObservation = wmul(
            sizeShare,
            _oneMinus(
                clamp(
                    adverseObservation * 5 +
                        wmul(flowSkew, 1900 * BPS) +
                        wmul(thinDemandPenalty, 2200 * BPS),
                    0,
                    WAD
                )
            )
        );
        uint256 inelasticObservation = _max(
            moveShare,
            wmul(thinDemandPenalty, _oneMinus(slowConfirmation))
        );

        if (moveIntensity < 3 * BPS && tradeSize > 5 * BPS) {
            elasticObservation = clamp(elasticObservation + wmul(tradeSize, 1400 * BPS), 0, WAD);
            inelasticObservation = wmul(inelasticObservation, 7200 * BPS);
        }
        if (adverseObservation > 7 * BPS && tradeSize < 9 * BPS) {
            inelasticObservation = clamp(
                inelasticObservation + wmul(adverseObservation, 2100 * BPS),
                0,
                WAD
            );
        }

        elasticDemand = _blend(elasticDemand, elasticObservation, ALPHA_DEMAND);
        inelasticDemand = _blend(inelasticDemand, inelasticObservation, ALPHA_DEMAND);

        bool bidSideAdverse = currentSpot >= latentSpot;
        bool adverseFlowAligned = bidSideAdverse ? buyFlow >= sellFlow : sellFlow > buyFlow;
        uint256 adverseDemandEvidence = _max(adverseLabel, wmul(flowSkew, volLabel));
        uint256 holdObservation = 0;
        if (adverseFlowAligned && inelasticDemand > elasticDemand) {
            holdObservation = wmul(
                inelasticDemand - elasticDemand,
                clamp(adverseDemandEvidence * 7 + wmul(divergence, 4200 * BPS), 0, WAD)
            );
        }
        holdOnlyLabel = _blend(holdOnlyLabel, holdObservation, ALPHA_HOLD);

        uint256 demandCore = _max(
            wmul(inelasticDemand, 1450 * BPS),
            wmul(elasticDemand, 420 * BPS)
        );
        uint256 adverseCore = wmul(adverseDemandEvidence, 1800 * BPS);
        uint256 skewCore = wmul(wmul(flowSkew, inelasticDemand), 5600 * BPS);
        uint256 sharedSpread = BASE_FEE + demandCore + adverseCore + skewCore;

        uint256 bidHold = 0;
        uint256 askHold = 0;
        uint256 holdLift = wmul(holdOnlyLabel, 5200 * BPS) + wmul(adverseLabel, 520 * BPS);
        if (bidSideAdverse) {
            bidHold = holdLift;
        } else {
            askHold = holdLift;
        }

        bidFee = clampFee(sharedSpread + bidHold);
        askFee = clampFee(sharedSpread + askHold);

        slots[0] = latentSpot;
        slots[1] = volLabel;
        slots[2] = buyFlow;
        slots[3] = sellFlow;
        slots[4] = adverseLabel;
        slots[5] = elasticDemand;
        slots[6] = currentSpot;
        slots[7] = trade.timestamp;
        slots[8] = inelasticDemand;
        slots[9] = flowSkew;
        slots[10] = holdOnlyLabel;

        return (bidFee, askFee);
    }

    function getName() external pure override returns (string memory) {
        return "RobustRetailDemandElasticitySurface";
    }

    function _blend(uint256 prev, uint256 sample, uint256 alpha) internal pure returns (uint256) {
        return wmul(prev, WAD - alpha) + wmul(sample, alpha);
    }

    function _gapRatio(uint256 gap, uint256 horizon) internal pure returns (uint256) {
        if (gap >= horizon) {
            return WAD;
        }
        return (gap * WAD) / horizon;
    }

    function _gapAdjustedDecay(
        uint256 baseDecay,
        uint256 gapRatio,
        uint256 gapImpact
    ) internal pure returns (uint256) {
        return wmul(baseDecay, WAD - wmul(gapRatio, gapImpact));
    }

    function _max(uint256 a, uint256 b) internal pure returns (uint256) {
        return a > b ? a : b;
    }

    function _oneMinus(uint256 x) internal pure returns (uint256) {
        return x >= WAD ? 0 : WAD - x;
    }
}
