// SPDX-License-Identifier: agpl-3.0
pragma solidity ^0.8.0;

import "./DummyERC20Impl.sol";
import "./DummyERC20RewardToken.sol";
import "./IStaticAToken.sol";
import "./IBridge_L2.sol";

contract DummyStaticATokenImpl is DummyERC20Impl {
    IBridge_L2 internal _L2Bridge;
    address internal _owner;
    mapping(address => uint256) internal unclaimedRewards;

    constructor(
        address Owner, 
        IBridge_L2 L2Bridge) {
        _owner = Owner;
        _L2Bridge = L2Bridge;
    }

    modifier onlyOwner()
    {
        require (msg.sender == _owner, "only owner can access");
        _;
    }

    function owner() public view returns (address) {
        return _owner;
    }

    function claimRewards(address caller) external {
        address _rewAAVE = _L2Bridge.getRewTokenAddress();
        require(_rewAAVE != address(0), "Invalid rewards token");
        uint256 amount = unclaimedRewards[caller];
        unclaimedRewards[caller] = 0;
        _L2Bridge.mintRewards(msg.sender, amount);
    }

    /**
     * @dev Mints `amount` tokens to `user`
     * @param user The address receiving the minted tokens
     * @param amount The amount of tokens getting minted
     * @return `true` if the entire action executed successfully
     */
    function mint(address user, uint256 amount) external onlyOwner returns (bool) {
        require(user != address(0), "attempted to mint to the 0 address");
        // shortcut to save gas
        require(amount != 0, "attempt to mint 0 tokens");

        // Updating the total supply
        uint256 oldTotalSupply = totalSupply();
        t = oldTotalSupply + amount;

        // Updating the balance of user to which to tokens were minted
        uint256 oldAccountBalance = balanceOf(user);
        b[user] = oldAccountBalance + amount;

        return true;
    }

    /**
     * @dev Burns `amount` tokens from `user`
     * @param user The owner of the tokens, getting them burned
     * @param amount The amount being burned
     **/
    function burn(address user, uint256 amount) external onlyOwner {
        require(user != address(0), "attempted to burn funds from address 0");
        // shortcut to save gas
        require(amount != 0, "attempt to burn 0 tokens");

        // Updating the total supply
        uint256 oldTotalSupply = totalSupply();
        t = oldTotalSupply - amount;

        // Updating the balance of user to which to tokens were minted
        uint256 oldAccountBalance = balanceOf(user);
        b[user] = oldAccountBalance - amount;
    }
}