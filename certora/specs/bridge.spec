////////////////////////////////////////////////////////////////////////////
//                       Imports and multi-contracts                      //
////////////////////////////////////////////////////////////////////////////

import "erc20.spec"

// Declaring aliases for contracts according to the format:
// using Target_Contract as Alias_Name
/************************
 *     L1 contracts     *
 ************************/
    using DummyERC20UnderlyingA_L1 as UNDERLYING_ASSET_A 
    using DummyERC20UnderlyingB_L1 as UNDERLYING_ASSET_B
    using ATokenWithPoolA_L1 as ATOKEN_A
    using ATokenWithPoolB_L1 as ATOKEN_B
    using DummyERC20RewardToken as REWARD_TOKEN
    using SymbolicLendingPoolL1 as LENDINGPOOL_L1


/************************
 *     L2 contracts     *
 ************************/
    using BridgeL2Harness as BRIDGE_L2
    using StaticATokenA_L2 as STATIC_ATOKEN_A
    using StaticATokenB_L2 as STATIC_ATOKEN_B

// For referencing structs
    using BridgeHarness as Bridge

////////////////////////////////////////////////////////////////////////////
//                       Methods                                          //
////////////////////////////////////////////////////////////////////////////
// Declaring contracts' methods and summarizing them as needed
methods {
/**********************
 *     Bridge.sol     *
 **********************/
    initialize(uint256, address, address, address[], uint256[])
    deposit(address, uint256, uint256, uint16, bool) returns (uint256) 
    withdraw(address, uint256, address, uint256, uint256, bool)
    updateL2State(address)
    receiveRewards(uint256, address, uint256)
    
/*************************
 *     BridgeHarness     *
 *************************/
    // Note that these methods take as args OR return the contract types that are written in comment to their right.
    // In CVL we contracts are addresses an therefore we demand return of an address
    getUnderlyingAssetOfAToken(address) returns (address) envfree //(IERC20)
    getATokenOfUnderlyingAsset(address, address) returns (address) envfree
    getLendingPoolOfAToken(address) returns (address) envfree //(ILendingPool)
    _staticToDynamicAmount_Wrapper(uint256, address, address) envfree //(ILendingPool)
    _dynamicToStaticAmount_Wrapper(uint256, address, address) envfree //(ILendingPool)
    _computeRewardsDiff_Wrapper(uint256, uint256, uint256) envfree
    _getCurrentRewardsIndex_Wrapper(address) returns (uint256) 
    initiateWithdraw_L2(address, uint256, address)
    bridgeRewards_L2(address, uint256)
    underlyingtoAToken(address) returns (address) => DISPATCHER(true)

/******************************
 *     IStarknetMessaging     *
 ******************************/
    // The methods of Bridge.sol that call this contract are being overridden to bypass the messaging communication.
    // Instead, we modeled the L2 side in solidity and made direct calls between the sides.

/************************
 *     ILendingPool     *
 ************************/
    // The lending pool used in the contract is encapsulated within a struct in IBridge.sol.
    // We point to direct calls to these methods using dispatchers. 
    deposit(address, uint256, address, uint16) => DISPATCHER(true)
    withdraw(address, uint256, address) returns (uint256) => DISPATCHER(true)
    getReserveNormalizedIncome(address) returns (uint256) => DISPATCHER(true)
    LENDINGPOOL_L1.liquidityIndex() returns (uint256) envfree


/*************************************************
 *     IATokenWithPool + IScaledBalanceToken     *
 *************************************************/
    mint(address, uint256, uint256) returns (bool) => DISPATCHER(true)
    mint(address, uint256) returns (bool) => DISPATCHER(true)
    burn(address,address, uint256, uint256) => DISPATCHER(true)
    burn(address, uint256) returns (bool) => DISPATCHER(true)
    POOL() returns (address) envfree => DISPATCHER(true)
    scaledTotalSupply() returns (uint256) envfree => DISPATCHER(true)
    UNDERLYING_ASSET_ADDRESS() => NONDET // just to remove red warning
    getIncentivesController() => NONDET

/************************************
 *     IncentivesControllerMock     *
 ************************************/
    _rewardToken() returns (address) envfree => DISPATCHER(true)
    DISTRIBUTION_END() returns (uint256) envfree => DISPATCHER(true)
    getRewardsVault() returns (address) envfree => DISPATCHER(true)
    getAssetData(address) returns (uint256, uint256, uint256) envfree => DISPATCHER(true)
    // Note that the sender of the funds here is RewardsVault which is arbitrary by default.
    // If any rule that count on the reward token balance, calls this method a `require RewardsVault != to` make sense to add
    claimRewards(address[], uint256, address) returns (uint256)

/***************************
 *     BridgeL2Harness     *
 ***************************/
    BRIDGE_L2.l2RewardsIndexSetter(uint256)
    BRIDGE_L2.deposit(address, uint256, address) envfree
    BRIDGE_L2.initiateWithdraw(address, uint256, address) returns (uint256)
    BRIDGE_L2.bridgeRewards(address, uint256)
    BRIDGE_L2.l2RewardsIndex() returns (uint256) envfree
    BRIDGE_L2.getStaticATokenAddress(address) returns (address) envfree
}

