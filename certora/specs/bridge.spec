import "erc20.spec"

// Declaring aliases for contracts according to the format:
// using Target_Contract as Alias_Name
using DummyERC20UnderlyingA_L1 as UNDERLYING_ASSET_A 
using DummyERC20UnderlyingB_L1 as UNDERLYING_ASSET_B
using ATokenWithPoolA_L1 as ATOKEN_A
using ATokenWithPoolB_L1 as ATOKEN_B
using DummyERC20RewardToken_L1 as REWARD_TOKEN
using SymbolicLendingPoolL1 as LENDINGPOOL_L1
// For referencing structs
using BridgeHarness as Bridge

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
    getLendingPoolOfAToken(address) returns (address) envfree //(ILendingPool)
    _staticToDynamicAmount_Wrapper(uint256, address, address) envfree //(ILendingPool)
    _computeRewardsDiff_Wrapper(uint256, uint256, uint256) envfree
    _getCurrentRewardsIndex_Wrapper(address)

/******************************
 *     IStarknetMessaging     *
 ******************************/
    // These methods' return values are never used, and they do not change the bridges state variables.
    // Therefore havocing is an over-approximation that should not harm verification of Bridge.sol
    sendMessageToL2(uint256, uint256, uint256[]) returns (bytes32) => NONDET
    consumeMessageFromL2(uint256, uint256[]) returns (bytes32) => NONDET

/************************
 *     ILendingPool     *
 ************************/
    // The lending pool used in the contract is encapsulated within a struct in IBridge.sol.
    // We point to direct calls to these methods using dispatchers. 
    deposit(address, uint256, address, uint16) => DISPATCHER(true)
    withdraw(address, uint256, address) returns (uint256) => DISPATCHER(true)
    getReserveNormalizedIncome(address) returns (uint256) => DISPATCHER(true)

/*************************************************
 *     IATokenWithPool + IScaledBalanceToken     *
 *************************************************/
    mint(address, uint256, uint256) returns (bool) => DISPATCHER(true)
    burn(address,address, uint256, uint256) => DISPATCHER(true)
    POOL() returns (address) envfree => DISPATCHER(true)
    scaledTotalSupply() returns (uint256) envfree => DISPATCHER(true)
    UNDERLYING_ASSET_ADDRESS() => NONDET // just to remove red warning
    getIncentivesController() => NONDET

/************************************
 *     IncentivesControllerMock     *
 ************************************/
    REWARD_TOKEN() returns (address) envfree
    DISTRIBUTION_END() returns (uint256) envfree
    getRewardsVault() returns (address) envfree
    getAssetData(address) returns (uint256, uint256, uint256) envfree
    // Note that the sender of the funds here is RewardsVault which is arbitrary by default.
    // If any rule that count on the reward token balance, calls this method a `require RewardsVault != to` make sense to add
    claimRewards(address[], uint256, address) returns (uint256)
}

// Linkning the instances of ERC20 and LendingPool within the ATokenData struct to the corresponding symbolic contracts
function setLinkage(address AToken){
    // Setting the underlying token of the given AToken as either UNDERLYING_ASSET_A or UNDERLYING_ASSET_B
    require getUnderlyingAssetOfAToken(AToken) == UNDERLYING_ASSET_A || getUnderlyingAssetOfAToken(AToken) == UNDERLYING_ASSET_B;
    require getLendingPoolOfAToken(AToken) == LENDINGPOOL_L1
    ;
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

rule sanity(method f)
{
	env e;
	calldataarg args;
	f(e,args);
	assert false;
}

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
    setLinkage(aToken);
    address underlying = getUnderlyingAssetOfAToken(aToken);
    uint256 underlyingBalanceBefore = tokenBalanceOf(e, underlying, recipient);
    uint256 aTokenBalanceBefore = tokenBalanceOf(e, aToken, recipient);
    uint256 rewardTokenBalanceBefore = tokenBalanceOf(e, REWARD_TOKEN, recipient);

    withdraw(e, aToken, l2sender, recipient, staticAmount, l2RewardsIndex, toUnderlyingAsset);

    uint256 underlyingBalanceAfter = tokenBalanceOf(e, underlying, recipient);
    uint256 aTokenBalanceAfter = tokenBalanceOf(e, aToken, recipient);
    uint256 rewardTokenBalanceAfter = tokenBalanceOf(e, REWARD_TOKEN, recipient);

    if (toUnderlyingAsset){
        assert underlyingBalanceAfter == underlyingBalanceBefore + _staticToDynamicAmount_Wrapper(staticAmount, underlying, LENDINGPOOL_L1);
    }
    else {
        assert aTokenBalanceAfter == aTokenBalanceBefore + _staticToDynamicAmount_Wrapper(staticAmount, underlying, LENDINGPOOL_L1);
    }
    assert true;
    // assert rewardTokenBalanceAfter == rewardTokenBalanceBefore + _computeRewardsDiff_Wrapper(staticAmount, l2RewardsIndex, _getCurrentRewardsIndex_Wrapper(e, aToken));
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

rule balanceOfUnderlyingAssetChanged(method f, address u, address aToken) {
    env eB;
    env eF;
    calldataarg args;
    setLinkage(aToken);
    address underlying  = getUnderlyingAssetOfAToken(aToken);
    uint256 underlyingBalanceBefore = tokenBalanceOf(eB, underlying, u);
    
    address aToken2; uint256 l2Recipient; address recipient; uint256 amount;

    callFunctionWithParams(f, eF, aToken2, l2Recipient, recipient, amount);
    // f(eF, args);

    uint256 underlyingBalanceAfter = tokenBalanceOf(eB, underlying, u);
    assert (underlyingBalanceAfter == underlyingBalanceBefore
            => f.selector != deposit(address, uint256, uint256, uint16, bool).selector 
            || f.selector != withdraw(address, uint256, address, uint256, uint256, bool).selector), "balanceOf changed";
    assert (f.selector != deposit(address, uint256, uint256, uint16, bool).selector 
            && f.selector != withdraw(address, uint256, address, uint256, uint256, bool).selector 
            => underlyingBalanceAfter == underlyingBalanceBefore), "balanceOf due to unauthorized method";
}
