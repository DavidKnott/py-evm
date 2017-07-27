import os
import pytest
from evm.db.backends.memory import MemoryDB
from evm.db import (
    get_db_backend,
)


pytest.importorskip('leveldb') 
# Sets db backend to leveldb
@pytest.fixture
def config_env(monkeypatch):
    monkeypatch.setenv('CHAIN_DB_BACKEND_CLASS',
                        'evm.db.backends.level.LevelDB')

@pytest.fixture()
def temporary_dir(tmpdir):
    _temporary_dir = str(tmpdir.mkdir("temporary-dir"))
    return _temporary_dir

@pytest.fixture
def memory_db():
    return MemoryDB()


def test_raises_if_db_path_is_not_specified(config_env):
    with pytest.raises(TypeError): get_db_backend()

def test_set_and_get(config_env, temporary_dir, memory_db):
    get_db_backend(db_path=temporary_dir).set(b'1', b'1')
    memory_db.set(b'1', b'1') 
    assert get_db_backend(db_path=temporary_dir).get(b'1') == memory_db.get(b'1') 

def test_set_on_existing_value(config_env, temporary_dir, memory_db):
    get_db_backend(db_path=temporary_dir).set(b'1', b'2') == memory_db.set(b'1', b'2') 
    assert get_db_backend(db_path=temporary_dir).get(b'1') == memory_db.get(b'1')

def test_exists(config_env, temporary_dir, memory_db):
    memory_db.set(b'1', b'1') 
    assert get_db_backend(db_path=temporary_dir).exists(b'1') == memory_db.exists(b'1')

def test_delete(config_env, temporary_dir, memory_db):
    memory_db.set(b'1', b'1')
    get_db_backend(db_path=temporary_dir).delete(b'1')
    memory_db.delete(b'1')
    assert get_db_backend(db_path=temporary_dir).exists(b'1') == memory_db.exists(b'1')

def test_snapshot_and_revert(config_env, temporary_dir):
    snapshot = get_db_backend(db_path=temporary_dir).snapshot()
    get_db_backend(db_path=temporary_dir).set(b'1', b'1')
    assert get_db_backend(db_path=temporary_dir).get(b'1')
    with pytest.raises(KeyError): snapshot.get(b'1')
    get_db_backend(db_path=temporary_dir).revert(snapshot)
    with pytest.raises(KeyError): get_db_backend(db_path=temporary_dir).get(b'1')