////////////////////////////////////////////////////////////////////////////
//                       Definitions                                      //
////////////////////////////////////////////////////////////////////////////

definition RAY() returns uint256 = 10^27;

////////////////////////////////////////////////////////////////////////////
//                       Rules                                            //
////////////////////////////////////////////////////////////////////////////

/*
    @Rule

    @Description:
        The balance of the recipient of a withdrawal increase by the deserved (dynamic) amount in either aToken or underlying, and in the reward token.

    @Formula:
        {

        }

        < call withdraw >
        
        {
            if toUnderlyingAsset:
                assert underlyingBalanceAfter == underlyingBalanceBefore + _staticToDynamicAmount_Wrapper(staticAmount, underlying, LENDINGPOOL)
            else:
                assert aTokenBalanceAfter == aTokenBalanceBefore + _staticToDynamicAmount_Wrapper(staticAmount, underlying, LENDINGPOOL)
            assert rewardTokenBalanceAfter == rewardTokenBalanceBefore + _computeRewardsDiff_Wrapper(staticAmount, l2RewardsIndex, _getCurrentRewardsIndex_Wrapper(e, aToken))
        }

    @Note:

    @Link:
*/

rule integrityOfWithdraw(method f, address recipient, address aToken){
    uint256 l2sender; bool toUnderlyingAsset;
    uint256 staticAmount; uint256 l2RewardsIndex;
    env e; calldataarg args;
    address underlying;
    setLinkage(underlying, aToken, STATIC_ATOKEN_A);
    uint256 underlyingBalanceBefore = tokenBalanceOf(e, underlying, recipient);
    uint256 aTokenBalanceBefore = tokenBalanceOf(e, aToken, recipient);
    uint256 rewardTokenBalanceBefore = tokenBalanceOf(e, REWARD_TOKEN, recipient);

    withdraw(e, aToken, l2sender, recipient, staticAmount, l2RewardsIndex, toUnderlyingAsset);

    uint256 underlyingBalanceAfter = tokenBalanceOf(e, underlying, recipient);
    uint256 aTokenBalanceAfter = tokenBalanceOf(e, aToken, recipient);
    uint256 rewardTokenBalanceAfter = tokenBalanceOf(e, REWARD_TOKEN, recipient);

    if (toUnderlyingAsset){
        assert underlyingBalanceAfter <= underlyingBalanceBefore + _staticToDynamicAmount_Wrapper(staticAmount, underlying, LENDINGPOOL_L1);
    }
    else {
        assert aTokenBalanceAfter <= aTokenBalanceBefore + _staticToDynamicAmount_Wrapper(staticAmount, underlying, LENDINGPOOL_L1);
    }
    assert rewardTokenBalanceAfter <= rewardTokenBalanceBefore + _computeRewardsDiff_Wrapper(staticAmount, l2RewardsIndex, _getCurrentRewardsIndex_Wrapper(e, aToken));
}

