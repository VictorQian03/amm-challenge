// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {AMMStrategyBase} from "./AMMStrategyBase.sol";
import {TradeInfo} from "./IAMMStrategy.sol";

contract Strategy is AMMStrategyBase {
    uint256 internal constant BASE_FEE = 70 * BPS;
    uint256 internal constant DECAY_FAST = 8500 * BPS;
    uint256 internal constant DECAY_SLOW = 9200 * BPS;
    uint256 internal constant DECAY_COOLDOWN = 9000 * BPS;

    function afterInitialize(uint256 initialX, uint256 initialY)
        external
        override
        returns (uint256 bidFee, uint256 askFee)
    {
        uint256 spot = wdiv(initialY, initialX);

        slots[0] = BASE_FEE;
        slots[1] = BASE_FEE;
        slots[2] = 0; // bid pressure
        slots[3] = 0; // ask pressure
        slots[4] = 0; // cooldown
        slots[5] = 0; // size memory
        slots[6] = 0; // last side: 0 none, 1 buy, 2 sell
        slots[7] = spot; // last observed spot

        return (BASE_FEE, BASE_FEE);
    }

    function afterSwap(TradeInfo calldata trade)
        external
        override
        returns (uint256 bidFee, uint256 askFee)
    {
        uint256 sizeX = wdiv(trade.amountX, trade.reserveX);
        uint256 sizeY = wdiv(trade.amountY, trade.reserveY);
        uint256 tradeSize = sizeX > sizeY ? sizeX : sizeY;

        uint256 currentSpot = wdiv(trade.reserveY, trade.reserveX);
        uint256 lastSpot = slots[7];
        uint256 spotJump = lastSpot == 0 ? 0 : wdiv(absDiff(currentSpot, lastSpot), lastSpot);

        uint256 bidPressure = wmul(slots[2], DECAY_FAST);
        uint256 askPressure = wmul(slots[3], DECAY_FAST);
        uint256 cooldown = wmul(slots[4], DECAY_COOLDOWN);
        uint256 sizeMemory = wmul(slots[5], DECAY_SLOW);

        uint256 shock = tradeSize > spotJump ? tradeSize : spotJump;
        if (tradeSize > 10 * BPS) {
            shock = shock + wmul(tradeSize, 2000 * BPS);
        } else if (tradeSize > 4 * BPS) {
            shock = shock + wmul(tradeSize, 1200 * BPS);
        }

        cooldown = clamp(cooldown + wmul(shock, 1500 * BPS), MIN_FEE, WAD);
        sizeMemory = sizeMemory > tradeSize ? sizeMemory : tradeSize;

        if (trade.isBuy) {
            bidPressure = clamp(bidPressure + wmul(shock, 1600 * BPS), MIN_FEE, WAD);
            askPressure = clamp(askPressure + wmul(shock, 700 * BPS), MIN_FEE, WAD);
        } else {
            askPressure = clamp(askPressure + wmul(shock, 1600 * BPS), MIN_FEE, WAD);
            bidPressure = clamp(bidPressure + wmul(shock, 700 * BPS), MIN_FEE, WAD);
        }

        uint256 common = BASE_FEE;
        common = clampFee(common + wmul(cooldown, 2400 * BPS) + wmul(sizeMemory, 900 * BPS));

        bidFee =
            common +
            wmul(bidPressure, 2200 * BPS) +
            wmul(shock, trade.isBuy ? 1800 * BPS : 600 * BPS);
        askFee =
            common +
            wmul(askPressure, 2200 * BPS) +
            wmul(shock, trade.isBuy ? 600 * BPS : 1800 * BPS);

        if (askFee > wmul(bidPressure, 900 * BPS)) {
            askFee -= wmul(bidPressure, 900 * BPS);
        } else {
            askFee = MIN_FEE;
        }
        if (bidFee > wmul(askPressure, 900 * BPS)) {
            bidFee -= wmul(askPressure, 900 * BPS);
        } else {
            bidFee = MIN_FEE;
        }

        if (trade.isBuy) {
            if (slots[6] == 1) {
                bidFee = clampFee(bidFee + BPS);
            }
            if (cooldown < 6 * BPS && askFee > 3 * BPS) {
                askFee -= 3 * BPS;
            }
            slots[6] = 1;
        } else {
            if (slots[6] == 2) {
                askFee = clampFee(askFee + BPS);
            }
            if (cooldown < 6 * BPS && bidFee > 3 * BPS) {
                bidFee -= 3 * BPS;
            }
            slots[6] = 2;
        }

        bidFee = clampFee(bidFee);
        askFee = clampFee(askFee);

        slots[0] = bidFee;
        slots[1] = askFee;
        slots[2] = bidPressure;
        slots[3] = askPressure;
        slots[4] = cooldown;
        slots[5] = sizeMemory;
        slots[7] = currentSpot;

        return (bidFee, askFee);
    }

    function getName() external pure override returns (string memory) {
        return "MicrostructureGuard";
    }
}
