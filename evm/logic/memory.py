from toolz import (
    partial,
)

from evm import constants

from evm.utils.padding import (
    pad_left,
)


def mstore_XX(computation, size):
    start_position = computation.stack.pop(type_hint=constants.UINT256)
    value = computation.stack.pop(type_hint=constants.BYTES)

    padded_value = pad_left(value, size, b'\x00')
    normalized_value = padded_value[-1 * size:]

    computation.extend_memory(start_position, size)

    computation.memory.write(start_position, size, normalized_value)


mstore = partial(mstore_XX, size=32)
mstore8 = partial(mstore_XX, size=1)


def mload(computation):
    start_position = computation.stack.pop(type_hint=constants.UINT256)

    computation.extend_memory(start_position, 32)

    value = computation.memory.read(start_position, 32)
    computation.stack.push(value)


def msize(computation):
    computation.stack.push(len(computation.memory))