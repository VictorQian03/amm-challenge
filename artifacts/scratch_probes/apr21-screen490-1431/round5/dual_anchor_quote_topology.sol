// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {AMMStrategyBase} from "./AMMStrategyBase.sol";
import {TradeInfo} from "./IAMMStrategy.sol";

/// @title Dual Anchor Quote Topology
/// @notice Track a fast latent anchor and a slower structural anchor, then let their interaction separate shocks from drift.
contract Strategy is AMMStrategyBase {
    uint256 internal constant BASE_FEE = 16 * BPS;

    uint256 internal constant DECAY_VOL = 9000 * BPS;
    uint256 internal constant DECAY_FLOW = 8700 * BPS;
    uint256 internal constant DECAY_HAZARD = 8900 * BPS;
    uint256 internal constant DECAY_CALM = 9300 * BPS;
    uint256 internal constant DECAY_TENSION = 9200 * BPS;

    uint256 internal constant ALPHA_FAST = 18 * BPS;
    uint256 internal constant ALPHA_SLOW = 6 * BPS;
    uint256 internal constant ALPHA_VOL = 26 * BPS;
    uint256 internal constant ALPHA_HAZARD = 30 * BPS;
    uint256 internal constant ALPHA_CALM = 14 * BPS;
    uint256 internal constant ALPHA_TENSION = 20 * BPS;
    uint256 internal constant ALPHA_FLOW = 18 * BPS;
    uint256 internal constant ALPHA_REFILL = 16 * BPS;

    function afterInitialize(uint256 initialX, uint256 initialY)
        external
        override
        returns (uint256 bidFee, uint256 askFee)
    {
        uint256 spot = wdiv(initialY, initialX);

        slots[0] = spot; // fast latent anchor
        slots[1] = spot; // slow structural anchor
        slots[2] = 0; // realized volatility memory
        slots[3] = 0; // buy-side flow memory
        slots[4] = 0; // sell-side flow memory
        slots[5] = 0; // adverse-selection hazard memory
        slots[6] = 0; // calm / mean-reversion memory
        slots[7] = spot; // last observed spot
        slots[8] = 0; // last timestamp
        slots[9] = 0; // anchor tension memory
        slots[10] = 0; // directional flow pressure memory
        slots[11] = 0; // safe-side refill memory

        return (BASE_FEE, BASE_FEE);
    }

    function afterSwap(TradeInfo calldata trade)
        external
        override
        returns (uint256 bidFee, uint256 askFee)
    {
        uint256 currentSpot = wdiv(trade.reserveY, trade.reserveX);
        uint256 fastAnchor = _blend(slots[0], currentSpot, ALPHA_FAST);
        uint256 structuralAnchor = slots[1] == 0 ? fastAnchor : slots[1];
        uint256 lastSpot = slots[7];
        uint256 gap = trade.timestamp > slots[8] ? trade.timestamp - slots[8] : 0;

        uint256 sizeX = wdiv(trade.amountX, trade.reserveX);
        uint256 sizeY = wdiv(trade.amountY, trade.reserveY);
        uint256 tradeSize = _max(sizeX, sizeY);
        uint256 spotJump = lastSpot == 0 ? 0 : wdiv(absDiff(currentSpot, lastSpot), lastSpot);
        uint256 fastGap = fastAnchor == 0 ? 0 : wdiv(absDiff(currentSpot, fastAnchor), fastAnchor);
        uint256 slowGap = structuralAnchor == 0 ? 0 : wdiv(absDiff(currentSpot, structuralAnchor), structuralAnchor);
        uint256 anchorSpread =
            structuralAnchor == 0 ? 0 : wdiv(absDiff(fastAnchor, structuralAnchor), structuralAnchor);
        uint256 shockSignal = fastGap > slowGap ? fastGap - slowGap : slowGap - fastGap;
        uint256 driftSignal = _min(fastGap, slowGap);

        uint256 gapShort = _gapRatio(gap, 3);
        uint256 gapLong = _gapRatio(gap, 8);

        uint256 volMemory = wmul(
            slots[2],
            _gapAdjustedDecay(DECAY_VOL, gapShort, 1400 * BPS)
        );
        uint256 buyFlow = wmul(
            slots[3],
            _gapAdjustedDecay(DECAY_FLOW, gapShort, 2200 * BPS)
        );
        uint256 sellFlow = wmul(
            slots[4],
            _gapAdjustedDecay(DECAY_FLOW, gapShort, 2200 * BPS)
        );
        uint256 hazardMemory = wmul(
            slots[5],
            _gapAdjustedDecay(DECAY_HAZARD, gapShort, 1700 * BPS)
        );
        uint256 calmMemory = wmul(
            slots[6],
            _gapAdjustedDecay(DECAY_CALM, gapLong, 700 * BPS)
        );
        uint256 tensionMemory = wmul(
            slots[9],
            _gapAdjustedDecay(DECAY_TENSION, gapShort, 1300 * BPS)
        );

        uint256 spotJumpVol = spotJump;
        if (spotJump > 6 * BPS) {
            spotJumpVol += wmul(spotJump - 6 * BPS, spotJump);
        }
        uint256 fastSlowVol = anchorSpread;
        if (anchorSpread > 5 * BPS) {
            fastSlowVol += wmul(anchorSpread - 5 * BPS, anchorSpread);
        }
        uint256 volObservation = _max(tradeSize, _max(spotJumpVol, _max(fastGap, _max(slowGap, fastSlowVol))));
        uint256 clusterObservation = wmul(volObservation, _oneMinus(gapShort));
        uint256 hazardObservation =
            _max(fastSlowVol, volObservation + wmul(clusterObservation, 6500 * BPS));
        uint256 calmObservation = wmul(
            gapLong,
            _oneMinus(clamp(hazardObservation * 6, 0, WAD))
        );
        uint256 tensionObservation = clamp(
            wmul(driftSignal, 6400 * BPS) +
                wmul(shockSignal, 2200 * BPS) +
                wmul(anchorSpread, 1500 * BPS),
            0,
            WAD
        );

        volMemory = _blend(volMemory, volObservation, ALPHA_VOL);
        hazardMemory = _blend(hazardMemory, hazardObservation, ALPHA_HAZARD);
        calmMemory = _blend(calmMemory, calmObservation, ALPHA_CALM);
        tensionMemory = _blend(tensionMemory, tensionObservation, ALPHA_TENSION);

        uint256 flowPulse = tradeSize + wmul(volObservation, 3600 * BPS);
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
        uint256 flowPressure = _blend(slots[10], flowImbalance, ALPHA_FLOW);
        uint256 oneSidedFlow = wmul(flowImbalance, _max(volMemory, tensionMemory));

        bool toxicBidSide = currentSpot >= structuralAnchor;
        bool fastBidSide = currentSpot >= fastAnchor;
        bool anchorConcord = toxicBidSide == fastBidSide;
        bool persistentDrift = anchorConcord && driftSignal > 4 * BPS;
        bool transientShock = !anchorConcord && shockSignal > driftSignal;

        uint256 quietGate = _oneMinus(
            clamp(
                wmul(volMemory, 2400 * BPS) +
                    wmul(hazardMemory, 2000 * BPS) +
                    wmul(flowPressure, 1800 * BPS) +
                    wmul(tensionMemory, 2200 * BPS) +
                    wmul(spotJump, 1600 * BPS),
                0,
                WAD
            )
        );

        uint256 fastRecenter = wmul(
            quietGate,
            gap >= 5 ? 1150 * BPS : gap >= 4 ? 820 * BPS : gap >= 3 ? 560 * BPS : 220 * BPS
        );
        if (transientShock) {
            fastRecenter = clamp(
                fastRecenter + wmul(fastRecenter, 1100 * BPS),
                0,
                WAD
            );
        }
        if (anchorConcord && driftSignal > 4 * BPS && gap >= 3) {
            fastRecenter = clamp(
                fastRecenter + wmul(fastRecenter, 550 * BPS),
                0,
                WAD
            );
        }

        uint256 slowRecenter = 0;
        if (gap >= 3) {
            slowRecenter = wmul(
                quietGate,
                gap >= 6 ? 260 * BPS : gap >= 4 ? 170 * BPS : 90 * BPS
            );
            if (persistentDrift) {
                slowRecenter = clamp(
                    slowRecenter + wmul(slowRecenter, 900 * BPS),
                    0,
                    WAD
                );
            } else if (transientShock) {
                slowRecenter = wmul(slowRecenter, 3200 * BPS);
            }
        }

        fastAnchor = _blend(fastAnchor, currentSpot, fastRecenter);
        if (slowRecenter > 0) {
            structuralAnchor = _blend(structuralAnchor, currentSpot, slowRecenter);
        }

        uint256 recenteredGap =
            structuralAnchor == 0 ? 0 : wdiv(absDiff(currentSpot, structuralAnchor), structuralAnchor);
        uint256 recenteredFastGap =
            fastAnchor == 0 ? 0 : wdiv(absDiff(currentSpot, fastAnchor), fastAnchor);
        uint256 recenteredSpread =
            structuralAnchor == 0 ? 0 : wdiv(absDiff(fastAnchor, structuralAnchor), structuralAnchor);
        uint256 postTensionObservation = clamp(
            wmul(_max(recenteredGap, recenteredFastGap), 5800 * BPS) +
                wmul(recenteredSpread, 1800 * BPS),
            0,
            WAD
        );
        tensionMemory = _blend(tensionMemory, postTensionObservation, ALPHA_TENSION);

        if (gap >= 4) {
            uint256 recenterConfidence = _oneMinus(
                clamp(wmul(recenteredSpread, 10000 * BPS), 0, WAD)
            );
            uint256 structuralRelease = wmul(
                wmul(quietGate, recenterConfidence),
                gapLong
            );
            hazardMemory = wmul(
                hazardMemory,
                _oneMinus(clamp(wmul(structuralRelease, 1200 * BPS), 0, WAD))
            );
        }

        uint256 richSignal = 0;
        uint256 cheapSignal = 0;
        if (toxicBidSide) {
            richSignal = tensionMemory;
        } else {
            cheapSignal = tensionMemory;
        }

        uint256 sideHazard = hazardMemory + wmul(flowImbalance, _max(volMemory, tensionMemory));
        if (sideHazard > WAD) {
            sideHazard = WAD;
        }

        uint256 directionalProtection = 0;
        if (flowPressure > 450 * BPS) {
            uint256 directionSignal = _max(tensionMemory, _max(driftSignal, shockSignal));
            if (directionSignal > 3 * BPS) {
                uint256 toxicFlowSignal = flowPressure + wmul(directionSignal, 2400 * BPS);
                directionalProtection = wmul(toxicFlowSignal, 320 * BPS);
            }
        }
        if (persistentDrift) {
            directionalProtection = clamp(
                directionalProtection + wmul(tensionMemory, 2400 * BPS),
                0,
                WAD
            );
        }

        uint256 bidFlowRisk = 0;
        uint256 askFlowRisk = 0;
        if (directionalProtection > 0) {
            if (toxicBidSide) {
                if (buyFlow >= sellFlow) {
                    askFlowRisk = directionalProtection;
                }
            } else if (sellFlow > buyFlow) {
                bidFlowRisk = directionalProtection;
            }
        }

        uint256 refillObservation = wmul(
            gapLong,
            _oneMinus(
                clamp(
                    wmul(flowPressure, 3000 * BPS) +
                        wmul(hazardMemory, 2400 * BPS) +
                        wmul(tensionMemory, 2800 * BPS),
                    0,
                    WAD
                )
            )
        );
        if (anchorConcord && !persistentDrift && gap >= 3) {
            refillObservation = wmul(refillObservation, 1200 * BPS);
        }
        if (transientShock) {
            refillObservation = wmul(refillObservation, 7000 * BPS);
        }
        uint256 refillMemory = _blend(slots[11], refillObservation, ALPHA_REFILL);
        if (gap >= 4) {
            refillMemory = wmul(refillMemory, 9600 * BPS);
        } else if (gap >= 2) {
            refillMemory = wmul(refillMemory, 9000 * BPS);
        }

        uint256 bidRiskSignal =
            wmul(sellShare, sideHazard) +
            wmul(richSignal, 8200 * BPS) +
            bidFlowRisk;
        uint256 askRiskSignal =
            wmul(buyShare, sideHazard) +
            wmul(cheapSignal, 8200 * BPS) +
            askFlowRisk;

        uint256 opportunityGate = wmul(
            calmMemory,
            _oneMinus(
                clamp(
                    wmul(flowPressure, 2400 * BPS) +
                        wmul(tensionMemory, 3600 * BPS) +
                        wmul(hazardMemory, 1800 * BPS),
                    0,
                    WAD
                )
            )
        );
        uint256 bidOpportunitySignal = wmul(opportunityGate, cheapSignal);
        uint256 askOpportunitySignal = wmul(opportunityGate, richSignal);

        uint256 sharedSpread =
            BASE_FEE +
            wmul(volMemory, 1750 * BPS) +
            wmul(hazardMemory, 1850 * BPS) +
            wmul(tensionMemory, 1100 * BPS);

        uint256 eventSignal = volObservation + hazardObservation + tensionObservation;
        if (eventSignal > WAD) {
            eventSignal = WAD;
        }
        uint256 eventCarry = wmul(eventSignal, 220 * BPS);
        uint256 directionalBurstFee = 0;
        if (eventSignal > 8 * BPS) {
            uint256 burstSignal = eventSignal - 8 * BPS;
            eventCarry += wmul(burstSignal, 280 * BPS);
            directionalBurstFee = wmul(burstSignal, 1600 * BPS);
        }
        sharedSpread += eventCarry;

        uint256 sharedRebate = wmul(wmul(calmMemory, quietGate), 110 * BPS);
        sharedSpread = sharedSpread > sharedRebate ? sharedSpread - sharedRebate : MIN_FEE;
        uint256 bidProtection = wmul(bidRiskSignal, 5200 * BPS);
        uint256 askProtection = wmul(askRiskSignal, 5200 * BPS);
        uint256 oneSidedProtection = wmul(oneSidedFlow, 2600 * BPS);
        uint256 healingRebate = wmul(directionalBurstFee, 2600 * BPS);
        uint256 inventoryGate = wmul(
            quietGate,
            _oneMinus(
                clamp(
                    hazardMemory * 8 +
                        wmul(flowPressure, 2500 * BPS) +
                        wmul(oneSidedFlow, 2200 * BPS) +
                        wmul(tensionMemory, 4000 * BPS),
                    0,
                    WAD
                )
            )
        );
        uint256 inventoryCenteringOffset = wmul(
            wmul(_max(refillMemory, calmMemory), inventoryGate),
            680 * BPS
        );
        uint256 centerCap = wmul(
            sharedSpread > BASE_FEE ? sharedSpread - BASE_FEE : 0,
            1350 * BPS
        );
        if (inventoryCenteringOffset > centerCap) {
            inventoryCenteringOffset = centerCap;
        }
        if (toxicBidSide) {
            askProtection += directionalBurstFee + oneSidedProtection + inventoryCenteringOffset;
        } else {
            bidProtection += directionalBurstFee + oneSidedProtection + inventoryCenteringOffset;
        }

        uint256 bidOpportunityCut = wmul(bidOpportunitySignal, 8000 * BPS);
        uint256 askOpportunityCut = wmul(askOpportunitySignal, 8000 * BPS);
        uint256 refillOpportunityCut = wmul(refillMemory, gap >= 4 ? 440 * BPS : 260 * BPS);
        if (persistentDrift) {
            refillOpportunityCut = wmul(refillOpportunityCut, 6000 * BPS);
        }
        uint256 safeSideConfidence = _oneMinus(
            clamp(
                wmul(tensionMemory, 4200 * BPS) +
                    wmul(flowPressure, 2200 * BPS) +
                    wmul(hazardMemory, 1800 * BPS),
                0,
                WAD
            )
        );
        if (transientShock) {
            safeSideConfidence = wmul(safeSideConfidence, 7000 * BPS);
        }
        refillOpportunityCut = clamp(
            refillOpportunityCut + wmul(wmul(refillMemory, safeSideConfidence), 220 * BPS),
            0,
            WAD
        );
        if (toxicBidSide) {
            askOpportunityCut += refillOpportunityCut + healingRebate + inventoryCenteringOffset;
        } else {
            bidOpportunityCut += refillOpportunityCut + healingRebate + inventoryCenteringOffset;
        }

        uint256 baselineFlex = sharedSpread > BASE_FEE ? sharedSpread - BASE_FEE : 0;
        bidOpportunityCut = clamp(
            bidOpportunityCut,
            0,
            bidProtection + wmul(baselineFlex, 1200 * BPS)
        );
        askOpportunityCut = clamp(
            askOpportunityCut,
            0,
            askProtection + wmul(baselineFlex, 1200 * BPS)
        );
        bidFee = sharedSpread + bidProtection;
        askFee = sharedSpread + askProtection;
        bidFee = bidFee > bidOpportunityCut ? bidFee - bidOpportunityCut : MIN_FEE;
        askFee = askFee > askOpportunityCut ? askFee - askOpportunityCut : MIN_FEE;

        bidFee = clampFee(bidFee);
        askFee = clampFee(askFee);

        slots[0] = fastAnchor;
        slots[1] = structuralAnchor;
        slots[2] = volMemory;
        slots[3] = buyFlow;
        slots[4] = sellFlow;
        slots[5] = hazardMemory;
        slots[6] = calmMemory;
        slots[7] = currentSpot;
        slots[8] = trade.timestamp;
        slots[9] = tensionMemory;
        slots[10] = flowPressure;
        slots[11] = refillMemory;

        return (bidFee, askFee);
    }

    function getName() external pure override returns (string memory) {
        return "DualAnchorQuoteTopology";
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

    function _share(uint256 part, uint256 total) internal pure returns (uint256) {
        if (total == 0) {
            return WAD / 2;
        }
        return wdiv(part, total);
    }
}
