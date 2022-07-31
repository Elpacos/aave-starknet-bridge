// SPDX-License-Identifier: Apache-2.0.
pragma solidity 0.8.10;

import "../../contracts/l1/Bridge.sol";
import {IBridge_L2} from "./IBridge_L2.sol";

contract BridgeHarness is Bridge {
    IBridge_L2 public BRIDGE_L2;

    /*************************
     *        Getters        *
     *************************/

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

    // Retrieving the balance of a user with respect to a given token
    function tokenBalanceOf(IERC20 token, address user)
        public
        view
        returns (uint256)
    {
        return token.balanceOf(user);
    }

    /************************
     *       Wrappers       *
     ************************/
    /* Wrapper functions allow calling internal functions from within the spec */

    // A wrapper function for _staticToDynamicAmount
    function _staticToDynamicAmount_Wrapper(
        uint256 amount,
        address asset,
        ILendingPool lendingPool
    ) external view returns (uint256) {
        return super._staticToDynamicAmount(amount, asset, lendingPool);
    }

    // A wrapper function for _getCurrentRewardsIndex
    function _getCurrentRewardsIndex_Wrapper(address l1AToken)
        external
        view
        returns (uint256)
    {
        return super._getCurrentRewardsIndex(l1AToken);
    }

    // A wrapper function for _computeRewardsDiff
    function _computeRewardsDiff_Wrapper(
        uint256 amount,
        uint256 l2RewardsIndex,
        uint256 l1RewardsIndex
    ) external pure returns (uint256) {
        return
            super._computeRewardsDiff(amount, l2RewardsIndex, l1RewardsIndex);
    }

    /*****************************************
     *        Function Summarizations        *
     *****************************************/
    // When depositing tokens via the L1 bridge, a deposit on the L2 side is invoked from this side to save 2 step deposit.
    // The L2 deposit just mints static_Atoken on the L2 side.
    function _sendDepositMessage(
        address l1Token,
        address from,
        uint256 l2Recipient,
        uint256 amount,
        uint256 blockNumber,
        uint256 currentRewardsIndex
    ) internal override {
        BRIDGE_L2.deposit(l1Token, amount, address(uint160(l2Recipient)));
    }

    // To save the 2 step mechanism, a call to withdraw from the L2 side invokes the withdraw on the L1 side.
    // Therefore the consumeMessage method is unneeded
    function _consumeMessage(
        address l1Token,
        uint256 l2sender,
        address recipient,
        uint256 amount,
        uint256 l2RewardsIndex
    ) internal override {}

    // A L1-L2 RewardIndex sync. A call from L1 sync the value on L2
    function _sendIndexUpdateMessage(
        address l1Token,
        address from,
        uint256 blockNumber,
        uint256 currentRewardsIndex
    ) internal override {
        BRIDGE_L2.l2RewardsIndexSetter(currentRewardsIndex);
    }

    // To save the 2 step mechanism, a call to bridgeRewards on the L2 side burns the rewardToken and invokes receiveRewards
    // Therefore the consumeBridgeRewardMessage method is unneeded
    function _consumeBridgeRewardMessage(
        uint256 l2sender,
        address recipient,
        uint256 amount
    ) internal override {}
}
