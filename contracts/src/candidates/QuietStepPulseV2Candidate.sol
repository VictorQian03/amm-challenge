// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {AMMStrategyBase} from "./AMMStrategyBase.sol";
import {TradeInfo} from "./IAMMStrategy.sol";

/// @title Quiet Step Pulse V2 Candidate
/// @notice Lower-fee step-pulse branch with faster quiet release and lighter carry pricing.
contract Strategy is AMMStrategyBase {
    uint256 internal constant BASE_FEE = 35 * BPS;
    uint256 internal constant DECAY_PULSE = 7300 * BPS;
    uint256 internal constant DECAY_CARRY = 8600 * BPS;
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
        slots[5] = 0; // last side: 1 buy, 2 sell
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
        uint256 gap = trade.timestamp > lastTimestamp ? trade.timestamp - lastTimestamp : 0;
        uint256 side = trade.isBuy ? 1 : 2;

        uint256 bidPulse = wmul(slots[0], DECAY_PULSE);
        uint256 askPulse = wmul(slots[1], DECAY_PULSE);
        uint256 carryShock = wmul(slots[2], DECAY_CARRY);
        uint256 sizeMemory = wmul(slots[3], DECAY_CARRY);

        if (!sameStep) {
            bidPulse = wmul(bidPulse, 2200 * BPS);
            askPulse = wmul(askPulse, 2200 * BPS);
            carryShock = wmul(carryShock, gap >= 4 ? 4200 * BPS : 6200 * BPS);
            sizeMemory = wmul(sizeMemory, gap >= 4 ? 5600 * BPS : 7800 * BPS);
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
            shock += wmul(tradeSize, 1600 * BPS);
        } else if (tradeSize > 8 * BPS) {
            shock += wmul(tradeSize, 1000 * BPS);
        } else if (tradeSize > 3 * BPS) {
            shock += wmul(tradeSize, 500 * BPS);
        }

        carryShock = clamp(carryShock + wmul(shock, 1200 * BPS), 0, WAD);

        if (sameStep && lastSide == side) {
            if (streak < MAX_STREAK) {
                streak += 1;
            }
        } else {
            streak = 1;
        }

        uint256 streakSignal = (streak * WAD) / MAX_STREAK;
        if (trade.isBuy) {
            bidPulse = clamp(
                bidPulse + wmul(shock, 2100 * BPS) + wmul(streakSignal, 16 * BPS),
                0,
                WAD
            );
            askPulse = wmul(askPulse, sameStep ? 7800 * BPS : 3600 * BPS);
        } else {
            askPulse = clamp(
                askPulse + wmul(shock, 2100 * BPS) + wmul(streakSignal, 16 * BPS),
                0,
                WAD
            );
            bidPulse = wmul(bidPulse, sameStep ? 7800 * BPS : 3600 * BPS);
        }

        uint256 common = clampFee(
            BASE_FEE +
                wmul(carryShock, 700 * BPS) +
                wmul(sizeMemory, 220 * BPS)
        );

        bidFee =
            common +
            wmul(bidPulse, 2450 * BPS) +
            wmul(shock, trade.isBuy ? 1550 * BPS : 450 * BPS);
        askFee =
            common +
            wmul(askPulse, 2450 * BPS) +
            wmul(shock, trade.isBuy ? 450 * BPS : 1550 * BPS);

        uint256 moveBias = lastSpot == 0 ? 0 : wdiv(absDiff(currentSpot, lastSpot), lastSpot);
        if (currentSpot >= lastSpot) {
            bidFee += wmul(moveBias, 550 * BPS);
        } else {
            askFee += wmul(moveBias, 550 * BPS);
        }

        uint256 recapture = 0;
        if (!sameStep && carryShock < 8 * BPS) {
            recapture = gap >= 4 ? 7 * BPS : 4 * BPS;
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

        if (gap >= 4 && carryShock < 6 * BPS) {
            bidFee = bidFee > 3 * BPS ? bidFee - 3 * BPS : MIN_FEE;
            askFee = askFee > 3 * BPS ? askFee - 3 * BPS : MIN_FEE;
        }

        bidFee = clampFee(bidFee);
        askFee = clampFee(askFee);

        slots[0] = bidPulse;
        slots[1] = askPulse;
        slots[2] = carryShock;
        slots[3] = sizeMemory;
        slots[4] = trade.timestamp;
        slots[5] = side;
        slots[6] = streak;
        slots[7] = currentSpot;

        return (bidFee, askFee);
    }

    function getName() external pure override returns (string memory) {
        return "QuietStepPulseV2";
    }
}
