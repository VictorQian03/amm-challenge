// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {AMMStrategyBase} from "../AMMStrategyBase.sol";
import {TradeInfo} from "../IAMMStrategy.sol";

/// @title Latent State Incumbent Gap-Aware V2 Candidate
/// @notice Same incumbent core as v1, with a slightly stronger release back to calm-period pricing.
contract Strategy is AMMStrategyBase {
    uint256 internal constant BASE_FEE = 69 * BPS;
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
        uint256 bidPressure = wmul(slots[1], DECAY_FAST);
        uint256 askPressure = wmul(slots[2], DECAY_FAST);
        uint256 cooldown = wmul(slots[3], DECAY_COOLDOWN);
        uint256 sizeMemory = wmul(slots[4], DECAY_SLOW);

        if (gap >= 4) {
            bidPressure = wmul(bidPressure, 8000 * BPS);
            askPressure = wmul(askPressure, 8000 * BPS);
            cooldown = wmul(cooldown, 7400 * BPS);
            sizeMemory = wmul(sizeMemory, 8400 * BPS);
        } else if (gap >= 2) {
            bidPressure = wmul(bidPressure, 9000 * BPS);
            askPressure = wmul(askPressure, 9000 * BPS);
            cooldown = wmul(cooldown, 8800 * BPS);
            sizeMemory = wmul(sizeMemory, 9300 * BPS);
        }

        uint256 shock = tradeSize > spotJump ? tradeSize : spotJump;
        if (tradeSize > 10 * BPS) {
            shock += wmul(tradeSize, 2000 * BPS);
        } else if (tradeSize > 4 * BPS) {
            shock += wmul(tradeSize, 1200 * BPS);
        }

        cooldown = clamp(cooldown + wmul(shock, 1500 * BPS), 0, WAD);
        sizeMemory = sizeMemory > tradeSize ? sizeMemory : tradeSize;

        if (trade.isBuy) {
            bidPressure = clamp(bidPressure + wmul(shock, 1600 * BPS), 0, WAD);
            askPressure = clamp(askPressure + wmul(shock, 700 * BPS), 0, WAD);
        } else {
            askPressure = clamp(askPressure + wmul(shock, 1600 * BPS), 0, WAD);
            bidPressure = clamp(bidPressure + wmul(shock, 700 * BPS), 0, WAD);
        }

        uint256 common = clampFee(
            BASE_FEE +
                wmul(cooldown, 2350 * BPS) +
                wmul(sizeMemory, 880 * BPS)
        );

        if (gap >= 3 && cooldown < 5 * BPS) {
            common = common > 2 * BPS ? common - 2 * BPS : MIN_FEE;
        }

        bidFee =
            common +
            wmul(bidPressure, 2200 * BPS) +
            wmul(shock, trade.isBuy ? 1800 * BPS : 600 * BPS);
        askFee =
            common +
            wmul(askPressure, 2200 * BPS) +
            wmul(shock, trade.isBuy ? 600 * BPS : 1800 * BPS);

        if (currentSpot >= latentSpot) {
            bidFee = clampFee(bidFee + BPS);
        } else {
            askFee = clampFee(askFee + BPS);
        }

        if (trade.isBuy) {
            if (slots[5] == 1) {
                bidFee = clampFee(bidFee + 2 * BPS);
            }
            if (cooldown < 5 * BPS && askFee > 5 * BPS) {
                askFee -= 5 * BPS;
            } else if (cooldown < 7 * BPS && askFee > 3 * BPS) {
                askFee -= 3 * BPS;
            }
            slots[5] = 1;
        } else {
            if (slots[5] == 2) {
                askFee = clampFee(askFee + 2 * BPS);
            }
            if (cooldown < 5 * BPS && bidFee > 5 * BPS) {
                bidFee -= 5 * BPS;
            } else if (cooldown < 7 * BPS && bidFee > 3 * BPS) {
                bidFee -= 3 * BPS;
            }
            slots[5] = 2;
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
        return "LatentStateIncumbentGapAwareV2";
    }

    function _blend(uint256 prev, uint256 sample, uint256 alpha) internal pure returns (uint256) {
        return wmul(prev, WAD - alpha) + wmul(sample, alpha);
    }
}
