// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {AMMStrategyBase} from "./AMMStrategyBase.sol";
import {TradeInfo} from "./IAMMStrategy.sol";

/// @title Rank Copula Risk Splitter
/// @notice Classifies joint rank dependence into discrete firewall states used only for layer-3 risk.
contract Strategy is AMMStrategyBase {
    uint256 internal constant BASE_FEE = 16 * BPS;

    uint256 internal constant DECAY_VOL = 9000 * BPS;
    uint256 internal constant DECAY_FLOW = 8700 * BPS;
    uint256 internal constant DECAY_HAZARD = 8900 * BPS;
    uint256 internal constant DECAY_CALM = 9300 * BPS;
    uint256 internal constant DECAY_DIVERGENCE = 9150 * BPS;

    uint256 internal constant ALPHA_SPOT = 12 * BPS;
    uint256 internal constant ALPHA_VOL = 26 * BPS;
    uint256 internal constant ALPHA_HAZARD = 30 * BPS;
    uint256 internal constant ALPHA_CALM = 14 * BPS;
    uint256 internal constant ALPHA_DIVERGENCE = 22 * BPS;
    uint256 internal constant ALPHA_FLOW = 18 * BPS;

    function afterInitialize(uint256 initialX, uint256 initialY)
        external
        override
        returns (uint256 bidFee, uint256 askFee)
    {
        uint256 spot = wdiv(initialY, initialX);

        slots[0] = spot;
        slots[1] = 0;
        slots[2] = 0;
        slots[3] = 0;
        slots[4] = 0;
        slots[5] = 0;
        slots[6] = spot;
        slots[7] = 0;
        slots[8] = 0;
        slots[9] = 0;

        return (BASE_FEE, BASE_FEE);
    }

    function afterSwap(TradeInfo calldata trade)
        external
        override
        returns (uint256 bidFee, uint256 askFee)
    {
        uint256 currentSpot = wdiv(trade.reserveY, trade.reserveX);
        uint256 latentSpot = _blend(slots[0], currentSpot, ALPHA_SPOT);
        uint256 lastSpot = slots[6];
        uint256 gap = trade.timestamp > slots[7] ? trade.timestamp - slots[7] : 0;

        uint256 sizeX = wdiv(trade.amountX, trade.reserveX);
        uint256 sizeY = wdiv(trade.amountY, trade.reserveY);
        uint256 tradeSize = _max(sizeX, sizeY);
        uint256 spotJump = lastSpot == 0 ? 0 : wdiv(absDiff(currentSpot, lastSpot), lastSpot);
        uint256 divergence = latentSpot == 0 ? 0 : wdiv(absDiff(currentSpot, latentSpot), latentSpot);

        uint256 gapShort = _gapRatio(gap, 3);
        uint256 gapLong = _gapRatio(gap, 8);

        uint256 volMemory = wmul(slots[1], _gapAdjustedDecay(DECAY_VOL, gapShort, 1400 * BPS));
        uint256 buyFlow = wmul(slots[2], _gapAdjustedDecay(DECAY_FLOW, gapShort, 2200 * BPS));
        uint256 sellFlow = wmul(slots[3], _gapAdjustedDecay(DECAY_FLOW, gapShort, 2200 * BPS));
        uint256 hazardMemory = wmul(slots[4], _gapAdjustedDecay(DECAY_HAZARD, gapShort, 1700 * BPS));
        uint256 calmMemory = wmul(slots[5], _gapAdjustedDecay(DECAY_CALM, gapLong, 700 * BPS));
        uint256 divergenceMemory =
            wmul(slots[8], _gapAdjustedDecay(DECAY_DIVERGENCE, gapShort, 1200 * BPS));

        uint256 spotJumpVol = spotJump;
        if (spotJump > 6 * BPS) {
            spotJumpVol += wmul(spotJump - 6 * BPS, spotJump);
        }
        uint256 divergenceVol = divergence;
        if (divergence > 6 * BPS) {
            divergenceVol += wmul(divergence - 6 * BPS, divergence);
        }
        uint256 volObservation = _max(tradeSize, _max(spotJumpVol, divergenceVol));
        uint256 clusterObservation = wmul(volObservation, _oneMinus(gapShort));
        uint256 hazardObservation = _max(divergenceVol, volObservation + wmul(clusterObservation, 7000 * BPS));
        uint256 calmObservation = wmul(gapLong, _oneMinus(clamp(hazardObservation * 6, 0, WAD)));

        volMemory = _blend(volMemory, volObservation, ALPHA_VOL);
        hazardMemory = _blend(hazardMemory, hazardObservation, ALPHA_HAZARD);
        calmMemory = _blend(calmMemory, calmObservation, ALPHA_CALM);
        divergenceMemory = _blend(divergenceMemory, divergence, ALPHA_DIVERGENCE);

        uint256 flowPulse = tradeSize + wmul(volObservation, 4500 * BPS);
        uint256 crossPulse = wmul(flowPulse, 2200 * BPS);
        if (trade.isBuy) {
            buyFlow = clamp(buyFlow + flowPulse, 0, WAD);
            sellFlow = clamp(sellFlow + crossPulse, 0, WAD);
        } else {
            sellFlow = clamp(sellFlow + flowPulse, 0, WAD);
            buyFlow = clamp(buyFlow + crossPulse, 0, WAD);
        }

        uint256 totalFlow = buyFlow + sellFlow;
        uint256 buyShare = _share(buyFlow, totalFlow);
        uint256 sellShare = _share(sellFlow, totalFlow);
        uint256 flowImbalance = totalFlow == 0 ? 0 : wdiv(absDiff(buyFlow, sellFlow), totalFlow);
        uint256 flowPressure = _blend(slots[9], flowImbalance, ALPHA_FLOW);
        uint256 oneSidedFlow = wmul(flowImbalance, _max(volMemory, hazardMemory));
        bool toxicBidSide = currentSpot >= latentSpot;
        bool continuationAligned = toxicBidSide ? buyFlow >= sellFlow : sellFlow > buyFlow;

        uint256 quietGate = _oneMinus(
            clamp(
                wmul(volMemory, 2400 * BPS) +
                    wmul(hazardMemory, 2000 * BPS) +
                    wmul(flowPressure, 2000 * BPS) +
                    wmul(spotJump, 1800 * BPS),
                0,
                WAD
            )
        );
        if (gap >= 3) {
            uint256 quietRecenter =
                wmul(quietGate, gap >= 5 ? 1050 * BPS : gap >= 4 ? 750 * BPS : 550 * BPS);
            if (continuationAligned) {
                uint256 continuationVeto = clamp(
                    wmul(flowPressure, 2800 * BPS) +
                        wmul(oneSidedFlow, 2200 * BPS) +
                        wmul(_max(divergenceMemory, spotJump), 1400 * BPS),
                    0,
                    4500 * BPS
                );
                quietRecenter = wmul(quietRecenter, _oneMinus(continuationVeto));
            }
            latentSpot = _blend(latentSpot, currentSpot, quietRecenter);
        }
        if (gap >= 4) {
            uint256 postRecenterDivergence =
                latentSpot == 0 ? 0 : wdiv(absDiff(currentSpot, latentSpot), latentSpot);
            uint256 reconvergenceGate = _oneMinus(clamp(wmul(postRecenterDivergence, 10000 * BPS), 0, WAD));
            uint256 quietDecay = wmul(wmul(quietGate, reconvergenceGate), wmul(gapLong, calmMemory));
            divergenceMemory = wmul(divergenceMemory, _oneMinus(clamp(wmul(quietDecay, 1200 * BPS), 0, WAD)));
        }

        uint256 copulaState = _copulaState(
            _rank(tradeSize, 250 * BPS, 800 * BPS, 1800 * BPS),
            _rank(_max(spotJumpVol, divergenceVol), 180 * BPS, 650 * BPS, 1400 * BPS),
            _rank(flowImbalance, 1200 * BPS, 3000 * BPS, 5600 * BPS),
            gapShort
        );

        uint256 richSignal = toxicBidSide ? divergenceMemory : 0;
        uint256 cheapSignal = toxicBidSide ? 0 : divergenceMemory;
        uint256 sideHazard = hazardMemory + wmul(flowImbalance, _max(volMemory, divergenceMemory));
        uint256 copulaFirewall = _copulaFirewall(copulaState);
        sideHazard = clamp(sideHazard + copulaFirewall, 0, WAD);

        uint256 flowDirectionalRisk = 0;
        if (flowPressure > 500 * BPS) {
            uint256 extensionSignal = _max(divergenceMemory, spotJump);
            if (extensionSignal > 3 * BPS) {
                flowDirectionalRisk = wmul(flowPressure + wmul(extensionSignal, 2200 * BPS), 320 * BPS);
            }
        }
        if (copulaState >= 2) {
            flowDirectionalRisk += wmul(copulaFirewall, copulaState == 4 ? 2600 * BPS : 1800 * BPS);
        }

        uint256 bidFlowRisk = 0;
        uint256 askFlowRisk = 0;
        if (flowDirectionalRisk > 0) {
            if (toxicBidSide && buyFlow >= sellFlow) {
                askFlowRisk = flowDirectionalRisk;
            } else if (!toxicBidSide && sellFlow > buyFlow) {
                bidFlowRisk = flowDirectionalRisk;
            }
        }

        uint256 bidRiskSignal = wmul(sellShare, sideHazard) + wmul(richSignal, 8500 * BPS) + bidFlowRisk;
        uint256 askRiskSignal = wmul(buyShare, sideHazard) + wmul(cheapSignal, 8500 * BPS) + askFlowRisk;

        uint256 sharedSpread =
            BASE_FEE +
            wmul(volMemory, 1800 * BPS) +
            wmul(hazardMemory, 1900 * BPS);
        uint256 eventSignal = volObservation + hazardObservation;
        if (eventSignal > WAD) {
            eventSignal = WAD;
        }
        sharedSpread += wmul(eventSignal, 220 * BPS);

        uint256 directionalBurstFee = 0;
        if (eventSignal > 8 * BPS) {
            directionalBurstFee = wmul(eventSignal - 8 * BPS, 1850 * BPS);
        }
        uint256 bidProtection = wmul(bidRiskSignal, 5400 * BPS);
        uint256 askProtection = wmul(askRiskSignal, 5400 * BPS);
        uint256 oneSidedProtection = wmul(oneSidedFlow, 2800 * BPS);
        if (toxicBidSide) {
            bidProtection += directionalBurstFee + oneSidedProtection;
        } else {
            askProtection += directionalBurstFee + oneSidedProtection;
        }

        bidFee = clampFee(sharedSpread + bidProtection);
        askFee = clampFee(sharedSpread + askProtection);

        slots[0] = latentSpot;
        slots[1] = volMemory;
        slots[2] = buyFlow;
        slots[3] = sellFlow;
        slots[4] = hazardMemory;
        slots[5] = calmMemory;
        slots[6] = currentSpot;
        slots[7] = trade.timestamp;
        slots[8] = divergenceMemory;
        slots[9] = flowPressure;

        return (bidFee, askFee);
    }

    function getName() external pure override returns (string memory) {
        return "RankCopulaRiskSplitter";
    }

    function _rank(uint256 x, uint256 low, uint256 mid, uint256 high) internal pure returns (uint256) {
        if (x >= high) {
            return 3;
        }
        if (x >= mid) {
            return 2;
        }
        if (x >= low) {
            return 1;
        }
        return 0;
    }

    function _copulaState(
        uint256 sizeRank,
        uint256 moveRank,
        uint256 flowRank,
        uint256 gapShort
    ) internal pure returns (uint256) {
        uint256 jointRank = sizeRank + moveRank + flowRank;
        if (moveRank >= 3 && flowRank >= 2 && gapShort < WAD) {
            return 4;
        }
        if (sizeRank >= 2 && moveRank >= 2 && flowRank >= 2) {
            return 3;
        }
        if (jointRank >= 5 && gapShort < 8000 * BPS) {
            return 2;
        }
        if (jointRank >= 3) {
            return 1;
        }
        return 0;
    }

    function _copulaFirewall(uint256 copulaState) internal pure returns (uint256) {
        if (copulaState == 4) {
            return 1400 * BPS;
        }
        if (copulaState == 3) {
            return 950 * BPS;
        }
        if (copulaState == 2) {
            return 520 * BPS;
        }
        if (copulaState == 1) {
            return 180 * BPS;
        }
        return 0;
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

    function _gapAdjustedDecay(uint256 baseDecay, uint256 gapRatio, uint256 gapImpact)
        internal
        pure
        returns (uint256)
    {
        return wmul(baseDecay, WAD - wmul(gapRatio, gapImpact));
    }

    function _max(uint256 a, uint256 b) internal pure returns (uint256) {
        return a > b ? a : b;
    }

    function _oneMinus(uint256 x) internal pure returns (uint256) {
        return x >= WAD ? 0 : WAD - x;
    }

    function _share(uint256 part, uint256 total) internal pure returns (uint256) {
        if (total == 0) {
            return WAD / 2;
        }
        return wdiv(part, total);
    }
}