/*
    @Rule

    @Description:
        Balance of underlying asset should not change unless by calling to deposit/withdraw

    @Formula:
        {

        }

        < call any function >
        
        {
            underlyingBalanceAfter == underlyingBalanceBefore => < any function besides deposit or withdraw was called >
            < Neither deposit nor withdraw were called > => underlyingBalanceAfter == underlyingBalanceBefore
        }

    @Note:

    @Link:
*/

/*
rule balanceOfUnderlyingAssetChanged(method f, address u, address aToken) {
    env eB;
    env eF;
    calldataarg args;
    address asset;
    setLinkage(asset, aToken, STATIC_ATOKEN_A);
    address underlying  = getUnderlyingAssetOfAToken(aToken);
    uint256 underlyingBalanceBefore = tokenBalanceOf(eB, underlying, u);
    
    address aToken2; uint256 l2Recipient; address recipient; uint256 amount;

    callFunctionWithParams(f, eF, aToken2, l2Recipient, recipient, amount);

    uint256 underlyingBalanceAfter = tokenBalanceOf(eB, underlying, u);
    assert (underlyingBalanceAfter != underlyingBalanceBefore
            <=> ((f.selector == deposit(address, uint256, address).selector) ||
             (f.selector == initiateWithdraw_L2(address, uint256, address).selector))), "balanceOf changed";
}
*/

rule whoChangedStaticTokenBalance(address user, method f)
{
    env e;
    calldataarg args;
    requireValidUser(user);
    uint256 balanceBefore = STATIC_ATOKEN_A.balanceOf(e, user);
        f(e, args);
    uint256 balanceAfter = STATIC_ATOKEN_A.balanceOf(e, user);
    assert balanceAfter == balanceBefore,
     "function ${f} changed the static token balance"; 
}

invariant ATokenAssetPair(address asset, address AToken)
    getUnderlyingAssetOfAToken(AToken) == asset 
    <=>
    getATokenOfUnderlyingAsset(LENDINGPOOL_L1, asset) == AToken
    {
        preserved{
            require (asset !=0 && AToken !=0);
        }
    }

// Rule violation, check required:
// https://vaas-stg.certora.com/output/41958/61bcbac9d2ea9016913c/?anonymousKey=2477f0370cec5c5c3eb7aaa9b536d0f6b4ad567b
rule depositWithdrawReversed(uint256 amount)
{
    env eB; env eF;
    address Atoken; // AAVE Token
    address asset;  // underlying asset
    address StaticAToken; // staticAToken
    uint256 l2Recipient;
    uint16 referralCode;
    bool fromUnderlyingAsset;

    uint256 index_L1 = LENDINGPOOL_L1.liquidityIndex(); 
    uint256 index_L2 = BRIDGE_L2.l2RewardsIndex();

    setLinkage(asset, Atoken , StaticAToken);
    requireValidTokens(asset, Atoken, StaticAToken);
    requireInvariant ATokenAssetPair(asset, Atoken);
    require eF.msg.sender == eB.msg.sender;
    requireRayIndex();
    requireValidUser(eF.msg.sender);

    uint256 balanceU1 = tokenBalanceOf(eB, asset, eB.msg.sender);
    uint256 balanceA1 = tokenBalanceOf(eB, Atoken, eB.msg.sender);
        deposit(eB, Atoken, l2Recipient, amount, referralCode, fromUnderlyingAsset);
    uint256 balanceU2 = tokenBalanceOf(eB, asset, eB.msg.sender);
    uint256 balanceA2 = tokenBalanceOf(eB, Atoken, eB.msg.sender);
        initiateWithdraw_L2(eF, Atoken, amount, eF.msg.sender);
    uint256 balanceU3 = tokenBalanceOf(eB, asset, eB.msg.sender);
    uint256 balanceA3 = tokenBalanceOf(eB, Atoken, eB.msg.sender);
    
    assert index_L1 == index_L2 =>
        (balanceA1 == balanceA3 && balanceU1 == balanceU3);
}

