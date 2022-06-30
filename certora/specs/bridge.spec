import "erc20.spec"

// Declaring aliases for contracts according to the format:
// using Target_Contract as Alias_Name
using DummyERC20A as UNDERLYING_ASSET_A
using DummyERC20B as UNDERLYING_ASSET_B
using DummyERC20C as REWARD_TOKEN
using ATokenWithPoolA as ATOKEN_A
using ATokenWithPoolB as ATOKEN_B
using SymbolicLendingPoolA as LENDINGPOOL_A
using SymbolicLendingPoolB as LENDINGPOOL_B

methods {
    /**********************
     *     Bridge.sol     *
     **********************/
    deposit(address, uint256, uint16, bool) returns (uint256) 
    withdraw(address, uint256, address, uint256, uint256, bool)
    updateL2State(address)
    receiveRewards(uint256, address, uint256)
    getRevision() returns (uint256)
    _approveBridgeTokens(address[], uint256[]) 
    _approveToken(address, uint256)
    _sendDepositMessage(address, address, uint256, uint256, uint256, uint256)
    _sendIndexUpdateMessage(address, address, uint256, uint256)
    _consumeMessage(address, uint256, address, uint256, uint256)
    // _dynamicToStaticAmount(uint256, address, ILendingPool) returns (uint256)
    // _staticToDynamicAmount(uint256, address, ILendingPool) returns (uint256)
    _getCurrentRewardsIndex(address) returns (uint256)
    _computeRewardsDiff(uint256, uint256, uint256) returns (uint256)
    _consumeBridgeRewardMessage(uint256, address, uint256)
    _transferRewards(address, uint256)

    /******************************
     *     IStarknetMessaging     *
     ******************************/
    // These methods' return values are never used, and they do not change the bridges state variables.
    // Therefore havocing is an over-approximation that should not harm verification of Bridge.sol
    sendMessageToL2(uint256, uint256, uint256[]) returns (bytes32) => HAVOC_ECF
    consumeMessageFromL2(uint256, uint256[]) returns (bytes32) => HAVOC_ECF

    /*******************************
     *     IScaledBalanceToken     *
     *******************************/
    // 
    scaledTotalSupply() returns (uint256) => 

    /************************
     *     ILendingPool     *
     ************************/
    // The lending pool used in the contract is encapsulated within a struct in IBridge.sol.
    // We point to direct calls to these methods using dispatchers. 
    deposit(address, uint256, address, uint16) => DISPATCHER(true)
    withdraw(address, uint256, address) returns (uint256) => DISPATCHER(true)
    getReserveNormalizedIncome(address) returns (uint256) => DISPATCHER(true)

    /*************************
     *     BridgeHarness     *
     *************************/
    // Not that these methods return the contract types that are written in comment to their right.
    // In CVL we contracts are addresses an therefore we demand return of an address
    getUnderlyingAssetOfAToken(address) returns (address) envfree //(IERC20)
    getLendingPoolOfAToken(address) returns (address) envfree //(ILendingPool)

    /************************************
     *     IncentivesControllerMock     *
     ************************************/
    REWARD_TOKEN() returns (address) envfree
    DISTRIBUTION_END() returns (uint256) envfree
    getRewardsVault() returns (address) envfree
    getAssetData(address) returns (uint256, uint256, uint256) envfree
    // Note that the sender of the funds here is RewardsVault which is arbitrary by default.
    // If any rule that count on the reward token balance, calls this method a require RewardsVault != to make sense to add
    claimRewards(address[], uint256, address) returns (uint256)
}

// Linkning the instances of ERC20 and LendingPool within the ATokenData struct the corresponding AToken to specific symbolic contract
// The if-else structure allows setting each AToken with a desired underlying asset and lending pool so that 2 ATokens can be compared.
function setLinkage(address AToken, uint8 underlyingContract, uint8 poolContract){
    // Setting the underlying token of the given AToken as either UNDERLYING_ASSET_A or UNDERLYING_ASSET_B
    if (underlyingContract == 1){
        require getUnderlyingAssetOfAToken(AToken) == UNDERLYING_ASSET_A;
        require ATOKEN_A.UNDERLYING_ASSET_ADDRESS() == UNDERLYING_ASSET_A;
    }
    else{
        require getUnderlyingAssetOfAToken(AToken) == UNDERLYING_ASSET_B;
        require ATOKEN_B.UNDERLYING_ASSET_ADDRESS() == UNDERLYING_ASSET_B;
    }

    // Setting the underlying token of the given AToken as either LENDINGPOOL_A or LENDINGPOOL_B
    if (poolContract == 1){
        require getLendingPoolOfAToken(AToken) == LENDINGPOOL_A;
        require ATOKEN_A.POOL() == LENDINGPOOL_A;
    }
    else{
        require getLendingPoolOfAToken(AToken) == LENDINGPOOL_B;
        require ATOKEN_B.POOL() == LENDINGPOOL_B;
    }
}

function setTotalSupplyScale(uint256 ratio) returns uint256 {

}

rule sanity(method f)
{
	env e;
	calldataarg args;
	f(e,args);
	assert false;
}


/*
This rule find which functions never reverts.

*/


rule noRevert(method f)
description "$f has reverting paths"
{
	env e;
	calldataarg arg;
	require e.msg.value == 0; 
	f@withrevert(e, arg); 
	assert !lastReverted, "${f.selector} can revert";
}


rule alwaysRevert(method f)
description "$f has reverting paths"
{
	env e;
	calldataarg arg;
	f@withrevert(e, arg); 
	assert lastReverted, "${f.selector} succeeds";
}


/*
This rule find which functions that can be called, may fail due to someone else calling a function right before.

This is n expensive rule - might fail on the demo site on big contracts
*/

rule simpleFrontRunning(method f, address privileged) filtered { f-> !f.isView }
description "$f can no longer be called after it had been called by someone else"
{
	env e1;
	calldataarg arg;
	require e1.msg.sender == privileged;  

	storage initialStorage = lastStorage;
	f(e1, arg); 
	bool firstSucceeded = !lastReverted;

	env e2;
	calldataarg arg2;
	require e2.msg.sender != e1.msg.sender;
	f(e2, arg2) at initialStorage; 
	f@withrevert(e1, arg);
	bool succeeded = !lastReverted;

	assert succeeded, "${f.selector} can be not be called if was called by someone else";
}


/*
This rule find which functions are privileged.
A function is privileged if there is only one address that can call it.

The rules finds this by finding which functions can be called by two different users.

*/


rule privilegedOperation(method f, address privileged)
description "$f can be called by more than one user without reverting"
{
	env e1;
	calldataarg arg;
	require e1.msg.sender == privileged;

	storage initialStorage = lastStorage;
	f@withrevert(e1, arg); // privileged succeeds executing candidate privileged operation.
	bool firstSucceeded = !lastReverted;

	env e2;
	calldataarg arg2;
	require e2.msg.sender != privileged;
	f@withrevert(e2, arg2) at initialStorage; // unprivileged
	bool secondSucceeded = !lastReverted;

	assert  !(firstSucceeded && secondSucceeded), "${f.selector} can be called by both ${e1.msg.sender} and ${e2.msg.sender}, so it is not privileged";
}

rule whoChangedBalanceOf(method f, address u) {
    env eB;
    env eF;
    calldataarg args;
    uint256 before = balanceOf(eB, u);
    f(eF,args);
    assert balanceOf(eB, u) == before, "balanceOf changed";
}