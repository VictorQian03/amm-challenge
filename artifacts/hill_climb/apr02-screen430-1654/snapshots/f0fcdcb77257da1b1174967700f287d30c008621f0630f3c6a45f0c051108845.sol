// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {AMMStrategyBase} from "./AMMStrategyBase.sol";
import {TradeInfo} from "./IAMMStrategy.sol";

/// @title Latent State Incumbent Gap-Aware V4 Candidate
/// @notice Keep the calm regime cheaper, but add a hard defensive regime for clustered shocks.
contract Strategy is AMMStrategyBase {
    uint256 internal constant BASE_FEE = 61 * BPS;
    uint256 internal constant DECAY_FAST = 8500 * BPS;
    uint256 internal constant DECAY_SLOW = 9200 * BPS;
    uint256 internal constant DECAY_COOLDOWN = 9000 * BPS;
    uint256 internal constant ALPHA_SPOT = 12 * BPS;
    uint256 internal constant ALPHA_QUIET = 8 * BPS;

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
        slots[8] = 0; // quiet memory

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
        uint256 latentGap = latentSpot == 0 ? 0 : wdiv(absDiff(currentSpot, latentSpot), latentSpot);

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

        uint256 eventSignal = shock > spotJump ? shock : spotJump;
        uint256 quietSignal = 0;
        if (gap >= 8) {
            quietSignal = WAD;
        } else if (gap > 0) {
            quietSignal = (gap * WAD) / 8;
        }
        if (eventSignal > 7 * BPS) {
            quietSignal /= 4;
        } else if (eventSignal > 4 * BPS) {
            quietSignal /= 2;
        }
        uint256 quietMemory = _blend(slots[8], quietSignal, ALPHA_QUIET);
        if (gap >= 4) {
            quietMemory = wmul(quietMemory, 7600 * BPS);
        } else if (gap >= 2) {
            quietMemory = wmul(quietMemory, 9000 * BPS);
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
                wmul(cooldown, 2200 * BPS) +
                wmul(sizeMemory, 820 * BPS)
        );

        if (gap >= 3 && cooldown < 5 * BPS) {
            common = common > 3 * BPS ? common - 3 * BPS : MIN_FEE;
        }

        uint256 quietRecapture = 0;
        if (
            cooldown < 5 * BPS &&
            quietSignal > 0 &&
            eventSignal <= 4 * BPS &&
            latentGap <= 3 * BPS
        ) {
            quietRecapture = wmul(quietSignal, 120 * BPS) + wmul(quietMemory, 60 * BPS);
        }
        bidFee =
            common +
            wmul(bidPressure, 2200 * BPS) +
            wmul(shock, trade.isBuy ? 1800 * BPS : 600 * BPS);
        askFee =
            common +
            wmul(askPressure, 2200 * BPS) +
            wmul(shock, trade.isBuy ? 600 * BPS : 1800 * BPS);

        if (eventSignal > 5 * BPS) {
            uint256 special = wmul(eventSignal - 5 * BPS, 650 * BPS);
            if (trade.isBuy) {
                bidFee += special;
                askFee += special / 4;
            } else {
                askFee += special;
                bidFee += special / 4;
            }
        }

        bool clustered = gap <= 1 && (
            (trade.isBuy && slots[5] == 1) || (!trade.isBuy && slots[5] == 2)
        );
        uint256 defense;
        if (eventSignal >= 8 * BPS) {
            defense = wmul(eventSignal - 8 * BPS, 1600 * BPS);
        } else if (clustered && eventSignal >= 4 * BPS) {
            defense = 2 * BPS + wmul(eventSignal - 4 * BPS, 900 * BPS);
        }
        if (defense != 0) {
            bidFee += defense;
            askFee += defense;
        }

        uint256 arbOverlay = 0;
        if (latentGap >= 4 * BPS) {
            arbOverlay = wmul(latentGap - 4 * BPS, 450 * BPS);
            if (eventSignal >= 6 * BPS) {
                arbOverlay += wmul(eventSignal - 6 * BPS, 180 * BPS);
            }
        }
        if (arbOverlay != 0) {
            if (trade.isBuy) {
                bidFee += arbOverlay;
                askFee += arbOverlay / 5;
            } else {
                askFee += arbOverlay;
                bidFee += arbOverlay / 5;
            }
        }

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

        if (quietRecapture > 0) {
            if (trade.isBuy) {
                if (askFee > quietRecapture) {
                    askFee -= quietRecapture;
                } else {
                    askFee = MIN_FEE;
                }
            } else {
                if (bidFee > quietRecapture) {
                    bidFee -= quietRecapture;
                } else {
                    bidFee = MIN_FEE;
                }
            }
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
        slots[8] = quietMemory > quietSignal ? quietMemory : quietSignal;

        return (bidFee, askFee);
    }

    function getName() external pure override returns (string memory) {
        return "LatentStateIncumbentGapAwareV10QuietIdle";
    }

    function _blend(uint256 prev, uint256 sample, uint256 alpha) internal pure returns (uint256) {
        return wmul(prev, WAD - alpha) + wmul(sample, alpha);
    }
}
