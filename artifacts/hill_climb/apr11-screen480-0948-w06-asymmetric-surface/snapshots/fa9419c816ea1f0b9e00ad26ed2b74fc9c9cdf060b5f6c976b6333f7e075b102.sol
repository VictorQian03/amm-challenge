// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {AMMStrategyBase} from "./AMMStrategyBase.sol";
import {TradeInfo} from "./IAMMStrategy.sol";

contract Strategy is AMMStrategyBase {
    uint256 internal constant ANCHOR_PRICE = 100 * WAD;
    uint256 internal constant BASE_FEE = 75 * BPS;
    uint256 internal constant MAX_STREAK = 8;

    function afterInitialize(uint256, uint256) external override returns (uint256, uint256) {
        slots[0] = BASE_FEE; // bid fee
        slots[1] = BASE_FEE; // ask fee
        slots[2] = 0; // signed flow memory
        slots[3] = 0; // signed trend memory
        slots[4] = 0; // last side: 0 unset, 1 buy, 2 sell
        slots[5] = 0; // streak length
        slots[6] = 0; // last timestamp
        slots[7] = ANCHOR_PRICE; // last observed spot price
        slots[8] = 0; // regime memory
        return (BASE_FEE, BASE_FEE);
    }

    function afterSwap(TradeInfo calldata trade) external override returns (uint256 bidFee, uint256 askFee) {
        uint256 prevBid = slots[0];
        uint256 prevAsk = slots[1];
        uint256 prevSpot = slots[7];
        uint256 prevRegime = slots[8];
        uint256 lastTimestamp = slots[6];
        uint256 lastSide = slots[4];
        uint256 streak = slots[5];

        uint256 currentSpot = trade.reserveX == 0 ? prevSpot : wdiv(trade.reserveY, trade.reserveX);
        uint256 xPressure = _cap01(_safeWdiv(trade.amountX, trade.reserveX));
        uint256 yPressure = _cap01(_safeWdiv(trade.amountY, trade.reserveY));
        uint256 sizeSignal = (xPressure + yPressure) / 2;
        uint256 spotSignal = _cap01(_safeWdiv(absDiff(currentSpot, ANCHOR_PRICE), ANCHOR_PRICE));
        uint256 moveSignal = prevSpot == 0
            ? spotSignal
            : _cap01(_safeWdiv(absDiff(currentSpot, prevSpot), _max(currentSpot, prevSpot)));

        uint256 gap = 1;
        if (trade.timestamp > lastTimestamp && lastTimestamp != 0) {
            gap = trade.timestamp - lastTimestamp;
        }
        uint256 cooldownSignal = gap >= 6 ? WAD : (gap * WAD) / 6;

        uint256 shapeSignal = sqrt(sizeSignal * WAD);
        uint256 interactionSignal = wmul(shapeSignal, moveSignal);
        uint256 regimeSignal = _cap01((moveSignal + interactionSignal + cooldownSignal) / 3);

        int256 flowMemory = int256(slots[2]);
        int256 trendMemory = int256(slots[3]);
        int256 direction = trade.isBuy ? int256(int256(WAD)) : -int256(int256(WAD));
        int256 spotDirection = currentSpot >= prevSpot ? int256(int256(WAD)) : -int256(int256(WAD));

        int256 nextFlow = (flowMemory * 3 + direction * int256(sizeSignal)) / 4;
        int256 nextTrend = (trendMemory * 3 + spotDirection * int256(moveSignal)) / 4;
        uint256 nextRegime = ((prevRegime * 3) + regimeSignal) / 4;

        uint256 nextStreak = 1;
        uint256 currentSide = trade.isBuy ? 1 : 2;
        if (lastSide == currentSide && streak < MAX_STREAK) {
            nextStreak = streak + 1;
        }

        uint256 bidAnchor = (prevBid * 3 + BASE_FEE) / 4;
        uint256 askAnchor = (prevAsk * 3 + BASE_FEE) / 4;

        uint256 toxicTilt = 0;
        toxicTilt = clampFee(toxicTilt + wmul(_cap01(_absSigned(nextFlow)), bpsToWad(4)));
        toxicTilt = clampFee(toxicTilt + wmul(spotSignal, bpsToWad(3)));
        toxicTilt = clampFee(toxicTilt + wmul(interactionSignal, bpsToWad(2)));
        toxicTilt = clampFee(toxicTilt + wmul(nextRegime, bpsToWad(2)));

        uint256 calmTilt = 0;
        calmTilt = clampFee(calmTilt + wmul(cooldownSignal, bpsToWad(1)));
        calmTilt = clampFee(calmTilt + wmul(_streakSignal(nextStreak), bpsToWad(1)));

        bool toxicOnAsk = nextFlow >= 0;
        if (nextTrend < 0) {
            toxicOnAsk = !toxicOnAsk;
        }
        if (currentSpot < prevSpot && nextRegime > 2 * BPS) {
            toxicOnAsk = false;
        } else if (currentSpot > prevSpot && nextRegime > 2 * BPS) {
            toxicOnAsk = true;
        }

        if (toxicOnAsk) {
            bidFee = clampFee(bidAnchor + calmTilt);
            askFee = askAnchor > toxicTilt ? askAnchor - toxicTilt : MIN_FEE;
        } else {
            bidFee = bidAnchor > toxicTilt ? bidAnchor - toxicTilt : MIN_FEE;
            askFee = clampFee(askAnchor + calmTilt);
        }

        if (trade.isBuy) {
            bidFee = clampFee(bidFee + wmul(_streakSignal(nextStreak), bpsToWad(1)));
        } else {
            askFee = clampFee(askFee + wmul(_streakSignal(nextStreak), bpsToWad(1)));
        }

        slots[0] = bidFee;
        slots[1] = askFee;
        slots[2] = uint256(nextFlow);
        slots[3] = uint256(nextTrend);
        slots[4] = currentSide;
        slots[5] = nextStreak;
        slots[6] = trade.timestamp;
        slots[7] = currentSpot;
        slots[8] = nextRegime;

        return (bidFee, askFee);
    }

    function getName() external pure override returns (string memory) {
        return "AsymmetricSurface";
    }

    function _safeWdiv(uint256 x, uint256 y) internal pure returns (uint256) {
        if (y == 0) {
            return 0;
        }
        return wdiv(x, y);
    }

    function _cap01(uint256 value) internal pure returns (uint256) {
        return value > WAD ? WAD : value;
    }

    function _absSigned(int256 value) internal pure returns (uint256) {
        return uint256(value >= 0 ? value : -value);
    }

    function _max(uint256 a, uint256 b) internal pure returns (uint256) {
        return a > b ? a : b;
    }

    function _streakSignal(uint256 streak) internal pure returns (uint256) {
        uint256 capped = streak > MAX_STREAK ? MAX_STREAK : streak;
        return (capped * WAD) / MAX_STREAK;
    }
}
