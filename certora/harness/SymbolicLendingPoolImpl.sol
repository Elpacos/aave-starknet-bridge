pragma solidity 0.8.10;
pragma experimental ABIEncoderV2;

import {IERC20} from '@aave/core-v3/contracts/dependencies/openzeppelin/contracts/IERC20.sol';
import {IAToken} from "../../contracts/l1/interfaces/IAToken.sol";

contract SymbolicLendingPoolImpl {

    address public aToken; 
    uint256 public liquidityIndex = 1; //TODO 
    uint256 public data;
    address public Asset;

    function deposit(
    address asset,
    uint256 amount,
    address onBehalfOf,
    uint16 referralCode
  ) external {
    Asset = asset;
    IERC20(Asset).transferFrom(msg.sender, aToken, amount);
    IAToken(aToken).mint(onBehalfOf, amount,liquidityIndex );
  }


  function withdraw(
    address asset,
    uint256 amount,
    address to
  ) external  returns (uint256) {
    
    IAToken(aToken).burn(msg.sender, to, amount, liquidityIndex);
    return amount;
  }
  
  function getReserveNormalizedIncome(address asset)
    external
    view
    virtual
    returns (uint256) {
      return liquidityIndex;
    }

    function finalizeTransfer(
    address asset,
    address from,
    address to,
    uint256 amount,
    uint256 balanceFromAfter,
    uint256 balanceToBefore
    ) external {
    }

    function getATokenAddress(address asset) public returns (address) {
      return aToken;
    }
} 