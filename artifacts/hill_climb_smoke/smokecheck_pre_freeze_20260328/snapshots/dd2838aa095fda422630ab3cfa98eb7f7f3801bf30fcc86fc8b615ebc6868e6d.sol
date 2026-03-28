// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {AMMStrategyBase} from "./AMMStrategyBase.sol";
import {TradeInfo} from "./IAMMStrategy.sol";

contract Strategy is AMMStrategyBase {
    uint256 internal constant ANCHOR_FEE = 75 * BPS;

    function afterInitialize(uint256, uint256) external pure override returns (uint256, uint256) {
        return (ANCHOR_FEE, ANCHOR_FEE);
    }

    function afterSwap(TradeInfo calldata) external pure override returns (uint256, uint256) {
        return (ANCHOR_FEE, ANCHOR_FEE);
    }

    function getName() external pure override returns (string memory) {
        return "Anchor75Control";
    }
}
