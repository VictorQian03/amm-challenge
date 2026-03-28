// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {AMMStrategyBase} from "./AMMStrategyBase.sol";
import {TradeInfo} from "./IAMMStrategy.sol";

/// @title Latent State Fast Recovery Candidate
/// @notice Keeps the latent-state shock response, but decays back to baseline faster after quiet gaps.
contract Strategy is AMMStrategyBase {
    uint256 internal constant BASE_FEE = 66 * BPS;
    uint256 internal constant DECAY_FAST = 8200 * BPS;
    uint256 internal constant DECAY_SLOW = 8800 * BPS;
    uint256 internal constant DECAY_COOLDOWN = 8600 * BPS;
    uint256 internal constant ALPHA_SPOT = 14 * BPS;
    uint256 internal constant ALPHA_INTENSITY = 16 * BPS;

    function afterInitialize(uint256 initialX, uint256 initialY)
        external
        override
        returns (uint256 bidFee, uint256 askFee)
    {
        uint256 spot = wdiv(initialY, initialX);

        slots[0] = spot; // latent spot estimate
        slots[1] = 0; // intensity memory
        slots[2] = 0; // bid-side pressure
        slots[3] = 0; // ask-side pressure
        slots[4] = 0; // cooldown memory
        slots[5] = 0; // size memory
        slots[6] = 0; // last side: 0 sell, 1 buy
        slots[7] = spot; // last observed spot
        slots[8] = 0; // last timestamp

        return (BASE_FEE, BASE_FEE);
    }

    function afterSwap(TradeInfo calldata trade)
        external
        override
        returns (uint256 bidFee, uint256 askFee)
    {
        uint256 spot = wdiv(trade.reserveY, trade.reserveX);
        uint256 lastSpot = slots[7];
        uint256 lastTimestamp = slots[8];
        uint256 latentSpot = _blend(slots[0], spot, ALPHA_SPOT);
        uint256 intensity = _tradeIntensity(trade);
        uint256 intensityMemory = _blend(slots[1], intensity, ALPHA_INTENSITY);

        uint256 sizeX = wdiv(trade.amountX, trade.reserveX);
        uint256 sizeY = wdiv(trade.amountY, trade.reserveY);
        uint256 tradeSize = sizeX > sizeY ? sizeX : sizeY;

        uint256 gap = trade.timestamp > lastTimestamp ? trade.timestamp - lastTimestamp : 0;
        uint256 spotJump = lastSpot == 0 ? 0 : wdiv(absDiff(spot, lastSpot), lastSpot);
        uint256 latentGap = latentSpot == 0 ? 0 : wdiv(absDiff(spot, latentSpot), latentSpot);
        uint256 shock = tradeSize > spotJump ? tradeSize : spotJump;
        if (latentGap > shock) {
            shock = latentGap;
        }

        if (tradeSize > 10 * BPS) {
            shock += wmul(tradeSize, 2100 * BPS);
        } else if (tradeSize > 4 * BPS) {
            shock += wmul(tradeSize, 1300 * BPS);
        }

        uint256 cooldown = wmul(slots[4], DECAY_COOLDOWN);
        uint256 sizeMemory = wmul(slots[5], DECAY_SLOW);
        uint256 bidPressure = wmul(slots[2], DECAY_FAST);
        uint256 askPressure = wmul(slots[3], DECAY_FAST);

        if (gap > 3) {
            cooldown = wmul(cooldown, 7800 * BPS);
            sizeMemory = wmul(sizeMemory, 7800 * BPS);
            bidPressure = wmul(bidPressure, 7600 * BPS);
            askPressure = wmul(askPressure, 7600 * BPS);
            intensityMemory = wmul(intensityMemory, 8200 * BPS);
        } else if (gap > 1) {
            cooldown = wmul(cooldown, 9000 * BPS);
            sizeMemory = wmul(sizeMemory, 8600 * BPS);
            bidPressure = wmul(bidPressure, 8400 * BPS);
            askPressure = wmul(askPressure, 8400 * BPS);
            intensityMemory = wmul(intensityMemory, 9000 * BPS);
        }

        cooldown = clamp(cooldown + wmul(shock, 1450 * BPS), 0, WAD);
        if (sizeMemory < tradeSize) {
            sizeMemory = tradeSize;
        }

        if (trade.isBuy) {
            bidPressure = clamp(
                bidPressure + wmul(shock, 1600 * BPS) + wmul(latentGap, 850 * BPS),
                0,
                WAD
            );
            askPressure = clamp(
                askPressure + wmul(shock, 700 * BPS) + wmul(intensityMemory, 350 * BPS),
                0,
                WAD
            );
        } else {
            askPressure = clamp(
                askPressure + wmul(shock, 1600 * BPS) + wmul(latentGap, 850 * BPS),
                0,
                WAD
            );
            bidPressure = clamp(
                bidPressure + wmul(shock, 700 * BPS) + wmul(intensityMemory, 350 * BPS),
                0,
                WAD
            );
        }

        uint256 common = BASE_FEE;
        common = clampFee(
            common +
                wmul(cooldown, 2000 * BPS) +
                wmul(sizeMemory, 650 * BPS) +
                wmul(intensityMemory, 550 * BPS)
        );

        bidFee =
            common +
            wmul(bidPressure, 2200 * BPS) +
            wmul(shock, trade.isBuy ? 1800 * BPS : 600 * BPS);
        askFee =
            common +
            wmul(askPressure, 2200 * BPS) +
            wmul(shock, trade.isBuy ? 600 * BPS : 1800 * BPS);

        if (spot >= latentSpot) {
            bidFee += wmul(latentGap, 1050 * BPS);
        } else {
            askFee += wmul(latentGap, 1050 * BPS);
        }

        uint256 recapture = 0;
        if (cooldown < 7 * BPS) {
            recapture = gap > 3 ? 6 * BPS : 4 * BPS;
        }

        if (trade.isBuy) {
            if (slots[6] == 1) {
                bidFee = clampFee(bidFee + BPS);
            }
            if (askFee > recapture) {
                askFee -= recapture;
            }
            slots[6] = 1;
        } else {
            if (slots[6] == 0) {
                askFee = clampFee(askFee + BPS);
            }
            if (bidFee > recapture) {
                bidFee -= recapture;
            }
            slots[6] = 0;
        }

        bidFee = clampFee(bidFee);
        askFee = clampFee(askFee);

        slots[0] = latentSpot;
        slots[1] = intensityMemory;
        slots[2] = bidPressure;
        slots[3] = askPressure;
        slots[4] = cooldown;
        slots[5] = sizeMemory;
        slots[7] = spot;
        slots[8] = trade.timestamp;

        return (bidFee, askFee);
    }

    function getName() external pure override returns (string memory) {
        return "LatentStateFastRecovery";
    }

    function _tradeIntensity(TradeInfo calldata trade) internal pure returns (uint256) {
        uint256 sizeX = wdiv(trade.amountX, trade.reserveX);
        uint256 sizeY = wdiv(trade.amountY, trade.reserveY);
        return sizeX > sizeY ? sizeX : sizeY;
    }

    function _blend(uint256 prev, uint256 sample, uint256 alpha) internal pure returns (uint256) {
        return wmul(prev, WAD - alpha) + wmul(sample, alpha);
    }
}
