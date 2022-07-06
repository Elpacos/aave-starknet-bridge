// SPDX-License-Identifier: agpl-3.0
pragma solidity ^0.8.0;

contract DummyERC20ExtendedImpl {
    uint256 t;
    mapping(address => uint256) b;
    mapping(address => mapping(address => uint256)) a;

    string public name;
    string public symbol;
    uint256 public decimals;

    function myAddress() public returns (address) {
        return address(this);
    }

    function add(uint256 a, uint256 b) internal pure returns (uint256) {
        uint256 c = a + b;
        require(c >= a);
        return c;
    }

    function sub(uint256 a, uint256 b) internal pure returns (uint256) {
        require(a >= b);
        return a - b;
    }

    function totalSupply() public view returns (uint256) {
        return t;
    }

    function balanceOf(address account) public view returns (uint256) {
        return b[account];
    }

    function transfer(address recipient, uint256 amount)
        external
        returns (bool)
    {
        b[msg.sender] = sub(b[msg.sender], amount);
        b[recipient] = add(b[recipient], amount);
        return true;
    }

    function allowance(address owner, address spender)
        external
        view
        returns (uint256)
    {
        return a[owner][spender];
    }

    function approve(address spender, uint256 amount) external returns (bool) {
        a[msg.sender][spender] = amount;
        return true;
    }

    function transferFrom(
        address sender,
        address recipient,
        uint256 amount
    ) external returns (bool) {
        b[sender] = sub(b[sender], amount);
        b[recipient] = add(b[recipient], amount);
        a[sender][msg.sender] = sub(a[sender][msg.sender], amount);
        return true;
    }

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
    function burn(address user, uint256 amount) external {
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
