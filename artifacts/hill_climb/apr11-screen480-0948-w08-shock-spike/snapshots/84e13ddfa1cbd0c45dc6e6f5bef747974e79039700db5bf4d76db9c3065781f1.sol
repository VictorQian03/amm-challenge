// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {AMMStrategyBase} from "./AMMStrategyBase.sol";
import {TradeInfo} from "./IAMMStrategy.sol";

/// @title Latent State Shock Spike Candidate
/// @notice Calm-period retail capture with sharper fee spikes on shocks and faster post-shock decay.
contract Strategy is AMMStrategyBase {
    uint256 internal constant BASE_FEE = 60 * BPS;
    uint256 internal constant EVENT_THRESHOLD = 8 * BPS;
    uint256 internal constant DECAY_FAST = 8400 * BPS;
    uint256 internal constant DECAY_SLOW = 9200 * BPS;
    uint256 internal constant DECAY_COOLDOWN = 9000 * BPS;
    uint256 internal constant ALPHA_SPOT = 12 * BPS;
    uint256 internal constant ALPHA_INTENSITY = 18 * BPS;

    function afterInitialize(uint256 initialX, uint256 initialY)
        external
        override
        returns (uint256 bidFee, uint256 askFee)
    {
        uint256 spot = wdiv(initialY, initialX);

        slots[0] = spot; // latent spot estimate
        slots[1] = 0; // intensity memory
        slots[2] = 0; // bid shock pressure
        slots[3] = 0; // ask shock pressure
        slots[4] = 0; // cooldown memory
        slots[5] = 0; // size memory
        slots[6] = 0; // last side: 0 unset, 1 buy, 2 sell
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
        uint256 gap = trade.timestamp > slots[8] ? trade.timestamp - slots[8] : 0;

        uint256 intensity = _tradeIntensity(trade);
        uint256 intensityMemory = _blend(slots[1], intensity, ALPHA_INTENSITY);
        if (gap > 4) {
            intensityMemory = wmul(intensityMemory, 7600 * BPS);
        } else if (gap > 1) {
            intensityMemory = wmul(intensityMemory, 8800 * BPS);
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
            shock += wmul(tradeSize, 2000 * BPS);
        } else if (tradeSize > 5 * BPS) {
            shock += wmul(tradeSize, 1000 * BPS);
        }
        if (spotJump > 6 * BPS && latentGap > 6 * BPS) {
            shock += wmul(spotJump + latentGap, 500 * BPS);
        }

        uint256 cooldown = wmul(slots[4], DECAY_COOLDOWN);
        if (gap > 5) {
            cooldown = wmul(cooldown, 5200 * BPS);
        } else if (gap > 2) {
            cooldown = wmul(cooldown, 7600 * BPS);
        }
        uint256 shockKick = shock > EVENT_THRESHOLD ? shock - EVENT_THRESHOLD : 0;
        cooldown = clamp(cooldown + wmul(shockKick, 1800 * BPS), 0, WAD);

        uint256 sizeMemory = wmul(slots[5], DECAY_SLOW);
        if (gap > 5) {
            sizeMemory = wmul(sizeMemory, 7000 * BPS);
        } else if (gap > 2) {
            sizeMemory = wmul(sizeMemory, 8500 * BPS);
        }
        if (sizeMemory < tradeSize) {
            sizeMemory = tradeSize;
        }

        uint256 bidPressure = wmul(slots[2], DECAY_FAST);
        uint256 askPressure = wmul(slots[3], DECAY_FAST);
        if (gap > 5) {
            bidPressure = wmul(bidPressure, 6500 * BPS);
            askPressure = wmul(askPressure, 6500 * BPS);
        }

        if (trade.isBuy) {
            bidPressure = clamp(
                bidPressure + wmul(shock, 2200 * BPS) + wmul(latentGap, 1200 * BPS),
                0,
                WAD
            );
            askPressure = clamp(
                askPressure + wmul(shock, 1100 * BPS) + wmul(intensityMemory, 350 * BPS),
                0,
                WAD
            );
        } else {
            askPressure = clamp(
                askPressure + wmul(shock, 2200 * BPS) + wmul(latentGap, 1200 * BPS),
                0,
                WAD
            );
            bidPressure = clamp(
                bidPressure + wmul(shock, 1100 * BPS) + wmul(intensityMemory, 350 * BPS),
                0,
                WAD
            );
        }

        uint256 eventSurcharge = 0;
        if (shockKick > 0) {
            eventSurcharge = wmul(shockKick, 1800 * BPS);
        }
        uint256 common = clampFee(
            BASE_FEE +
                wmul(cooldown, 1700 * BPS) +
                eventSurcharge
        );

        uint256 recapture = 0;
        if (cooldown < 7 * BPS) {
            recapture = gap > 4 ? 6 * BPS : 3 * BPS;
        }

        bidFee =
            common +
            wmul(bidPressure, 2400 * BPS) +
            wmul(shock, trade.isBuy ? 2000 * BPS : 700 * BPS);
        askFee =
            common +
            wmul(askPressure, 2400 * BPS) +
            wmul(shock, trade.isBuy ? 700 * BPS : 2000 * BPS);

        if (spot >= latentSpot) {
            bidFee += wmul(latentGap, 900 * BPS);
        } else {
            askFee += wmul(latentGap, 900 * BPS);
        }

        if (trade.isBuy) {
            if (slots[6] == 1) {
                bidFee = clampFee(bidFee + BPS);
            }
            if (askFee > recapture) {
                askFee -= recapture;
            } else {
                askFee = MIN_FEE;
            }
            slots[6] = 1;
        } else {
            if (slots[6] == 2) {
                askFee = clampFee(askFee + BPS);
            }
            if (bidFee > recapture) {
                bidFee -= recapture;
            } else {
                bidFee = MIN_FEE;
            }
            slots[6] = 2;
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
        return "LatentStateShockSpike";
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
