__copyright__ = """
    Copyright 2020 Diomidis Spinellis

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""
__license__ = "Apache 2.0"

from dp3t.protocols.client_database import ClientDatabase, EPOCH_START
import pytest
from time import time


############################
### TEST CLIENT DATABASE ###
############################


@pytest.fixture(scope="function")
def db_connection():
    d = ClientDatabase(":memory:")
    yield d
    d.close()


def test_database_initialization(db_connection):
    assert db_connection.get_last_ephid_change() == EPOCH_START


def test_last_ephid_change_explicit(db_connection):
    db_connection.set_last_ephid_change(42)
    assert db_connection.get_last_ephid_change() == 42


def test_last_ephid_change_multiple(db_connection):
    db_connection.set_last_ephid_change(42)
    assert db_connection.get_last_ephid_change() == 42
    db_connection.set_last_ephid_change(80)
    assert db_connection.get_last_ephid_change() == 80


def test_last_ephid_change_default(db_connection):
    db_connection.set_last_ephid_change()
    assert abs(time() - db_connection.get_last_ephid_change()) < 10


def test_add_get_epoch_ids(db_connection):
    for i in range(1, 10):
        db_connection.add_epoch_ids(i, f"S{i}", f"E{i}")
    seeds = db_connection.get_epoch_seeds(5, 6)
    assert b"S4" not in seeds
    assert b"S5" in seeds
    assert b"S6" in seeds
    assert b"S7" not in seeds


def test_add_delete_past_epochs(db_connection):
    for i in range(1, 10):
        db_connection.add_epoch_ids(i, f"S{i}", f"E{i}")
    db_connection.delete_past_epoch_ids(5)
    seeds = db_connection.get_epoch_seeds(2, 6)
    assert b"S4" not in seeds
    assert b"S5" in seeds
