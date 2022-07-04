// SPDX-License-Identifier: Apache-2.0.
pragma solidity 0.8.10;

import "../../contracts/l1/Bridge.sol";

contract BridgeHarness is Bridge {
    // Retrieving the UnderlyingAsset of the AToken
    function getUnderlyingAssetOfAToken(address AToken)
        public
        returns (IERC20 underlyingAsset)
    {
        return _aTokenData[AToken].underlyingAsset;
    }

    // Retrieving the LendingPool of the AToken
    function getLendingPoolOfAToken(address AToken)
        public
        returns (ILendingPool lendingPool)
    {
        return _aTokenData[AToken].lendingPool;
    }

    function tokenBalanceOf(IERC20 token, address u)
        public
        view
        returns (uint256)
    {
        return token.balanceOf(u);
    }
}
