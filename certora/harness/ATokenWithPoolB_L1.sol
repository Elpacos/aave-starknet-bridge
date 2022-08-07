// SPDX-License-Identifier: agpl-3.0
pragma solidity 0.8.10;

import {ATokenWithPoolImpl} from "./ATokenWithPoolImpl.sol";
import {ILendingPool} from "../../contracts/l1/interfaces/ILendingPool.sol";
import "./DummyERC20ExtendedImpl.sol";

contract ATokenWithPoolB_L1 is ATokenWithPoolImpl {
    constructor(ILendingPool _POOL, address owner_)
        ATokenWithPoolImpl( _POOL, owner_)
    {}
}

