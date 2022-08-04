pragma solidity 0.8.10;
pragma experimental ABIEncoderV2;

import {IERC20} from "@aave/core-v3/contracts/dependencies/openzeppelin/contracts/IERC20.sol";
import {IAToken} from "../../contracts/l1/interfaces/IAToken.sol";

contract SymbolicLendingPoolL1 {
    mapping(address => address) public underlyingAssetToAToken_L1;
    uint256 public liquidityIndex; 

    /**
     * @dev Deposits underlying token in the Atoken's contract on behalf of the user,
            and mints Atoken on behalf of the user in return.
     * @param asset The underlying sent by the user and to which Atoken shall be minted
     * @param amount The amount of underlying token sent by the user
     * @param onBehalfOf The recipient of the minted Atokens
     * @param referralCode A unique code
     **/
    function deposit(
        address asset,
        uint256 amount,
        address onBehalfOf,
        uint16 referralCode
    ) external {
        IERC20(asset).transferFrom(
            msg.sender,
            underlyingAssetToAToken_L1[asset],
            amount
        );
        IAToken(underlyingAssetToAToken_L1[asset]).mint(
            onBehalfOf,
            amount,
            liquidityIndex
        );
    }

    /**
     * @dev Burns Atokens in exchange for underlying asset
     * @param asset The underlying asset to which the Atoken is connected
     * @param amount The amount of Atokens to be burned
     * @param to The recipient of the burned Atokens
     * @return The `amount` of tokens withdrawn
     **/
    function withdraw(
        address asset,
        uint256 amount,
        address to
    ) external returns (uint256) {
        IAToken(underlyingAssetToAToken_L1[asset]).burn(
            msg.sender,
            to,
            amount,
            liquidityIndex
        );
        return amount;
    }

    /**
     * @dev A simplification returning a constant
     * @param asset The underlying asset to which the Atoken is connected
     * @return liquidityIndex the `liquidityIndex`
     **/
    function getReserveNormalizedIncome(address asset)
        external
        view
        virtual
        returns (uint256)
    {
        return liquidityIndex;
    }

    function underlyingtoAToken(address asset) external view
    returns(address){
        return underlyingAssetToAToken_L1[asset];
    }
}
