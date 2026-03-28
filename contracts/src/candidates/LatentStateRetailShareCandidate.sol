// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {AMMStrategyBase} from "../AMMStrategyBase.sol";
import {TradeInfo} from "../IAMMStrategy.sol";

/// @title Latent State Retail Share Candidate
/// @notice Lower resting fee with sharper idle recapture and fast shock reversion.
contract Strategy is AMMStrategyBase {
    uint256 internal constant BASE_FEE = 62 * BPS;
    uint256 internal constant DECAY_FAST = 8000 * BPS;
    uint256 internal constant DECAY_SLOW = 8800 * BPS;
    uint256 internal constant DECAY_COOLDOWN = 8700 * BPS;
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
        slots[6] = 0; // last side: 1 buy, 2 sell
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
        uint256 gap = trade.timestamp > lastTimestamp ? trade.timestamp - lastTimestamp : 0;
        uint256 latentSpot = _blend(slots[0], spot, ALPHA_SPOT);

        uint256 intensity = _tradeIntensity(trade);
        uint256 intensityMemory = _blend(slots[1], intensity, ALPHA_INTENSITY);
        if (gap >= 4) {
            intensityMemory = wmul(intensityMemory, 7000 * BPS);
        } else if (gap >= 2) {
            intensityMemory = wmul(intensityMemory, 8500 * BPS);
        }

        uint256 sizeX = wdiv(trade.amountX, trade.reserveX);
        uint256 sizeY = wdiv(trade.amountY, trade.reserveY);
        uint256 tradeSize = sizeX > sizeY ? sizeX : sizeY;

        uint256 spotJump = lastSpot == 0 ? 0 : wdiv(absDiff(spot, lastSpot), lastSpot);
        uint256 latentGap = latentSpot == 0 ? 0 : wdiv(absDiff(spot, latentSpot), latentSpot);
        uint256 shock = tradeSize > spotJump ? tradeSize : spotJump;
        if (latentGap > shock) {
            shock = latentGap;
        }
        if (tradeSize > 10 * BPS) {
            shock += wmul(tradeSize, 2200 * BPS);
        } else if (tradeSize > 4 * BPS) {
            shock += wmul(tradeSize, 1400 * BPS);
        }

        uint256 cooldown = wmul(slots[4], DECAY_COOLDOWN);
        if (gap >= 4) {
            cooldown = wmul(cooldown, 5500 * BPS);
        } else if (gap >= 2) {
            cooldown = wmul(cooldown, 7800 * BPS);
        }
        cooldown = clamp(cooldown + wmul(shock, 1300 * BPS), 0, WAD);

        uint256 sizeMemory = wmul(slots[5], DECAY_SLOW);
        if (gap >= 4) {
            sizeMemory = wmul(sizeMemory, 6500 * BPS);
        } else if (gap >= 2) {
            sizeMemory = wmul(sizeMemory, 8000 * BPS);
        }
        if (sizeMemory < tradeSize) {
            sizeMemory = tradeSize;
        }

        uint256 bidPressure = wmul(slots[2], DECAY_FAST);
        uint256 askPressure = wmul(slots[3], DECAY_FAST);
        if (gap >= 4) {
            bidPressure = wmul(bidPressure, 6500 * BPS);
            askPressure = wmul(askPressure, 6500 * BPS);
        } else if (gap >= 2) {
            bidPressure = wmul(bidPressure, 8200 * BPS);
            askPressure = wmul(askPressure, 8200 * BPS);
        }

        if (trade.isBuy) {
            bidPressure = clamp(
                bidPressure + wmul(shock, 1700 * BPS) + wmul(latentGap, 900 * BPS),
                0,
                WAD
            );
            askPressure = clamp(
                askPressure + wmul(shock, 800 * BPS) + wmul(intensityMemory, 450 * BPS),
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
                bidPressure + wmul(shock, 800 * BPS) + wmul(intensityMemory, 450 * BPS),
                0,
                WAD
            );
        }

        uint256 common = BASE_FEE;
        common = clampFee(
            common +
                wmul(cooldown, 1800 * BPS) +
                wmul(sizeMemory, 700 * BPS) +
                wmul(intensityMemory, 450 * BPS)
        );

        bidFee =
            common +
            wmul(bidPressure, 2200 * BPS) +
            wmul(shock, trade.isBuy ? 1900 * BPS : 700 * BPS);
        askFee =
            common +
            wmul(askPressure, 2200 * BPS) +
            wmul(shock, trade.isBuy ? 700 * BPS : 1900 * BPS);

        if (spot >= latentSpot) {
            bidFee += wmul(latentGap, 900 * BPS);
        } else {
            askFee += wmul(latentGap, 900 * BPS);
        }

        uint256 recapture = 0;
        if (cooldown < 8 * BPS) {
            if (gap >= 5) {
                recapture = 8 * BPS;
            } else if (gap >= 2) {
                recapture = 5 * BPS;
            } else {
                recapture = 3 * BPS;
            }
        }

        uint256 sameSideRecapture = 0;
        if (cooldown < 6 * BPS) {
            sameSideRecapture = gap >= 4 ? 4 * BPS : 2 * BPS;
        }

        if (trade.isBuy) {
            if (slots[6] == 1 && bidFee > sameSideRecapture) {
                bidFee -= sameSideRecapture;
            }
            if (askFee > recapture) {
                askFee -= recapture;
            } else {
                askFee = MIN_FEE;
            }
            slots[6] = 1;
        } else {
            if (slots[6] == 2 && askFee > sameSideRecapture) {
                askFee -= sameSideRecapture;
            }
            if (bidFee > recapture) {
                bidFee -= recapture;
            } else {
                bidFee = MIN_FEE;
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

        return (bidFee, askFee);
    }

    function getName() external pure override returns (string memory) {
        return "LatentRetailShare";
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
