// SPDX-License-Identifier: agpl-3.0
pragma solidity ^0.8.0;

import {IERC20} from "./DummyERC20Impl.sol";
import {ILendingPool} from "./SymbolicLendingPool.sol";


contract ATokenWithPoolImpl is DummyERC20Impl {
  
    address public UNDERLYING_ASSET_ADDRESS;
    ILendingPool public POOL;


    modifier onlyLendingPool() {
        require(msg.sender == address(POOL));
        _;
    }

    /**
     * @dev Mints `amount` aTokens to `user`
     * - Only callable by the LendingPool, as extra state updates there need to be managed
    * @param user The address receiving the minted tokens
    * @param amount The amount of tokens getting minted
    * @param index The new liquidity index of the reserve
    * @return `true` if the the previous balance of the user was 0
    */
    function mint(
        address user,
        uint256 amount,
        uint256 index
    ) external override onlyLendingPool returns (bool) {
        require(user != address(0), "attempted to mint to the 0 address");
        // shortcut to save gas
        require(amount != 0, "attempt to mint 0 tokens");
    
        // Updating the total supply
        uint256 oldTotalSupply = super.totalSupply();
        t = oldTotalSupply.add(amount);

        // Updating the balance of user to which to tokens were minted
        uint256 oldAccountBalance = super.balanceOf(user);
        b[user] = oldAccountBalance.add(amount);

        return true;
    }

    /**
     * @dev Burns aTokens from `user` and sends the equivalent amount of underlying to `receiverOfUnderlying`
     * - Only callable by the LendingPool, as extra state updates there need to be managed
     * @param user The owner of the aTokens, getting them burned
     * @param receiverOfUnderlying The address that will receive the underlying
     * @param amount The amount being burned
     * @param index The new liquidity index of the reserve
     **/
    function burn(
        address user,
        address receiverOfUnderlying,
        uint256 amount,
        uint256 index
    ) external override onlyLendingPool {
        require(user != address(0), "attempted to burn funds from address 0");
        // shortcut to save gas
        require(amount != 0, "attempt to burn 0 tokens");

        // Updating the total supply
        uint256 oldTotalSupply = super.totalSupply();
        t = oldTotalSupply.sub(amount);

        // Updating the balance of user to which to tokens were minted
        uint256 oldAccountBalance = super.balanceOf(user);
        b[user] = oldAccountBalance.sub(amount);

        IERC20(UNDERLYING_ASSET_ADDRESS).transfer(receiverOfUnderlying, amount);
    }

    /**
     * @dev Returns the scaled total supply of the variable debt token. as a simplification it chosen to be twice the value of total supply
     * @return the scaled total supply
     **/
    function scaledTotalSupply() public returns (uint256) {
        return (super.totalSupply() * 2);
    }
}