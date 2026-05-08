// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {AMMStrategyBase} from "./AMMStrategyBase.sol";
import {TradeInfo} from "./IAMMStrategy.sol";

/// @title Worst Slice Spread Assembler
/// @notice Builds only a symmetric shared spread floor from layer-3 risk labels.
contract Strategy is AMMStrategyBase {
    uint256 internal constant BASE_FEE = 43 * BPS;

    uint256 internal constant DECAY_FAST = 8750 * BPS;
    uint256 internal constant DECAY_FLOW = 8600 * BPS;
    uint256 internal constant DECAY_SLOW = 9250 * BPS;

    uint256 internal constant ALPHA_SPOT = 12 * BPS;
    uint256 internal constant ALPHA_VOL = 24 * BPS;
    uint256 internal constant ALPHA_FLOW = 17 * BPS;
    uint256 internal constant ALPHA_HAZARD = 27 * BPS;
    uint256 internal constant ALPHA_STRESS = 16 * BPS;

    function afterInitialize(uint256 initialX, uint256 initialY)
        external
        override
        returns (uint256 bidFee, uint256 askFee)
    {
        uint256 spot = wdiv(initialY, initialX);

        slots[0] = spot;
        slots[1] = 0; // volatility label
        slots[2] = 0; // buy-flow label
        slots[3] = 0; // sell-flow label
        slots[4] = 0; // adverse label
        slots[5] = 0; // fragile-floor label
        slots[6] = spot;
        slots[7] = 0;
        slots[8] = 0; // divergence label
        slots[9] = 0; // flow-pressure label

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

        uint256 volLabel = wmul(slots[1], _gapAdjustedDecay(DECAY_FAST, gapShort, 1300 * BPS));
        uint256 buyFlow = wmul(slots[2], _gapAdjustedDecay(DECAY_FLOW, gapShort, 2100 * BPS));
        uint256 sellFlow = wmul(slots[3], _gapAdjustedDecay(DECAY_FLOW, gapShort, 2100 * BPS));
        uint256 adverseLabel = wmul(slots[4], _gapAdjustedDecay(DECAY_FAST, gapShort, 1500 * BPS));
        uint256 floorStress = wmul(slots[5], _gapAdjustedDecay(DECAY_SLOW, gapLong, 700 * BPS));
        uint256 divergenceLabel = wmul(slots[8], _gapAdjustedDecay(DECAY_SLOW, gapShort, 950 * BPS));

        uint256 convexJump = spotJump;
        if (spotJump > 7 * BPS) {
            convexJump += wmul(spotJump - 7 * BPS, spotJump);
        }
        uint256 convexDivergence = divergence;
        if (divergence > 7 * BPS) {
            convexDivergence += wmul(divergence - 7 * BPS, divergence);
        }
        uint256 volObservation = _max(tradeSize, _max(convexJump, convexDivergence));
        uint256 clusteredObservation = wmul(volObservation, _oneMinus(gapShort));
        uint256 adverseObservation = _max(
            convexDivergence,
            volObservation + wmul(clusteredObservation, 5200 * BPS)
        );

        volLabel = _blend(volLabel, volObservation, ALPHA_VOL);
        adverseLabel = _blend(adverseLabel, adverseObservation, ALPHA_HAZARD);
        divergenceLabel = _blend(divergenceLabel, divergence, ALPHA_HAZARD);

        uint256 flowPulse = tradeSize + wmul(volObservation, 3600 * BPS);
        uint256 crossPulse = wmul(flowPulse, 1800 * BPS);
        if (trade.isBuy) {
            buyFlow = clamp(buyFlow + flowPulse, 0, WAD);
            sellFlow = clamp(sellFlow + crossPulse, 0, WAD);
        } else {
            sellFlow = clamp(sellFlow + flowPulse, 0, WAD);
            buyFlow = clamp(buyFlow + crossPulse, 0, WAD);
        }

        uint256 totalFlow = buyFlow + sellFlow;
        uint256 flowImbalance = totalFlow == 0 ? 0 : wdiv(absDiff(buyFlow, sellFlow), totalFlow);
        uint256 flowPressure = _blend(slots[9], flowImbalance, ALPHA_FLOW);
        uint256 oneSidedFlow = wmul(flowPressure, _max(volLabel, adverseLabel));

        uint256 quietService = wmul(
            gapLong,
            _oneMinus(
                clamp(
                    adverseObservation * 6 +
                        wmul(flowPressure, 2600 * BPS) +
                        wmul(divergence, 3600 * BPS),
                    0,
                    WAD
                )
            )
        );
        uint256 fragilityObservation = _oneMinus(quietService);
        if (volObservation < 5 * BPS && divergence < 5 * BPS && flowPressure < 600 * BPS) {
            fragilityObservation = wmul(fragilityObservation, 5200 * BPS);
        }
        floorStress = _blend(floorStress, fragilityObservation, ALPHA_STRESS);

        uint256 worstSlice = _max(adverseLabel, _max(oneSidedFlow, divergenceLabel));
        uint256 minSlice = _min(adverseLabel, _min(volLabel, floorStress));
        uint256 nonlinearConsensus = wmul(worstSlice, minSlice);
        uint256 spreadLift =
            wmul(volLabel, 1350 * BPS) +
            wmul(worstSlice, 1650 * BPS) +
            wmul(floorStress, 360 * BPS) +
            wmul(nonlinearConsensus, 6200 * BPS);

        uint256 eventFloor = 0;
        uint256 eventSignal = volObservation + adverseObservation;
        if (eventSignal > 9 * BPS) {
            eventFloor = wmul(eventSignal - 9 * BPS, 760 * BPS);
        }
        uint256 sharedSpread = BASE_FEE + spreadLift + eventFloor;
        if (sharedSpread > 56 * BPS) {
            sharedSpread = 56 * BPS;
        }

        bidFee = clampFee(sharedSpread);
        askFee = bidFee;

        slots[0] = latentSpot;
        slots[1] = volLabel;
        slots[2] = buyFlow;
        slots[3] = sellFlow;
        slots[4] = adverseLabel;
        slots[5] = floorStress;
        slots[6] = currentSpot;
        slots[7] = trade.timestamp;
        slots[8] = divergenceLabel;
        slots[9] = flowPressure;

        return (bidFee, askFee);
    }

    function getName() external pure override returns (string memory) {
        return "WorstSliceSpreadAssembler";
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

    function _min(uint256 a, uint256 b) internal pure returns (uint256) {
        return a < b ? a : b;
    }

    function _oneMinus(uint256 x) internal pure returns (uint256) {
        return x >= WAD ? 0 : WAD - x;
    }
}
