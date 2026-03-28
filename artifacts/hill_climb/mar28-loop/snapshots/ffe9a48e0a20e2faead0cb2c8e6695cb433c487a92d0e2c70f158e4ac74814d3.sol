// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {AMMStrategyBase} from "./AMMStrategyBase.sol";
import {TradeInfo} from "./IAMMStrategy.sol";

/// @title Latent State Quiet Recovery Candidate
/// @notice Latent spot guard with explicit idle-gap recovery to re-enter retail flow faster.
contract Strategy is AMMStrategyBase {
    uint256 internal constant BASE_FEE = 64 * BPS;
    uint256 internal constant DECAY_FAST = 8500 * BPS;
    uint256 internal constant DECAY_SLOW = 9200 * BPS;
    uint256 internal constant DECAY_COOLDOWN = 9000 * BPS;
    uint256 internal constant ALPHA_SPOT = 12 * BPS;

    function afterInitialize(uint256 initialX, uint256 initialY)
        external
        override
        returns (uint256 bidFee, uint256 askFee)
    {
        uint256 spot = wdiv(initialY, initialX);

        slots[0] = spot; // latent spot estimate
        slots[1] = 0; // bid pressure
        slots[2] = 0; // ask pressure
        slots[3] = 0; // cooldown
        slots[4] = 0; // size memory
        slots[5] = 0; // last side: 1 buy, 2 sell
        slots[6] = spot; // last observed spot
        slots[7] = 0; // last timestamp

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
        uint256 lastTimestamp = slots[7];
        uint256 gap = trade.timestamp > lastTimestamp ? trade.timestamp - lastTimestamp : 0;

        uint256 sizeX = wdiv(trade.amountX, trade.reserveX);
        uint256 sizeY = wdiv(trade.amountY, trade.reserveY);
        uint256 tradeSize = sizeX > sizeY ? sizeX : sizeY;

        uint256 spotJump = lastSpot == 0 ? 0 : wdiv(absDiff(currentSpot, lastSpot), lastSpot);
        uint256 latentGap = latentSpot == 0 ? 0 : wdiv(absDiff(currentSpot, latentSpot), latentSpot);
        uint256 bidPressure = wmul(slots[1], DECAY_FAST);
        uint256 askPressure = wmul(slots[2], DECAY_FAST);
        uint256 cooldown = wmul(slots[3], DECAY_COOLDOWN);
        uint256 sizeMemory = wmul(slots[4], DECAY_SLOW);

        uint256 shock = tradeSize > spotJump ? tradeSize : spotJump;
        if (latentGap > shock) {
            shock = latentGap;
        }
        if (tradeSize > 10 * BPS) {
            shock += wmul(tradeSize, 2000 * BPS);
        } else if (tradeSize > 4 * BPS) {
            shock += wmul(tradeSize, 1200 * BPS);
        }

        if (gap >= 6) {
            bidPressure = wmul(bidPressure, 6500 * BPS);
            askPressure = wmul(askPressure, 6500 * BPS);
            cooldown = wmul(cooldown, 5000 * BPS);
            sizeMemory = wmul(sizeMemory, 7200 * BPS);
        } else if (gap >= 3) {
            bidPressure = wmul(bidPressure, 8200 * BPS);
            askPressure = wmul(askPressure, 8200 * BPS);
            cooldown = wmul(cooldown, 7800 * BPS);
            sizeMemory = wmul(sizeMemory, 8600 * BPS);
        }

        cooldown = clamp(cooldown + wmul(shock, 1500 * BPS), 0, WAD);
        sizeMemory = sizeMemory > tradeSize ? sizeMemory : tradeSize;

        uint256 quietSignal = 0;
        if (gap >= 8) {
            quietSignal = WAD;
        } else if (gap > 0) {
            quietSignal = (gap * WAD) / 8;
        }

        uint256 calmSignal = quietSignal;
        if (shock > 8 * BPS) {
            calmSignal = calmSignal / 4;
        } else if (shock > 4 * BPS) {
            calmSignal = calmSignal / 2;
        }

        if (trade.isBuy) {
            bidPressure = clamp(bidPressure + wmul(shock, 1600 * BPS), 0, WAD);
            askPressure = clamp(askPressure + wmul(shock, 700 * BPS), 0, WAD);
        } else {
            askPressure = clamp(askPressure + wmul(shock, 1600 * BPS), 0, WAD);
            bidPressure = clamp(bidPressure + wmul(shock, 700 * BPS), 0, WAD);
        }

        uint256 common = clampFee(
            BASE_FEE +
                wmul(cooldown, 2200 * BPS) +
                wmul(sizeMemory, 760 * BPS)
        );

        if (calmSignal > 0 && cooldown < 9 * BPS) {
            uint256 calmRebate = wmul(calmSignal, 260 * BPS);
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

        if (currentSpot >= latentSpot) {
            bidFee = clampFee(bidFee + BPS + wmul(latentGap, 700 * BPS));
        } else {
            askFee = clampFee(askFee + BPS + wmul(latentGap, 700 * BPS));
        }

        uint256 recapture = 0;
        if (cooldown < 7 * BPS) {
            if (gap >= 6) {
                recapture = 6 * BPS;
            } else if (gap >= 3) {
                recapture = 3 * BPS;
            }
        }

        if (trade.isBuy) {
            if (slots[5] == 1) {
                bidFee = clampFee(bidFee + 2 * BPS);
            }
            if (askFee > recapture) {
                askFee -= recapture;
            } else if (recapture > 0) {
                askFee = MIN_FEE;
            }
            slots[5] = 1;
        } else {
            if (slots[5] == 2) {
                askFee = clampFee(askFee + 2 * BPS);
            }
            if (bidFee > recapture) {
                bidFee -= recapture;
            } else if (recapture > 0) {
                bidFee = MIN_FEE;
            }
            slots[5] = 2;
        }

        if (gap >= 5 && cooldown < 5 * BPS) {
            bidFee = bidFee > 2 * BPS ? bidFee - 2 * BPS : MIN_FEE;
            askFee = askFee > 2 * BPS ? askFee - 2 * BPS : MIN_FEE;
        }

        bidFee = clampFee(bidFee);
        askFee = clampFee(askFee);

        slots[0] = latentSpot;
        slots[1] = bidPressure;
        slots[2] = askPressure;
        slots[3] = cooldown;
        slots[4] = sizeMemory;
        slots[6] = currentSpot;
        slots[7] = trade.timestamp;

        return (bidFee, askFee);
    }

    function getName() external pure override returns (string memory) {
        return "LatentStateQuietRecovery";
    }

    function _blend(uint256 prev, uint256 sample, uint256 alpha) internal pure returns (uint256) {
        return wmul(prev, WAD - alpha) + wmul(sample, alpha);
    }
}
