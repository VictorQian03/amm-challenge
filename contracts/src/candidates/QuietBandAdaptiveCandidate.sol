// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {AMMStrategyBase} from "./AMMStrategyBase.sol";
import {TradeInfo} from "./IAMMStrategy.sol";

/// @title Quiet Band Adaptive Candidate
/// @notice Low-resting-fee strategy with modest shock spikes and faster quiet-gap release.
contract Strategy is AMMStrategyBase {
    uint256 internal constant BASE_FEE = 37 * BPS;
    uint256 internal constant DECAY_FAST = 8600 * BPS;
    uint256 internal constant DECAY_SLOW = 9300 * BPS;
    uint256 internal constant DECAY_COOLDOWN = 8800 * BPS;
    uint256 internal constant ALPHA_SPOT = 10 * BPS;
    uint256 internal constant ALPHA_INTENSITY = 12 * BPS;

    function afterInitialize(uint256 initialX, uint256 initialY)
        external
        override
        returns (uint256 bidFee, uint256 askFee)
    {
        uint256 spot = wdiv(initialY, initialX);

        slots[0] = 0; // bid pressure
        slots[1] = 0; // ask pressure
        slots[2] = 0; // cooldown
        slots[3] = 0; // size memory
        slots[4] = 0; // intensity memory
        slots[5] = 0; // last side: 0 none, 1 buy, 2 sell
        slots[6] = 0; // last timestamp
        slots[7] = spot; // latent spot estimate

        return (BASE_FEE, BASE_FEE);
    }

    function afterSwap(TradeInfo calldata trade)
        external
        override
        returns (uint256 bidFee, uint256 askFee)
    {
        uint256 spot = wdiv(trade.reserveY, trade.reserveX);
        uint256 latentSpot = _blend(slots[7], spot, ALPHA_SPOT);
        uint256 lastTimestamp = slots[6];
        uint256 gap = trade.timestamp > lastTimestamp ? trade.timestamp - lastTimestamp : 0;

        uint256 sizeX = wdiv(trade.amountX, trade.reserveX);
        uint256 sizeY = wdiv(trade.amountY, trade.reserveY);
        uint256 tradeSize = sizeX > sizeY ? sizeX : sizeY;

        uint256 lastSpot = slots[7];
        uint256 spotJump = lastSpot == 0 ? 0 : wdiv(absDiff(spot, lastSpot), lastSpot);
        uint256 latentGap = latentSpot == 0 ? 0 : wdiv(absDiff(spot, latentSpot), latentSpot);

        uint256 intensity = tradeSize > spotJump ? tradeSize : spotJump;
        if (latentGap > intensity) {
            intensity = latentGap;
        }
        if (tradeSize > 8 * BPS) {
            intensity += wmul(tradeSize, 1400 * BPS);
        } else if (tradeSize > 3 * BPS) {
            intensity += wmul(tradeSize, 900 * BPS);
        }

        uint256 bidPressure = wmul(slots[0], DECAY_FAST);
        uint256 askPressure = wmul(slots[1], DECAY_FAST);
        uint256 cooldown = wmul(slots[2], DECAY_COOLDOWN);
        uint256 sizeMemory = wmul(slots[3], DECAY_SLOW);
        uint256 intensityMemory = _blend(wmul(slots[4], DECAY_SLOW), intensity, ALPHA_INTENSITY);

        if (gap >= 4) {
            bidPressure = wmul(bidPressure, 7200 * BPS);
            askPressure = wmul(askPressure, 7200 * BPS);
            cooldown = wmul(cooldown, 6800 * BPS);
            sizeMemory = wmul(sizeMemory, 7800 * BPS);
            intensityMemory = wmul(intensityMemory, 8400 * BPS);
        } else if (gap >= 2) {
            bidPressure = wmul(bidPressure, 8600 * BPS);
            askPressure = wmul(askPressure, 8600 * BPS);
            cooldown = wmul(cooldown, 8800 * BPS);
            sizeMemory = wmul(sizeMemory, 9100 * BPS);
            intensityMemory = wmul(intensityMemory, 9200 * BPS);
        }

        cooldown = clamp(cooldown + wmul(intensity, 1200 * BPS), MIN_FEE, WAD);
        if (sizeMemory < tradeSize) {
            sizeMemory = tradeSize;
        }

        if (trade.isBuy) {
            bidPressure = clamp(bidPressure + wmul(intensity, 1500 * BPS), MIN_FEE, WAD);
            askPressure = clamp(askPressure + wmul(intensity, 650 * BPS), MIN_FEE, WAD);
        } else {
            askPressure = clamp(askPressure + wmul(intensity, 1500 * BPS), MIN_FEE, WAD);
            bidPressure = clamp(bidPressure + wmul(intensity, 650 * BPS), MIN_FEE, WAD);
        }

        uint256 common = clampFee(
            BASE_FEE +
                wmul(cooldown, 1800 * BPS) +
                wmul(sizeMemory, 550 * BPS) +
                wmul(intensityMemory, 350 * BPS)
        );

        bidFee =
            common +
            wmul(bidPressure, 1900 * BPS) +
            wmul(intensity, trade.isBuy ? 1400 * BPS : 500 * BPS);
        askFee =
            common +
            wmul(askPressure, 1900 * BPS) +
            wmul(intensity, trade.isBuy ? 500 * BPS : 1400 * BPS);

        if (spot >= latentSpot) {
            bidFee += wmul(latentGap, 700 * BPS);
        } else {
            askFee += wmul(latentGap, 700 * BPS);
        }

        uint256 quietRelease = 0;
        if (gap >= 5 && cooldown < 6 * BPS) {
            quietRelease = 5 * BPS;
        } else if (gap >= 3 && cooldown < 8 * BPS) {
            quietRelease = 3 * BPS;
        }

        if (trade.isBuy) {
            if (slots[5] == 1 && bidFee > BPS) {
                bidFee -= BPS;
            }
            if (askFee > quietRelease) {
                askFee -= quietRelease;
            }
            slots[5] = 1;
        } else {
            if (slots[5] == 2 && askFee > BPS) {
                askFee -= BPS;
            }
            if (bidFee > quietRelease) {
                bidFee -= quietRelease;
            }
            slots[5] = 2;
        }

        if (gap >= 4 && cooldown < 5 * BPS) {
            bidFee = bidFee > 2 * BPS ? bidFee - 2 * BPS : MIN_FEE;
            askFee = askFee > 2 * BPS ? askFee - 2 * BPS : MIN_FEE;
        }

        bidFee = clampFee(bidFee);
        askFee = clampFee(askFee);

        slots[0] = bidPressure;
        slots[1] = askPressure;
        slots[2] = cooldown;
        slots[3] = sizeMemory;
        slots[4] = intensityMemory;
        slots[6] = trade.timestamp;
        slots[7] = latentSpot;

        return (bidFee, askFee);
    }

    function getName() external pure override returns (string memory) {
        return "QuietBandAdaptive";
    }

    function _blend(uint256 prev, uint256 sample, uint256 alpha) internal pure returns (uint256) {
        return wmul(prev, WAD - alpha) + wmul(sample, alpha);
    }
}
