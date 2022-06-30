// SPDX-License-Identifier: agpl-3.0
pragma solidity 0.8.10;

import {IAToken} from "./IAToken.sol";
import {ILendingPool} from "./ILendingPool.sol";

contract ATokenWithPool {

    address internal Underlying_Asset;
    ILendingPool internal Lending_Pool;
    IAaveIncentivesController internal Incentive_Controller;
    
    /**
     * @dev Returns the lending pool of this aToken.
     **/
    function POOL() external view returns (ILendingPool){
        return Lending_Pool;
    }

    /**
     * @dev Returns the address of the underlying asset of this aToken (E.g. WETH for aWETH)
     **/
    function UNDERLYING_ASSET_ADDRESS() external view returns (address){
        return Underlying_Asset;
    }

    /**
     * @dev Returns the address of the incentives controller contract
     **/
    function getIncentivesController()
        external
        view
        returns (IAaveIncentivesController) {
            return Incentive_Controller;
        }
}