// Checks that the transitions between static to dyanmic are inverses.
rule dynamicToStaticInversible(uint256 amount)
{
    // We assume both indexes (L1,L2) are represented in Ray (1e27).
    requireRayIndex();
    address asset;
    uint256 dynm = _staticToDynamicAmount_Wrapper(amount, asset, LENDINGPOOL_L1);
    uint256 stat = _dynamicToStaticAmount_Wrapper(dynm, asset, LENDINGPOOL_L1);
    assert amount == stat;
}

////////////////////////////////////////////////////////////////////////////
//                       Functions                                        //
////////////////////////////////////////////////////////////////////////////

// By definition, the liquidity indexes are expressed in RAY units.
// Therefore they must be as large as RAY (assuming liquidity index > 1).
function requireRayIndex() {
    require LENDINGPOOL_L1.liquidityIndex() >= RAY();
    require BRIDGE_L2.l2RewardsIndex() >= RAY();
}

// Linking the instances of ERC20s and LendingPool 
// within the ATokenData struct to the corresponding 
// symbolic contracts.
function setLinkage(
    address asset, 
    address AToken, 
    address static){
    // Setting the underlying token of the given AToken as either UNDERLYING_ASSET_A or UNDERLYING_ASSET_B
    require getUnderlyingAssetOfAToken(AToken) == asset;
    require getLendingPoolOfAToken(AToken) == LENDINGPOOL_L1;
    require BRIDGE_L2.getStaticATokenAddress(AToken) == static;
}

// Require the token trio (asset, Atoken, StaticAToken) to have
// distinct addresses.
function requireValidTokens(
    address asset, 
    address AToken, 
    address static){
        require asset != AToken &&
                AToken != static &&
                static != asset;
}

// Requirements for a "valid" user - exclude contracts addresses.
function requireValidUser(address user){
    require 
        user != Bridge &&
        user != BRIDGE_L2 &&
        user != UNDERLYING_ASSET_A &&
        user != UNDERLYING_ASSET_B &&
        user != ATOKEN_A &&
        user != ATOKEN_B &&
        user != STATIC_ATOKEN_A &&
        user != STATIC_ATOKEN_B &&
        user != REWARD_TOKEN &&
        user != LENDINGPOOL_L1;
}

// Helper function that allows to call an arbirary function with explicit values (you can move parameters from the body of the function to the args line)
// returns the return value of the called method, or 0 in case of methods that doesnt return anything
function callFunctionWithParams(method f, env e, address l1AToken, uint256 l2Recipient, address recipient, uint256 amount) returns uint256{
        address messagingContract; address incentivesController; uint16 referralCode; uint256 l2Bridge;
        bool fromUnderlyingAsset; bool toUnderlyingAsset;  uint256 l2RewardsIndex;
        uint256 staticAmount; uint256 l2sender;
        address[] l1Tokens;
        uint256[] l2Tokens;

	if (f.selector == initialize(uint256, address, address, address[], uint256[]).selector) {
		initialize(e, l2Bridge, messagingContract, incentivesController, l1Tokens, l2Tokens);
        return 0;
	} else if (f.selector == deposit(address, uint256, uint256, uint16, bool).selector) {
		uint256 result = deposit(e, l1AToken, l2Recipient, amount, referralCode, fromUnderlyingAsset);
        return result;
	} else if (f.selector == withdraw(address, uint256, address, uint256, uint256, bool).selector) {
		withdraw(e, l1AToken, l2sender, recipient, staticAmount, l2RewardsIndex, toUnderlyingAsset);
        return 0;
	} else if  (f.selector == updateL2State(address).selector) {
        updateL2State(e, l1AToken);
        return 0;
	} else if (f.selector == receiveRewards(uint256, address, uint256).selector) {
		receiveRewards(e, l2sender, recipient, amount);
        return 0;
	} else {
        calldataarg args;
        f(e, args);
        return 0;
    }
}