// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {AMMStrategyBase} from "./AMMStrategyBase.sol";
import {TradeInfo} from "./IAMMStrategy.sol";

contract Strategy is AMMStrategyBase {
    uint256 internal constant BASE_FEE = 68 * BPS;
    uint256 internal constant DECAY_FAST = 8600 * BPS;
    uint256 internal constant DECAY_SLOW = 9300 * BPS;
    uint256 internal constant DECAY_COOLDOWN = 9000 * BPS;
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
        slots[2] = 0; // bid danger pressure
        slots[3] = 0; // ask danger pressure
        slots[4] = 0; // cooldown
        slots[5] = 0; // size memory
        slots[6] = 0; // last side: 1 buy-x-from-user, 2 sell-x-to-user
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
        uint256 latentSpot = _blend(slots[0], spot, ALPHA_SPOT);
        uint256 lastTimestamp = slots[8];
        uint256 gap = trade.timestamp > lastTimestamp ? trade.timestamp - lastTimestamp : 0;

        uint256 intensity = _tradeIntensity(trade);
        uint256 intensityMemory = _blend(slots[1], intensity, ALPHA_INTENSITY);
        if (gap > 3) {
            intensityMemory = wmul(intensityMemory, 8000 * BPS);
        }

        uint256 sizeMemory = wmul(slots[5], DECAY_SLOW);
        uint256 sizeX = wdiv(trade.amountX, trade.reserveX);
        uint256 sizeY = wdiv(trade.amountY, trade.reserveY);
        uint256 tradeSize = sizeX > sizeY ? sizeX : sizeY;
        if (gap > 3) {
            sizeMemory = wmul(sizeMemory, 8200 * BPS);
        }
        if (sizeMemory < tradeSize) {
            sizeMemory = tradeSize;
        }

        uint256 spotJump = lastSpot == 0 ? 0 : wdiv(absDiff(spot, lastSpot), lastSpot);
        uint256 latentGap = latentSpot == 0 ? 0 : wdiv(absDiff(spot, latentSpot), latentSpot);
        uint256 shock = tradeSize > spotJump ? tradeSize : spotJump;
        if (latentGap > shock) {
            shock = latentGap;
        }
        if (tradeSize > 10 * BPS) {
            shock += wmul(tradeSize, 1600 * BPS);
        } else if (tradeSize > 4 * BPS) {
            shock += wmul(tradeSize, 800 * BPS);
        }

        uint256 cooldown = wmul(slots[4], DECAY_COOLDOWN);
        if (gap > 4) {
            cooldown = wmul(cooldown, 7200 * BPS);
        }
        cooldown = clamp(cooldown + wmul(shock, 1200 * BPS), 0, WAD);

        uint256 bidDanger = wmul(slots[2], DECAY_FAST);
        uint256 askDanger = wmul(slots[3], DECAY_FAST);
        if (gap > 4) {
            bidDanger = wmul(bidDanger, 7800 * BPS);
            askDanger = wmul(askDanger, 7800 * BPS);
        }

        if (trade.isBuy) {
            askDanger = clamp(
                askDanger + wmul(shock, 1700 * BPS) + wmul(latentGap, 1100 * BPS),
                0,
                WAD
            );
            bidDanger = clamp(
                bidDanger + wmul(shock, 500 * BPS) + wmul(intensityMemory, 250 * BPS),
                0,
                WAD
            );
        } else {
            bidDanger = clamp(
                bidDanger + wmul(shock, 1700 * BPS) + wmul(latentGap, 1100 * BPS),
                0,
                WAD
            );
            askDanger = clamp(
                askDanger + wmul(shock, 500 * BPS) + wmul(intensityMemory, 250 * BPS),
                0,
                WAD
            );
        }

        uint256 common = BASE_FEE;
        common = clampFee(
            common +
                wmul(cooldown, 1500 * BPS) +
                wmul(sizeMemory, 700 * BPS) +
                wmul(intensityMemory, 450 * BPS)
        );

        bidFee = common + wmul(bidDanger, 2100 * BPS);
        askFee = common + wmul(askDanger, 2100 * BPS);

        if (spot >= latentSpot) {
            bidFee += wmul(latentGap, 1100 * BPS);
        } else {
            askFee += wmul(latentGap, 1100 * BPS);
        }

        uint256 idleDiscount = 0;
        if (cooldown < 7 * BPS) {
            if (gap >= 6) {
                idleDiscount = 10 * BPS;
            } else if (gap >= 3) {
                idleDiscount = 4 * BPS;
            }
        }

        if (trade.isBuy) {
            if (slots[6] == 1 && bidFee > 2 * BPS) {
                bidFee -= 2 * BPS;
            }
            if (bidFee > idleDiscount) {
                bidFee -= idleDiscount;
            } else {
                bidFee = MIN_FEE;
            }
            slots[6] = 1;
        } else {
            if (slots[6] == 2 && askFee > 2 * BPS) {
                askFee -= 2 * BPS;
            }
            if (askFee > idleDiscount) {
                askFee -= idleDiscount;
            } else {
                askFee = MIN_FEE;
            }
            slots[6] = 2;
        }

        bidFee = clampFee(bidFee);
        askFee = clampFee(askFee);

        slots[0] = latentSpot;
        slots[1] = intensityMemory;
        slots[2] = bidDanger;
        slots[3] = askDanger;
        slots[4] = cooldown;
        slots[5] = sizeMemory;
        slots[7] = spot;
        slots[8] = trade.timestamp;

        return (bidFee, askFee);
    }

    function getName() external pure override returns (string memory) {
        return "LatentArbAware";
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
