// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {AMMStrategyBase} from "./AMMStrategyBase.sol";
import {TradeInfo} from "./IAMMStrategy.sol";

contract Strategy is AMMStrategyBase {
    uint256 internal constant BASE_FEE = 66 * BPS;
    uint256 internal constant DECAY_FAST = 8200 * BPS;
    uint256 internal constant DECAY_SLOW = 9000 * BPS;
    uint256 internal constant MAX_STREAK = 6;

    function afterInitialize(uint256 initialX, uint256 initialY)
        external
        override
        returns (uint256 bidFee, uint256 askFee)
    {
        uint256 spot = wdiv(initialY, initialX);

        slots[0] = 0; // bid pulse
        slots[1] = 0; // ask pulse
        slots[2] = 0; // carry shock
        slots[3] = 0; // size memory
        slots[4] = 0; // last timestamp
        slots[5] = 0; // last side: 1 trade.isBuy, 2 otherwise
        slots[6] = 0; // same-step streak
        slots[7] = spot; // last observed spot

        return (BASE_FEE, BASE_FEE);
    }

    function afterSwap(TradeInfo calldata trade)
        external
        override
        returns (uint256 bidFee, uint256 askFee)
    {
        uint256 lastTimestamp = slots[4];
        uint256 lastSide = slots[5];
        uint256 streak = slots[6];
        bool sameStep = trade.timestamp == lastTimestamp;
        uint256 currentSide = trade.isBuy ? 1 : 2;

        uint256 bidPulse = wmul(slots[0], DECAY_FAST);
        uint256 askPulse = wmul(slots[1], DECAY_FAST);
        uint256 carryShock = wmul(slots[2], DECAY_SLOW);
        uint256 sizeMemory = wmul(slots[3], DECAY_SLOW);

        if (!sameStep) {
            bidPulse = wmul(bidPulse, 3500 * BPS);
            askPulse = wmul(askPulse, 3500 * BPS);
            carryShock = wmul(carryShock, 6000 * BPS);
            streak = 0;
        }

        uint256 sizeX = wdiv(trade.amountX, trade.reserveX);
        uint256 sizeY = wdiv(trade.amountY, trade.reserveY);
        uint256 tradeSize = sizeX > sizeY ? sizeX : sizeY;
        if (sizeMemory < tradeSize) {
            sizeMemory = tradeSize;
        }

        uint256 currentSpot = wdiv(trade.reserveY, trade.reserveX);
        uint256 lastSpot = slots[7];
        uint256 spotJump = lastSpot == 0 ? 0 : wdiv(absDiff(currentSpot, lastSpot), lastSpot);

        uint256 shock = tradeSize > spotJump ? tradeSize : spotJump;
        if (sameStep) {
            shock += wmul(tradeSize, 1100 * BPS);
        } else {
            shock += wmul(tradeSize, 500 * BPS);
        }
        carryShock = clamp(carryShock + wmul(shock, 1200 * BPS), 0, WAD);

        if (lastSide == currentSide && sameStep) {
            if (streak < MAX_STREAK) {
                streak += 1;
            }
        } else {
            streak = 1;
        }

        uint256 streakSignal = (streak * WAD) / MAX_STREAK;
        if (trade.isBuy) {
            bidPulse = clamp(
                bidPulse + wmul(shock, 1900 * BPS) + wmul(streakSignal, 12 * BPS),
                0,
                WAD
            );
            askPulse = wmul(askPulse, sameStep ? 8500 * BPS : 5000 * BPS);
        } else {
            askPulse = clamp(
                askPulse + wmul(shock, 1900 * BPS) + wmul(streakSignal, 12 * BPS),
                0,
                WAD
            );
            bidPulse = wmul(bidPulse, sameStep ? 8500 * BPS : 5000 * BPS);
        }

        uint256 common = BASE_FEE;
        common = clampFee(
            common +
                wmul(carryShock, 1000 * BPS) +
                wmul(sizeMemory, 400 * BPS)
        );

        bidFee = common + wmul(bidPulse, 2400 * BPS);
        askFee = common + wmul(askPulse, 2400 * BPS);

        uint256 recapture = 0;
        if (!sameStep && carryShock < 8 * BPS) {
            recapture = 6 * BPS;
        } else if (sameStep && streak == 1 && carryShock < 6 * BPS) {
            recapture = 3 * BPS;
        }

        if (trade.isBuy) {
            if (askFee > recapture) {
                askFee -= recapture;
            }
            slots[5] = 1;
        } else {
            if (bidFee > recapture) {
                bidFee -= recapture;
            }
            slots[5] = 2;
        }

        bidFee = clampFee(bidFee);
        askFee = clampFee(askFee);

        slots[0] = bidPulse;
        slots[1] = askPulse;
        slots[2] = carryShock;
        slots[3] = sizeMemory;
        slots[4] = trade.timestamp;
        slots[6] = streak;
        slots[7] = currentSpot;

        return (bidFee, askFee);
    }

    function getName() external pure override returns (string memory) {
        return "StepPulse";
    }
}
