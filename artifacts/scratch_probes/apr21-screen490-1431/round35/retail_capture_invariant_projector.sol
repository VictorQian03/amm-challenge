// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {AMMStrategyBase} from "./AMMStrategyBase.sol";
import {TradeInfo} from "./IAMMStrategy.sol";

/// @title Retail Capture Invariant Projector
/// @notice Keeps quantile tail ownership, then projects retail-capture stress into one-way side protection before quote assembly.
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

        slots[0] = spot; // latent fair spot
        slots[1] = 0; // realized volatility memory
        slots[2] = 0; // buy-side flow memory
        slots[3] = 0; // sell-side flow memory
        slots[4] = 0; // adverse-selection hazard memory
        slots[5] = 0; // calm / mean-reversion memory
        slots[6] = spot; // last observed spot
        slots[7] = 0; // last timestamp
        slots[8] = 0; // latent divergence memory
        slots[9] = 0; // directional flow pressure memory

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

        uint256 volMemory = wmul(
            slots[1],
            _gapAdjustedDecay(DECAY_VOL, gapShort, 1400 * BPS)
        );
        uint256 buyFlow = wmul(
            slots[2],
            _gapAdjustedDecay(DECAY_FLOW, gapShort, 2200 * BPS)
        );
        uint256 sellFlow = wmul(
            slots[3],
            _gapAdjustedDecay(DECAY_FLOW, gapShort, 2200 * BPS)
        );
        uint256 hazardMemory = wmul(
            slots[4],
            _gapAdjustedDecay(DECAY_HAZARD, gapShort, 1700 * BPS)
        );
        uint256 calmMemory = wmul(
            slots[5],
            _gapAdjustedDecay(DECAY_CALM, gapLong, 700 * BPS)
        );
        uint256 divergenceMemory = wmul(
            slots[8],
            _gapAdjustedDecay(DECAY_DIVERGENCE, gapShort, 1200 * BPS)
        );

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
        uint256 tailSignal = _max(tradeSize, _max(spotJumpVol, divergenceVol));
        uint256 tailBucket = 0;
        if (tailSignal > 22 * BPS) {
            tailBucket = 3;
        } else if (tailSignal > 13 * BPS) {
            tailBucket = 2;
        } else if (tailSignal > 8 * BPS) {
            tailBucket = 1;
        }
        uint256 tailBucketFloor = tailBucket == 0
            ? 0
            : tailBucket == 1
                ? 4 * BPS
                : tailBucket == 2
                    ? 8 * BPS
                    : 13 * BPS;
        uint256 monotoneEvidenceFloor = _max(
            divergenceVol,
            wmul(clusterObservation, 5400 * BPS)
        );
        if (monotoneEvidenceFloor < tailBucketFloor) {
            monotoneEvidenceFloor = tailBucketFloor;
        }
        if (hazardObservation < monotoneEvidenceFloor) {
            hazardObservation = monotoneEvidenceFloor;
        }
        uint256 calmObservation = wmul(
            gapLong,
            _oneMinus(clamp(hazardObservation * 6, 0, WAD))
        );

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
        bool continuationAligned =
            toxicBidSide ? buyFlow >= sellFlow : sellFlow > buyFlow;
        uint256 continuationVeto = 0;
        if (continuationAligned) {
            continuationVeto = clamp(
                wmul(flowPressure, 2800 * BPS) +
                    wmul(oneSidedFlow, 2200 * BPS) +
                    wmul(_max(divergenceMemory, spotJump), 1400 * BPS) +
                    tailBucket * 90 * BPS,
                0,
                4500 * BPS
            );
        }

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
            if (continuationVeto > 0) {
                quietRecenter = wmul(quietRecenter, _oneMinus(continuationVeto));
            }
            latentSpot = _blend(latentSpot, currentSpot, quietRecenter);
        }
        if (gap >= 4) {
            uint256 postRecenterDivergence =
                latentSpot == 0 ? 0 : wdiv(absDiff(currentSpot, latentSpot), latentSpot);
            uint256 reconvergenceGate = _oneMinus(
                clamp(wmul(postRecenterDivergence, 10000 * BPS), 0, WAD)
            );
            uint256 benignGapGate = wmul(gapLong, calmMemory);
            uint256 quietSettle = wmul(wmul(quietGate, reconvergenceGate), benignGapGate);
            divergenceMemory = wmul(
                divergenceMemory,
                _oneMinus(clamp(wmul(quietSettle, 1200 * BPS), 0, WAD))
            );
        }

        uint256 richSignal = 0;
        uint256 cheapSignal = 0;
        if (toxicBidSide) {
            richSignal = divergenceMemory;
        } else {
            cheapSignal = divergenceMemory;
        }

        uint256 sideHazard = hazardMemory + wmul(flowImbalance, _max(volMemory, divergenceMemory));
        sideHazard += wmul(monotoneEvidenceFloor, 950 * BPS);
        if (sideHazard > WAD) {
            sideHazard = WAD;
        }

        uint256 flowDirectionalRisk = 0;
        if (flowPressure > 500 * BPS) {
            uint256 extensionSignal = _max(divergenceMemory, spotJump);
            if (extensionSignal > 3 * BPS) {
                uint256 toxicFlowSignal = flowPressure + wmul(extensionSignal, 2200 * BPS);
                flowDirectionalRisk = wmul(toxicFlowSignal, 320 * BPS);
            }
        }
        uint256 bidFlowRisk = 0;
        uint256 askFlowRisk = 0;
        if (flowDirectionalRisk > 0) {
            if (toxicBidSide) {
                if (buyFlow >= sellFlow) {
                    askFlowRisk = flowDirectionalRisk;
                }
            } else if (sellFlow > buyFlow) {
                bidFlowRisk = flowDirectionalRisk;
            }
        }

        uint256 bidRiskSignal =
            wmul(sellShare, sideHazard) +
            wmul(richSignal, 8500 * BPS) +
            bidFlowRisk;
        uint256 askRiskSignal =
            wmul(buyShare, sideHazard) +
            wmul(cheapSignal, 8500 * BPS) +
            askFlowRisk;

        uint256 captureInvariant = _max(
            monotoneEvidenceFloor,
            _max(wmul(oneSidedFlow, 8200 * BPS), wmul(flowPressure, _max(volMemory, hazardMemory)))
        );
        captureInvariant += wmul(tailBucketFloor, 4000 * BPS);
        if (captureInvariant > WAD) {
            captureInvariant = WAD;
        }
        uint256 adverseProjection = wmul(captureInvariant, 6800 * BPS) +
            wmul(_max(spotJump, divergenceMemory), 2400 * BPS);
        adverseProjection = clamp(adverseProjection, 0, WAD);
        if (toxicBidSide) {
            if (bidRiskSignal < adverseProjection) {
                bidRiskSignal = adverseProjection;
            }
        } else if (askRiskSignal < adverseProjection) {
            askRiskSignal = adverseProjection;
        }

        uint256 sharedSpread =
            BASE_FEE +
            wmul(volMemory, 1650 * BPS) +
            wmul(hazardMemory, 1750 * BPS);

        uint256 eventSignal = volObservation + hazardObservation;
        if (eventSignal > WAD) {
            eventSignal = WAD;
        }
        uint256 eventCarry = wmul(eventSignal, 180 * BPS);
        uint256 directionalBurstFee = 0;
        if (eventSignal > 8 * BPS) {
            uint256 burstSignal = eventSignal - 8 * BPS;
            eventCarry += wmul(burstSignal, 260 * BPS);
            directionalBurstFee = wmul(burstSignal, 1650 * BPS);
        }
        sharedSpread += eventCarry;

        uint256 bidProtection = wmul(bidRiskSignal, 5000 * BPS);
        uint256 askProtection = wmul(askRiskSignal, 5000 * BPS);
        uint256 oneSidedProtection = wmul(oneSidedFlow, 2500 * BPS);
        if (currentSpot >= latentSpot) {
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
        return "RetailCaptureInvariantProjector";
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

    function _share(uint256 part, uint256 total) internal pure returns (uint256) {
        if (total == 0) {
            return WAD / 2;
        }
        return wdiv(part, total);
    }
}
