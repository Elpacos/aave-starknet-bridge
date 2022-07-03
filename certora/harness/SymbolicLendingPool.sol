pragma solidity 0.8.10;
pragma experimental ABIEncoderV2;

import {IERC20} from '@aave/core-v3/contracts/dependencies/openzeppelin/contracts/IERC20.sol';
import {IAToken} from "../../contracts/l1/interfaces/IAToken.sol";

contract SymbolicLendingPool {

    mapping(address => address) public assetToAToken;
    uint256 public liquidityIndex = 1; //TODO 

    function deposit(
    address asset,
    uint256 amount,
    address onBehalfOf,
    uint16 referralCode
  ) external {
    IERC20(asset).transferFrom(msg.sender, assetToAToken[asset], amount);
    IAToken(assetToAToken[asset]).mint(onBehalfOf, amount,liquidityIndex );
  }

  function withdraw(
    address asset,
    uint256 amount,
    address to
  ) external  returns (uint256) {
    
    IAToken(assetToAToken[asset]).burn(msg.sender, to, amount, liquidityIndex);
    return amount;
  }
  
  function getReserveNormalizedIncome(address asset)
    external
    view
    virtual
    returns (uint256) {
      return liquidityIndex;
    }
} 