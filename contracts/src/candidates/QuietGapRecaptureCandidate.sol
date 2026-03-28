// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {AMMStrategyBase} from "./AMMStrategyBase.sol";
import {TradeInfo} from "./IAMMStrategy.sol";

/// @title Quiet Gap Recapture Candidate
/// @notice Lower resting fees with stronger quiet-gap rebates and sharper asymmetry on recapture.
contract Strategy is AMMStrategyBase {
    uint256 internal constant BASE_FEE = 36 * BPS;
    uint256 internal constant DECAY_FAST = 8200 * BPS;
    uint256 internal constant DECAY_SLOW = 9000 * BPS;
    uint256 internal constant DECAY_COOLDOWN = 8600 * BPS;
    uint256 internal constant ALPHA_SPOT = 10 * BPS;
    uint256 internal constant ALPHA_INTENSITY = 14 * BPS;

    function afterInitialize(uint256 initialX, uint256 initialY)
        external
        override
        returns (uint256 bidFee, uint256 askFee)
    {
        uint256 spot = wdiv(initialY, initialX);

        slots[0] = spot; // latent spot estimate
        slots[1] = 0; // intensity memory
        slots[2] = 0; // bid pressure
        slots[3] = 0; // ask pressure
        slots[4] = 0; // cooldown memory
        slots[5] = 0; // size memory
        slots[6] = 0; // last side: 0 unset, 1 buy, 2 sell
        slots[7] = spot; // last observed spot
        slots[8] = 0; // last timestamp
        slots[9] = 0; // quiet memory

        return (BASE_FEE, BASE_FEE);
    }

    function afterSwap(TradeInfo calldata trade)
        external
        override
        returns (uint256 bidFee, uint256 askFee)
    {
        uint256 spot = wdiv(trade.reserveY, trade.reserveX);
        uint256 lastSpot = slots[7];
        uint256 latentSpot = _blend(slots[0], spot, ALPHA_SPOT);
        uint256 lastTimestamp = slots[8];
        uint256 gap = trade.timestamp > lastTimestamp ? trade.timestamp - lastTimestamp : 0;

        uint256 sizeX = wdiv(trade.amountX, trade.reserveX);
        uint256 sizeY = wdiv(trade.amountY, trade.reserveY);
        uint256 tradeSize = sizeX > sizeY ? sizeX : sizeY;

        uint256 spotJump = lastSpot == 0 ? 0 : wdiv(absDiff(spot, lastSpot), lastSpot);
        uint256 latentGap = latentSpot == 0 ? 0 : wdiv(absDiff(spot, latentSpot), latentSpot);
        uint256 shock = tradeSize > spotJump ? tradeSize : spotJump;
        if (latentGap > shock) {
            shock = latentGap;
        }
        if (tradeSize > 9 * BPS) {
            shock += wmul(tradeSize, 1900 * BPS);
        } else if (tradeSize > 4 * BPS) {
            shock += wmul(tradeSize, 1100 * BPS);
        }

        uint256 intensity = _tradeIntensity(trade);
        uint256 intensityMemory = _blend(slots[1], intensity, ALPHA_INTENSITY);
        if (gap >= 4) {
            intensityMemory = wmul(intensityMemory, 7600 * BPS);
        } else if (gap >= 2) {
            intensityMemory = wmul(intensityMemory, 9000 * BPS);
        }

        uint256 cooldown = wmul(slots[4], DECAY_COOLDOWN);
        uint256 sizeMemory = wmul(slots[5], DECAY_SLOW);
        uint256 bidPressure = wmul(slots[2], DECAY_FAST);
        uint256 askPressure = wmul(slots[3], DECAY_FAST);
        uint256 quietMemory = wmul(slots[9], DECAY_SLOW);

        if (gap >= 5) {
            cooldown = wmul(cooldown, 5400 * BPS);
            sizeMemory = wmul(sizeMemory, 7600 * BPS);
            bidPressure = wmul(bidPressure, 7000 * BPS);
            askPressure = wmul(askPressure, 7000 * BPS);
            quietMemory = wmul(quietMemory, 6500 * BPS);
        } else if (gap >= 2) {
            cooldown = wmul(cooldown, 8200 * BPS);
            sizeMemory = wmul(sizeMemory, 8800 * BPS);
            bidPressure = wmul(bidPressure, 8500 * BPS);
            askPressure = wmul(askPressure, 8500 * BPS);
            quietMemory = wmul(quietMemory, 8400 * BPS);
        }

        cooldown = clamp(cooldown + wmul(shock, 1200 * BPS), 0, WAD);
        if (sizeMemory < tradeSize) {
            sizeMemory = tradeSize;
        }

        uint256 quietSignal = 0;
        if (gap >= 8) {
            quietSignal = WAD;
        } else if (gap > 0) {
            quietSignal = (gap * WAD) / 8;
        }

        uint256 calmSignal = quietSignal;
        if (shock > 7 * BPS) {
            calmSignal = calmSignal / 3;
        } else if (shock > 4 * BPS) {
            calmSignal = calmSignal / 2;
        }

        if (trade.isBuy) {
            bidPressure = clamp(
                bidPressure + wmul(shock, 1700 * BPS) + wmul(latentGap, 900 * BPS),
                0,
                WAD
            );
            askPressure = clamp(
                askPressure + wmul(shock, 650 * BPS) + wmul(intensityMemory, 250 * BPS),
                0,
                WAD
            );
        } else {
            askPressure = clamp(
                askPressure + wmul(shock, 1700 * BPS) + wmul(latentGap, 900 * BPS),
                0,
                WAD
            );
            bidPressure = clamp(
                bidPressure + wmul(shock, 650 * BPS) + wmul(intensityMemory, 250 * BPS),
                0,
                WAD
            );
        }

        uint256 common = BASE_FEE;
        common = clampFee(
            common +
                wmul(cooldown, 1550 * BPS) +
                wmul(sizeMemory, 620 * BPS) +
                wmul(intensityMemory, 420 * BPS) +
                wmul(quietMemory, 200 * BPS)
        );

        if (calmSignal > 0) {
            uint256 calmRebate = wmul(calmSignal, 420 * BPS);
            common = common > calmRebate ? common - calmRebate : MIN_FEE;
        }

        bidFee =
            common +
            wmul(bidPressure, 2150 * BPS) +
            wmul(shock, trade.isBuy ? 1750 * BPS : 550 * BPS);
        askFee =
            common +
            wmul(askPressure, 2150 * BPS) +
            wmul(shock, trade.isBuy ? 550 * BPS : 1750 * BPS);

        if (spot >= latentSpot) {
            bidFee += wmul(latentGap, 950 * BPS);
        } else {
            askFee += wmul(latentGap, 950 * BPS);
        }

        uint256 recapture = 0;
        if (cooldown < 7 * BPS) {
            if (gap >= 5) {
                recapture = 7 * BPS;
            } else if (gap >= 2) {
                recapture = 4 * BPS;
            } else {
                recapture = 2 * BPS;
            }
        }

        uint256 sameSideBoost = 0;
        if (cooldown < 5 * BPS) {
            sameSideBoost = gap >= 4 ? 3 * BPS : 2 * BPS;
        }

        if (trade.isBuy) {
            if (slots[6] == 1) {
                bidFee = clampFee(bidFee + sameSideBoost);
            }
            if (askFee > recapture) {
                askFee -= recapture;
            } else {
                askFee = MIN_FEE;
            }
            if (quietSignal > 0 && askFee > 4 * BPS) {
                askFee -= wmul(quietSignal, 250 * BPS);
            }
            slots[6] = 1;
        } else {
            if (slots[6] == 2) {
                askFee = clampFee(askFee + sameSideBoost);
            }
            if (bidFee > recapture) {
                bidFee -= recapture;
            } else {
                bidFee = MIN_FEE;
            }
            if (quietSignal > 0 && bidFee > 4 * BPS) {
                bidFee -= wmul(quietSignal, 250 * BPS);
            }
            slots[6] = 2;
        }

        if (gap >= 4 && cooldown < 5 * BPS) {
            bidFee = bidFee > 3 * BPS ? bidFee - 3 * BPS : MIN_FEE;
            askFee = askFee > 3 * BPS ? askFee - 3 * BPS : MIN_FEE;
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
        slots[9] = quietMemory > quietSignal ? quietMemory : quietSignal;

        return (bidFee, askFee);
    }

    function getName() external pure override returns (string memory) {
        return "QuietGapRecapture";
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
