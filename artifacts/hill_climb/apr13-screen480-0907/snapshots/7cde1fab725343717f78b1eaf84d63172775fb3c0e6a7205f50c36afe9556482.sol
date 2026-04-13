// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {AMMStrategyBase} from "./AMMStrategyBase.sol";
import {TradeInfo} from "./IAMMStrategy.sol";

/// @title Latent State Quote Engine
/// @notice Estimate fair value and market state first, then map state into spread, side risk, and side opportunity.
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
    uint256 internal constant ALPHA_PASSIVE = 18 * BPS;
    uint256 internal constant ROUTER_ALPHA_PROTECT = 1800 * BPS;
    uint256 internal constant ROUTER_ALPHA_RELEASE = 600 * BPS;
    uint256 internal constant ROUTER_PROTECT_DEFAULT = 7800 * BPS;
    uint256 internal constant ROUTER_MIN_PROTECT = 3200 * BPS;

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
        slots[11] = ROUTER_PROTECT_DEFAULT; // protective router weight
        slots[12] = 0; // calm confirmation count

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
        if (currentSpot >= latentSpot) {
            richSignal = divergenceMemory;
        } else {
            cheapSignal = divergenceMemory;
        }

        uint256 sideHazard = hazardMemory + wmul(flowImbalance, _max(volMemory, divergenceMemory));
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
            if (currentSpot >= latentSpot) {
                if (buyFlow >= sellFlow) {
                    askFlowRisk = flowDirectionalRisk;
                }
            } else if (sellFlow > buyFlow) {
                bidFlowRisk = flowDirectionalRisk;
            }
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
            bidFlowRisk;
        uint256 askRiskSignal =
            wmul(buyShare, sideHazard) +
            wmul(cheapSignal, 8500 * BPS) +
            askFlowRisk;

        uint256 opportunityGate = wmul(
            calmMemory,
            _oneMinus(clamp(hazardMemory * 8, 0, WAD))
        );
        uint256 bidOpportunitySignal = wmul(opportunityGate, cheapSignal);
        uint256 askOpportunitySignal = wmul(opportunityGate, richSignal);

        uint256 sharedSpread =
            BASE_FEE +
            wmul(volMemory, 1800 * BPS) +
            wmul(hazardMemory, 2400 * BPS) +
            wmul(divergenceMemory, 650 * BPS) +
            wmul(oneSidedFlow, 1700 * BPS);

        uint256 eventSignal = volObservation + hazardObservation;
        if (eventSignal > WAD) {
            eventSignal = WAD;
        }
        uint256 eventCarry = wmul(eventSignal, 390 * BPS);
        uint256 directionalBurstFee = 0;
        if (eventSignal > 8 * BPS) {
            uint256 burstSignal = eventSignal - 8 * BPS;
            eventCarry += wmul(burstSignal, 800 * BPS);
            directionalBurstFee = wmul(burstSignal, 1050 * BPS);
        }
        uint256 calmConfirmations = slots[12];
        bool benignGap =
            gap >= 2 &&
            quietGate > 6200 * BPS &&
            hazardMemory < 1100 * BPS &&
            flowPressure < 700 * BPS &&
            eventSignal < 18 * BPS;
        if (benignGap) {
            calmConfirmations = calmConfirmations < 3 ? calmConfirmations + 1 : 3;
        } else if (
            eventSignal > 24 * BPS ||
            hazardMemory > 1400 * BPS ||
            flowPressure > 900 * BPS
        ) {
            calmConfirmations = 0;
        } else if (calmConfirmations > 0 && gap == 0) {
            calmConfirmations -= 1;
        }

        uint256 competeConfirmationBonus = calmConfirmations >= 2
            ? 1600 * BPS
            : calmConfirmations == 1 ? 500 * BPS : 0;
        uint256 maxFlowRisk = _max(bidFlowRisk, askFlowRisk);
        uint256 protectSignal = clamp(
            wmul(hazardMemory, 4600 * BPS) +
                wmul(volMemory, 2200 * BPS) +
                wmul(flowPressure, 1800 * BPS) +
                wmul(oneSidedFlow, 2000 * BPS) +
                wmul(divergenceMemory, 1200 * BPS) +
                wmul(eventSignal, 900 * BPS) +
                wmul(maxFlowRisk, 7000 * BPS),
            0,
            WAD
        );
        uint256 competeSignal = clamp(
            wmul(calmMemory, 2600 * BPS) +
                wmul(quietGate, 1800 * BPS) +
                wmul(passiveRecaptureMemory, 2000 * BPS) +
                wmul(gapLong, 1000 * BPS) +
                competeConfirmationBonus,
            0,
            WAD
        );
        uint256 routerTarget = ROUTER_PROTECT_DEFAULT;
        if (calmConfirmations >= 2 && competeSignal > protectSignal) {
            uint256 routerRelease =
                1400 * BPS + wmul(competeSignal - protectSignal, 4200 * BPS);
            routerTarget = routerTarget > routerRelease
                ? routerTarget - routerRelease
                : ROUTER_MIN_PROTECT;
            if (routerTarget < ROUTER_MIN_PROTECT) {
                routerTarget = ROUTER_MIN_PROTECT;
            }
        } else {
            routerTarget = clamp(
                routerTarget + wmul(protectSignal, 1800 * BPS),
                ROUTER_PROTECT_DEFAULT,
                WAD
            );
        }
        uint256 routerAlpha = routerTarget > slots[11]
            ? ROUTER_ALPHA_PROTECT
            : ROUTER_ALPHA_RELEASE;
        uint256 routerScore = _blend(slots[11], routerTarget, routerAlpha);
        uint256 modeBlend = clamp(
            5500 * BPS + wmul(routerScore, 4500 * BPS),
            5500 * BPS,
            WAD
        );

        sharedSpread += eventCarry;

        uint256 protectiveSpread = sharedSpread;
        uint256 protectiveRebate = wmul(calmMemory, 300 * BPS);
        protectiveSpread = protectiveSpread > protectiveRebate
            ? protectiveSpread - protectiveRebate
            : MIN_FEE;

        uint256 protectiveBidFee =
            protectiveSpread +
            wmul(bidRiskSignal, 4800 * BPS);
        uint256 protectiveAskFee =
            protectiveSpread +
            wmul(askRiskSignal, 4800 * BPS);
        uint256 healingRebate = wmul(directionalBurstFee, 5000 * BPS);
        if (currentSpot >= latentSpot) {
            protectiveBidFee += directionalBurstFee;
            protectiveAskFee = protectiveAskFee > healingRebate ? protectiveAskFee - healingRebate : MIN_FEE;
        } else {
            protectiveAskFee += directionalBurstFee;
            protectiveBidFee = protectiveBidFee > healingRebate ? protectiveBidFee - healingRebate : MIN_FEE;
        }

        uint256 bidOpportunityCut = wmul(bidOpportunitySignal, 8200 * BPS);
        uint256 askOpportunityCut = wmul(askOpportunitySignal, 8200 * BPS);
        uint256 passiveRecaptureCut = wmul(passiveRecaptureMemory, 1550 * BPS);
        uint256 calmDivergenceBonus = 0;
        if (hazardMemory < 1100 * BPS && flowPressure < 650 * BPS && gap >= 2) {
            calmDivergenceBonus = wmul(divergenceMemory, gap >= 4 ? 650 * BPS : 400 * BPS);
        }
        if (currentSpot >= latentSpot) {
            askOpportunityCut += passiveRecaptureCut + calmDivergenceBonus;
        } else {
            bidOpportunityCut += passiveRecaptureCut + calmDivergenceBonus;
        }
        protectiveBidFee = protectiveBidFee > bidOpportunityCut ? protectiveBidFee - bidOpportunityCut : MIN_FEE;
        protectiveAskFee = protectiveAskFee > askOpportunityCut ? protectiveAskFee - askOpportunityCut : MIN_FEE;

        uint256 competitiveSpread = protectiveSpread;
        uint256 competitiveSpreadTrim =
            wmul(eventCarry, 6500 * BPS) +
            wmul(calmMemory, 140 * BPS) +
            wmul(passiveRecaptureMemory, 160 * BPS);
        if (calmConfirmations >= 2) {
            competitiveSpreadTrim += wmul(quietGate, 90 * BPS);
        }
        competitiveSpreadTrim = clamp(competitiveSpreadTrim, 0, 12 * BPS);
        competitiveSpread = competitiveSpread > competitiveSpreadTrim
            ? competitiveSpread - competitiveSpreadTrim
            : MIN_FEE;

        uint256 competitiveBidFee =
            competitiveSpread +
            wmul(bidRiskSignal, 4200 * BPS);
        uint256 competitiveAskFee =
            competitiveSpread +
            wmul(askRiskSignal, 4200 * BPS);
        uint256 competitiveDirectionalTilt = wmul(directionalBurstFee, 2500 * BPS);
        uint256 competitiveHealing = wmul(competitiveDirectionalTilt, 4500 * BPS);
        if (currentSpot >= latentSpot) {
            competitiveBidFee += competitiveDirectionalTilt;
            competitiveAskFee = competitiveAskFee > competitiveHealing
                ? competitiveAskFee - competitiveHealing
                : MIN_FEE;
        } else {
            competitiveAskFee += competitiveDirectionalTilt;
            competitiveBidFee = competitiveBidFee > competitiveHealing
                ? competitiveBidFee - competitiveHealing
                : MIN_FEE;
        }

        uint256 competitiveBidCut = wmul(bidOpportunitySignal, 7000 * BPS);
        uint256 competitiveAskCut = wmul(askOpportunitySignal, 7000 * BPS);
        uint256 competitivePassiveCut = wmul(passiveRecaptureMemory, 900 * BPS);
        uint256 competitiveCalmBonus = 0;
        if (hazardMemory < 1000 * BPS && flowPressure < 650 * BPS && gap >= 2) {
            competitiveCalmBonus = wmul(divergenceMemory, gap >= 4 ? 400 * BPS : 250 * BPS);
        }
        if (currentSpot >= latentSpot) {
            competitiveAskCut += competitivePassiveCut + competitiveCalmBonus;
        } else {
            competitiveBidCut += competitivePassiveCut + competitiveCalmBonus;
        }
        competitiveBidFee = competitiveBidFee > competitiveBidCut ? competitiveBidFee - competitiveBidCut : MIN_FEE;
        competitiveAskFee = competitiveAskFee > competitiveAskCut ? competitiveAskFee - competitiveAskCut : MIN_FEE;

        bidFee = clampFee(_blend(competitiveBidFee, protectiveBidFee, modeBlend));
        askFee = clampFee(_blend(competitiveAskFee, protectiveAskFee, modeBlend));

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
        slots[11] = routerScore;
        slots[12] = calmConfirmations;

        return (bidFee, askFee);
    }

    function getName() external pure override returns (string memory) {
        return "LatentStateQuoteEngine";
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
