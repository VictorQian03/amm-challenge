// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {AMMStrategyBase} from "./AMMStrategyBase.sol";
import {TradeInfo} from "./IAMMStrategy.sol";

/// @title Directional Adverse Mass Splitter
/// @notice Splits adverse event mass from benign volume before assigning side holds.
contract Strategy is AMMStrategyBase {
    uint256 internal constant BASE_FEE = 16 * BPS;

    uint256 internal constant DECAY_VOL = 9000 * BPS;
    uint256 internal constant DECAY_FLOW = 8700 * BPS;
    uint256 internal constant DECAY_HAZARD = 8900 * BPS;
    uint256 internal constant DECAY_CALM = 9300 * BPS;
    uint256 internal constant DECAY_DIVERGENCE = 9150 * BPS;
    uint256 internal constant DECAY_MASS = 9050 * BPS;

    uint256 internal constant ALPHA_SPOT = 12 * BPS;
    uint256 internal constant ALPHA_VOL = 26 * BPS;
    uint256 internal constant ALPHA_HAZARD = 30 * BPS;
    uint256 internal constant ALPHA_CALM = 14 * BPS;
    uint256 internal constant ALPHA_DIVERGENCE = 22 * BPS;
    uint256 internal constant ALPHA_FLOW = 18 * BPS;
    uint256 internal constant ALPHA_PASSIVE = 18 * BPS;
    uint256 internal constant ALPHA_MASS = 24 * BPS;

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
        slots[10] = 0; // passive recapture memory
        slots[11] = 0; // adverse event mass memory
        slots[12] = 0; // benign volume memory

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
        bool priceMoveUp = currentSpot >= lastSpot;
        bool weaklyInconsistentEvent =
            lastSpot != 0 && ((trade.isBuy && !priceMoveUp) || (!trade.isBuy && priceMoveUp));

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
        uint256 adverseMassMemory = wmul(
            slots[11],
            _gapAdjustedDecay(DECAY_MASS, gapShort, 1500 * BPS)
        );
        uint256 benignVolumeMemory = wmul(
            slots[12],
            _gapAdjustedDecay(DECAY_MASS, gapLong, 800 * BPS)
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
        uint256 feasibilityResidual = 0;
        if (weaklyInconsistentEvent) {
            feasibilityResidual = clamp(
                wmul(_max(spotJump, divergence), 5200 * BPS) +
                    wmul(tradeSize, 1700 * BPS),
                0,
                10 * BPS
            );
            hazardObservation = clamp(hazardObservation + feasibilityResidual, 0, WAD);
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
        uint256 adverseMassObservation = 0;
        if (weaklyInconsistentEvent && continuationAligned) {
            adverseMassObservation = _max(
                feasibilityResidual,
                wmul(_max(monotoneEvidenceFloor, tailSignal), 6200 * BPS)
            );
            adverseMassObservation = clamp(
                adverseMassObservation + wmul(oneSidedFlow, 1800 * BPS),
                0,
                WAD
            );
        } else if (weaklyInconsistentEvent) {
            adverseMassObservation = clamp(
                wmul(feasibilityResidual, 7200 * BPS) + wmul(monotoneEvidenceFloor, 2800 * BPS),
                0,
                WAD
            );
        }
        uint256 benignVolumeObservation = 0;
        if (!weaklyInconsistentEvent) {
            uint256 benignCalmGate = wmul(gapLong, calmMemory);
            benignVolumeObservation = wmul(
                tradeSize + wmul(volObservation, 1800 * BPS),
                _oneMinus(clamp(hazardObservation * 5 + wmul(flowImbalance, 1800 * BPS), 0, WAD))
            );
            benignVolumeObservation = clamp(
                benignVolumeObservation + wmul(benignCalmGate, 2400 * BPS),
                0,
                WAD
            );
        }
        adverseMassMemory = _blend(adverseMassMemory, adverseMassObservation, ALPHA_MASS);
        benignVolumeMemory = _blend(benignVolumeMemory, benignVolumeObservation, ALPHA_MASS);
        bool adverseMassDominates = adverseMassMemory > benignVolumeMemory;
        bool adverseEventAgreement = weaklyInconsistentEvent && adverseMassDominates;
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
        uint256 counterflowRelease = 0;
        if (!continuationAligned && gap >= 4) {
            counterflowRelease = clamp(
                wmul(calmMemory, 1200 * BPS) +
                    wmul(gapLong, 600 * BPS),
                0,
                1800 * BPS
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
            } else if (counterflowRelease > 0) {
                quietRecenter = clamp(
                    quietRecenter + wmul(quietRecenter, counterflowRelease),
                    0,
                    WAD
                );
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
            uint256 quietRelease = wmul(wmul(quietGate, reconvergenceGate), benignGapGate);
            divergenceMemory = wmul(
                divergenceMemory,
                _oneMinus(clamp(wmul(quietRelease, 1200 * BPS), 0, WAD))
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
        sideHazard +=
            wmul(monotoneEvidenceFloor, 850 * BPS) +
            wmul(feasibilityResidual, 1100 * BPS) +
            wmul(adverseMassMemory, 1250 * BPS);
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
        uint256 adverseBidLabel = 0;
        uint256 adverseAskLabel = 0;
        uint256 benignBidLabel = 0;
        uint256 benignAskLabel = 0;
        if (toxicBidSide) {
            adverseAskLabel = adverseMassMemory;
            benignBidLabel = benignVolumeMemory;
        } else {
            adverseBidLabel = adverseMassMemory;
            benignAskLabel = benignVolumeMemory;
        }
        if (buyFlow > sellFlow) {
            adverseAskLabel = _max(adverseAskLabel, wmul(adverseMassMemory, buyShare));
            benignAskLabel = _max(benignAskLabel, wmul(benignVolumeMemory, sellShare));
        } else {
            adverseBidLabel = _max(adverseBidLabel, wmul(adverseMassMemory, sellShare));
            benignBidLabel = _max(benignBidLabel, wmul(benignVolumeMemory, buyShare));
        }

        uint256 passiveRecaptureObservation = wmul(
            gapLong,
            _oneMinus(
                clamp(
                    wmul(flowPressure, 3000 * BPS) +
                        wmul(divergence, 4500 * BPS),
                    0,
                    WAD
                )
            )
        );
        if (gap >= 4) {
            uint256 passiveRecenterDivergence =
                latentSpot == 0 ? 0 : wdiv(absDiff(currentSpot, latentSpot), latentSpot);
            uint256 passiveRecenterGate = _oneMinus(
                clamp(wmul(passiveRecenterDivergence, 10000 * BPS), 0, WAD)
            );
            passiveRecaptureObservation = wmul(
                passiveRecaptureObservation,
                wmul(quietGate, passiveRecenterGate)
            );
        }
        uint256 passiveRecaptureMemory = _blend(slots[10], passiveRecaptureObservation, ALPHA_PASSIVE);
        if (gap >= 4) {
            passiveRecaptureMemory = wmul(passiveRecaptureMemory, 9600 * BPS);
        } else if (gap >= 2) {
            passiveRecaptureMemory = wmul(passiveRecaptureMemory, 9000 * BPS);
        }

        uint256 bidRiskSignal =
            wmul(sellShare, sideHazard) +
            wmul(richSignal, 8500 * BPS) +
            bidFlowRisk +
            wmul(adverseBidLabel, 1500 * BPS);
        uint256 askRiskSignal =
            wmul(buyShare, sideHazard) +
            wmul(cheapSignal, 8500 * BPS) +
            askFlowRisk +
            wmul(adverseAskLabel, 1500 * BPS);

        uint256 sharedSpread =
            BASE_FEE +
            wmul(volMemory, 1800 * BPS) +
            wmul(hazardMemory, 1900 * BPS);

        uint256 eventSignal = volObservation + hazardObservation;
        if (eventSignal > WAD) {
            eventSignal = WAD;
        }
        uint256 eventCarry = wmul(eventSignal, 220 * BPS);
        uint256 directionalBurstFee = 0;
        if (eventSignal > 8 * BPS) {
            uint256 burstSignal = eventSignal - 8 * BPS;
            eventCarry += wmul(burstSignal, 300 * BPS);
            directionalBurstFee = wmul(burstSignal, 1850 * BPS);
        }
        sharedSpread += eventCarry;

        uint256 sharedRebate = wmul(wmul(calmMemory, quietGate), 110 * BPS);
        sharedSpread = sharedSpread > sharedRebate ? sharedSpread - sharedRebate : MIN_FEE;
        uint256 bidProtection = wmul(bidRiskSignal, 5400 * BPS);
        uint256 askProtection = wmul(askRiskSignal, 5400 * BPS);
        uint256 tailProtectionCap = tailBucket == 0
            ? 11 * BPS
            : tailBucket == 1
                ? 17 * BPS
                : tailBucket == 2
                    ? 26 * BPS
                    : 38 * BPS;
        if (bidProtection > tailProtectionCap) {
            bidProtection = tailProtectionCap;
        }
        if (askProtection > tailProtectionCap) {
            askProtection = tailProtectionCap;
        }
        uint256 oneSidedProtection = wmul(oneSidedFlow, 2800 * BPS);
        uint256 healingRebate = wmul(directionalBurstFee, 2800 * BPS);
        uint256 agreedAdverseHold = 0;
        if (adverseEventAgreement) {
            agreedAdverseHold = clamp(
                wmul(adverseMassMemory - benignVolumeMemory, 3600 * BPS) +
                    wmul(feasibilityResidual, 5200 * BPS),
                0,
                tailProtectionCap
            );
        }
        if (currentSpot >= latentSpot) {
            bidProtection += directionalBurstFee + oneSidedProtection;
            askProtection += agreedAdverseHold;
        } else {
            askProtection += directionalBurstFee + oneSidedProtection;
            bidProtection += agreedAdverseHold;
        }

        uint256 bidBenignVolumeCut = wmul(benignBidLabel, 4200 * BPS);
        uint256 askBenignVolumeCut = wmul(benignAskLabel, 4200 * BPS);
        uint256 passiveRecaptureCut = wmul(passiveRecaptureMemory, 1550 * BPS);
        uint256 calmDivergenceBonus = 0;
        if (hazardMemory < 1100 * BPS && flowPressure < 650 * BPS && gap >= 2) {
            calmDivergenceBonus = wmul(divergenceMemory, gap >= 4 ? 650 * BPS : 400 * BPS);
        }
        // Allow a small extra safe-side refill only after repeated calm confirmations.
        uint256 refillCalmConfirmation = passiveRecaptureMemory;
        if (gap >= 4) {
            refillCalmConfirmation = clamp(
                refillCalmConfirmation + wmul(calmMemory, 2200 * BPS),
                0,
                WAD
            );
        } else if (gap >= 2) {
            refillCalmConfirmation = wmul(
                clamp(
                    refillCalmConfirmation + wmul(calmMemory, 1200 * BPS),
                    0,
                    WAD
                ),
                7000 * BPS
            );
        } else {
            refillCalmConfirmation = 0;
        }
        uint256 refillRiskGate = _oneMinus(
            clamp(
                hazardMemory * 8 +
                    wmul(flowPressure, 3200 * BPS) +
                    wmul(oneSidedFlow, 2600 * BPS) +
                    wmul(divergenceMemory, 5200 * BPS),
                0,
                WAD
            )
        );
        uint256 refillAuctionBudget = wmul(
            wmul(refillCalmConfirmation, quietGate),
            refillRiskGate
        );
        refillAuctionBudget = wmul(
            refillAuctionBudget,
            _oneMinus(clamp(wmul(flowImbalance, 4500 * BPS), 0, WAD))
        );
        uint256 refillAuctionCut =
            wmul(refillAuctionBudget, gap >= 4 ? 420 * BPS : 260 * BPS) +
            wmul(wmul(refillAuctionBudget, passiveRecaptureMemory), 220 * BPS);
        if (toxicBidSide) {
            askBenignVolumeCut += passiveRecaptureCut + calmDivergenceBonus + healingRebate;
            askBenignVolumeCut += refillAuctionCut;
        } else {
            bidBenignVolumeCut += passiveRecaptureCut + calmDivergenceBonus + healingRebate;
            bidBenignVolumeCut += refillAuctionCut;
        }
        uint256 baselineFlex = sharedSpread > BASE_FEE ? sharedSpread - BASE_FEE : 0;
        bidBenignVolumeCut = clamp(
            bidBenignVolumeCut,
            0,
            bidProtection + wmul(baselineFlex, 1200 * BPS)
        );
        askBenignVolumeCut = clamp(
            askBenignVolumeCut,
            0,
            askProtection + wmul(baselineFlex, 1200 * BPS)
        );
        bidFee = sharedSpread + bidProtection;
        askFee = sharedSpread + askProtection;
        bidFee = bidFee > bidBenignVolumeCut ? bidFee - bidBenignVolumeCut : MIN_FEE;
        askFee = askFee > askBenignVolumeCut ? askFee - askBenignVolumeCut : MIN_FEE;

        bidFee = clampFee(bidFee);
        askFee = clampFee(askFee);

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
        slots[10] = passiveRecaptureMemory;
        slots[11] = adverseMassMemory;
        slots[12] = benignVolumeMemory;

        return (bidFee, askFee);
    }

    function getName() external pure override returns (string memory) {
        return "DirectionalAdverseMassSplitter";
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
