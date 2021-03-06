import pytest

import rlp

from eth_utils import (
    to_canonical_address,
)

import os

from trie.db.memory import (
    MemoryDB,
)

from eth_utils import (
    keccak,
)

from evm.exceptions import (
    ValidationError,
)
from evm.rlp.headers import (
    BlockHeader,
)
from evm.vm.flavors import (
    MainnetEVM,
)

from evm.utils.fixture_tests import (
    find_fixtures,
    normalize_transactiontest_fixture,
    normalize_signed_transaction,
)


ROOT_PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


BASE_FIXTURE_PATH = os.path.join(ROOT_PROJECT_DIR, 'fixtures', 'TransactionTests')


def transaction_fixture_skip_fn(fixture_path, fixture_name, fixture):
    # TODO: enable all fixture tests
    return "ttTransactionTest.json" not in fixture_path


FIXTURES = find_fixtures(
    BASE_FIXTURE_PATH,
    normalize_transactiontest_fixture,
    transaction_fixture_skip_fn,
)


def test_transaction_fixtures_smoke_test():
    assert FIXTURES


@pytest.mark.parametrize(
    'fixture_name,fixture', FIXTURES,
)
def test_transaction_fixtures(fixture_name, fixture):
    header = BlockHeader(1, fixture.get('blocknumber', 0), 100)
    evm = MainnetEVM(MemoryDB(), header=header)
    vm = evm.get_vm()
    TransactionClass = vm.get_transaction_class()

    if 'sender' in fixture:
        transaction = rlp.decode(fixture['rlp'], sedes=TransactionClass)
        expected = normalize_signed_transaction(fixture['transaction'])

        assert transaction.nonce == expected['nonce']
        assert transaction.gas_price == expected['gasPrice']
        assert transaction.gas == expected['gasLimit']
        assert transaction.to == expected['to']
        assert transaction.value == expected['value']
        assert transaction.data == expected['data']
        assert transaction.v == expected['v']
        assert transaction.r == expected['r']
        assert transaction.s == expected['s']

        sender = to_canonical_address(fixture['sender'])

        assert transaction.sender == sender
    else:
        # check RLP correctness
        try:
            transaction = rlp.decode(fixture['rlp'], sedes=TransactionClass)
        except rlp.exceptions.ObjectDeserializationError:
            return

        # check parameter correctness
        try:
            transaction.validate()
        except ValidationError:
            return
