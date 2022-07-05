// SPDX-License-Identifier: agpl-3.0
pragma solidity ^0.8.0;
import "./DummyERC20Impl.sol";

contract DummyERC20RewAAVE_L2 is DummyERC20Impl {
    /**
     * @dev Mints `amount` tokens to `user`
     * @param user The address receiving the minted tokens
     * @param amount The amount of tokens getting minted
     * @return `true` if the entire action executed successfully
     */
    function mint(address user, uint256 amount) external returns (bool) {
        require(user != address(0), "attempted to mint to the 0 address");
        // shortcut to save gas
        require(amount != 0, "attempt to mint 0 tokens");

        // Updating the total supply
        uint256 oldTotalSupply = super.totalSupply();
        t = oldTotalSupply + amount;

        // Updating the balance of user to which to tokens were minted
        uint256 oldAccountBalance = super.balanceOf(user);
        b[user] = oldAccountBalance + amount;

        return true;
    }

    /**
     * @dev Burns `amount` tokens from `user`
     * @param user The owner of the tokens, getting them burned
     * @param amount The amount being burned
     **/
    function burn(address user, uint256 amount) external {
        require(user != address(0), "attempted to burn funds from address 0");
        // shortcut to save gas
        require(amount != 0, "attempt to burn 0 tokens");

        // Updating the total supply
        uint256 oldTotalSupply = super.totalSupply();
        t = oldTotalSupply - amount;

        // Updating the balance of user to which to tokens were minted
        uint256 oldAccountBalance = super.balanceOf(user);
        b[user] = oldAccountBalance - amount;
    }
}
