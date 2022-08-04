certoraRun certora/harness/BridgeHarness.sol certora/harness/DummyERC20UnderlyingA_L1.sol certora/harness/DummyERC20UnderlyingB_L1.sol certora/harness/DummyERC20RewardToken.sol certora/harness/SymbolicLendingPoolL1.sol certora/harness/IncentivesControllerMock_L1.sol certora/harness/ATokenWithPoolA_L1.sol certora/harness/ATokenWithPoolB_L1.sol certora/harness/StaticATokenA_L2.sol certora/harness/StaticATokenB_L2.sol certora/harness/BridgeL2Harness.sol \
            --verify BridgeHarness:certora/specs/bridge.spec \
            --link  BridgeHarness:_rewardToken=DummyERC20RewardToken \
                    BridgeHarness:_incentivesController=IncentivesControllerMock_L1 \
                    BridgeHarness:BRIDGE_L2=BridgeL2Harness \
                    IncentivesControllerMock_L1:_rewardToken=DummyERC20RewardToken \
                    ATokenWithPoolA_L1:POOL=SymbolicLendingPoolL1 \
                    ATokenWithPoolA_L1:INCENTIVES_CONTROLLER=IncentivesControllerMock_L1 \
                    ATokenWithPoolB_L1:POOL=SymbolicLendingPoolL1 \
                    ATokenWithPoolB_L1:INCENTIVES_CONTROLLER=IncentivesControllerMock_L1 \
                    BridgeL2Harness:BRIDGE_L1=BridgeHarness \
                    BridgeL2Harness:REW_AAVE=DummyERC20RewardToken \
            --solc solc8.10 \
            --optimistic_loop \
            --loop_iter 9 \
            --send_only \
            --rule_sanity basic \
            --staging \
            --rule depositWithdrawReversed \
            --msg "Bridge depositWithdrawReversed"

# The first line (#6) specifies all the contracts that are being called through the bridge.sol file.
# This is a declaration of multiple contracts for the verification context.

# The second line (#7) is of the form Contract:SPEC, and it is a specification of the main contract to be verified and the spec to check this contract against.

# The next few lines (#8-#9) are under the --link flag which specifies links for vars which are instances of other contracts.
# It written in the form: < Contract_Where_The_Instance_Appear > : < Name_Of_Instance_Var_In_This_Contract > : < Target_Contract_To_Link_The_Calls_To >

# The --solc flag specifies the solc that the prover needs to use in verification. It has to be correlated with the pragma line of the contract.
# The value solc8.10 is merely the name of the actual compiler file. In this case the containing directory is in $PATH.

# The --optimistic_loop flag assumes loops are executed well and nicely, even if in practice no full unrolling of the loop is being done.
# This means that a if loop of, say, fixed size 5 is in the code, and we unroll it 1 time, meaning we only execute 1 iteration, we assume that the loop condition was not breached even without executing the entire thing.

# The --loop_iter 9 flag specifies the number of times the tool unroll loops when running (can be thought of as the number of iterations executed).
# Here we neede to specify a loop_iter of 9 due to the way that the tool treat dynamic types as arrays.
# The method `_sendDepositMessage` contains payload array which is filled with 8 elements, which requires a large loop_iter.