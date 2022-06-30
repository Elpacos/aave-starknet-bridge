certoraRun contracts/l1/Bridge.sol:Bridge \
    --verify Bridge:certora/specs/complexity.spec \
    --solc solc8.10 \
    --optimistic_loop \
    --staging  \
    --msg "Bridge complexity check"
