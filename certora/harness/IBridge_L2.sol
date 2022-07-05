pragma solidity 0.8.10;
pragma experimental ABIEncoderV2;

interface IBridge_L2 {
    function l2RewardsIndexSetter(uint256 l1RewardsIndex) external;

    function deposit(
        address asset,
        uint256 amount,
        address onBehalfOf
    ) external;

    function initiateWithdraw(
        address asset,
        uint256 amount,
        address to
    ) external returns (uint256);

    function bridgeRewards(address recipient, uint256 amount) external;
}
