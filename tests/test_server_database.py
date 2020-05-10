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

from dp3t.protocols.server_database import ServerDatabase
from dp3t.protocols.unlinkable import epoch_from_time
import pytest
from datetime import datetime, timezone


############################
### TEST SERVER DATABASE ###
############################


@pytest.fixture(scope="function")
def db_connection():
    d = ServerDatabase(":memory:")
    yield d
    d.close()


def test_get_epoch_seeds_empty(db_connection):
    for (epoch, seed) in db_connection.get_epoch_seeds():
        assert False


def test_add_get_epoch_seeds(db_connection):
    for i in range(1, 10):
        db_connection.add_epoch_seed(i, f"S{i}")
    count = 1
    for (epoch, seed) in db_connection.get_epoch_seeds():
        assert epoch == count
        assert seed == bytes(f"S{count}", encoding="ascii")
        count += 1
    assert count == 10


def test_delete_epoch_seeds(db_connection):
    time_out = datetime(2020, 4, 25, 20, 59, tzinfo=timezone.utc)
    time_in = datetime(2020, 4, 25, 21, 1, tzinfo=timezone.utc)
    db_connection.add_epoch_seed(epoch_from_time(time_out), "out")
    db_connection.add_epoch_seed(epoch_from_time(time_in), "in")

    all_records = db_connection.get_epoch_seeds()
    assert sum(1 for _ in all_records) == 2

    db_connection.delete_expired_data(
        datetime(2020, 4, 25, 21, 00, tzinfo=timezone.utc)
    )

    all_records = db_connection.get_epoch_seeds()
    for (epoch, seed) in all_records:
        assert epoch == epoch_from_time(time_in)
        assert seed == b"in"
