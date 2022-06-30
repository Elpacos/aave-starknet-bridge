pragma solidity 0.8.10;
pragma experimental ABIEncoderV2;

import {IERC20} from '@aave/core-v3/contracts/dependencies/openzeppelin/contracts/IERC20.sol';

contract IncentivesControllerMock {
  address internal Reward_Token;
  uint256 internal Distribution_End;
  address internal _rewardsVault;
  mapping(address => assetData) internal Asset_Data;

    struct assetData {
        uint256 index;
        uint256 emissionPerSecond;
        uint256 lastUpdate;
    }

  /**
   * @notice for backward compatibility with previous implementation of the Incentives controller
   * @return The address of the reward token
   */
  function REWARD_TOKEN() external view returns (address){
      return Reward_Token;
  }

    /**
     * @dev Gets the distribution end timestamp of the emissions
     */
    function DISTRIBUTION_END() external view returns (uint256){
        return Distribution_End;
    }

    /**
     * @dev returns the current rewards vault contract
     * @return address
     */
    function getRewardsVault() external view returns (address) {
        return _rewardsVault;
    }

    /*
     * @dev Returns the configuration of the distribution for a certain asset
     * @param asset The address of the reference asset of the distribution
     * @return The asset index, the emission per second and the last updated timestamp
     **/
    function getAssetData(address asset)
        external
        view
        returns (uint256, uint256, uint256){
            return (Asset_Data[asset].index, Asset_Data[asset].emissionPerSecond, Asset_Data[asset].lastUpdate);
        }

  /**
     * @dev Claims reward for a user, on all the assets of the lending pool, accumulating the pending rewards
     * @param amount Amount of rewards to claim
     * @param to Address that will be receiving the rewards
     * @return Rewards claimed
     **/
    function claimRewards(
        address[] calldata assets,
        uint256 amount,
        address to
    ) external returns (uint256){
        IERC20(Reward_Token).transferFrom(_rewardsVault, to, amount);
    }

}