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

from datetime import datetime, timedelta
from dp3t.config import EPOCH_LENGTH
from dp3t.protocols.client_database import ClientDatabase
from dp3t.protocols.server_database import ServerDatabase
from dp3t.protocols.unlinkable import epoch_from_time
from os import close, remove
from pathlib import Path
import pytest
import requests
import subprocess
from tempfile import mkstemp
from time import sleep


# A start time within the retention period
START_TIME = datetime.utcnow() - timedelta(days=2)
SERVER_URL = "http://127.0.0.1:5000"


###################
### TEST UPLOAD ###
###################


def script_path(script):
    """Return the full path of a script in the epidose/ directory. """
    return Path(__file__).parent.parent / "epidose" / script


@pytest.fixture
def test_context():
    # Initialize client database
    (client_db_handle, client_db_path) = mkstemp()
    close(client_db_handle)
    client_db = ClientDatabase(client_db_path)

    # Add seeds to the client database
    for i in range(0, 10):
        e = epoch_from_time(START_TIME + timedelta(minutes=i * EPOCH_LENGTH))
        client_db.add_epoch_ids(e, bytes.fromhex(f"deadbeef0{i}"), f"E{i}")
    close(client_db_handle)
    # subprocess.call(["/home/dds/src/epidose/utils/client-db-report.sh", client_db_path])

    # Instantiate the back-end server
    (server_db_handle, server_db_path) = mkstemp()
    close(server_db_handle)
    server_proc = subprocess.Popen(
        [script_path("back_end/ha_server.py"), "-d", "-v", "-D", server_db_path]
    )

    # Wait for server to come up
    count = 0
    while True:
        try:
            res = requests.get(f"{SERVER_URL}/version")
            if res.ok:
                break
        except requests.exceptions.ConnectionError:
            pass
        sleep(0.1)
        count += 0.1
        # Timeout after 5s
        if count > 5:
            raise TimeoutError

    server_db = ServerDatabase(server_db_path)

    yield (client_db_path, server_db)
    # Shutdown the server
    res = requests.get(f"{SERVER_URL}/shutdown")
    assert res.ok

    # Wait for the server to finish
    server_proc.wait()

    # Cleanup
    server_db.close()
    remove(server_db_path)
    remove(client_db_path)


def test_upload_seeds(test_context):
    (client_db_path, server_db) = test_context

    # Upload contacts from database
    client_proc = subprocess.run(
        [
            script_path("device/upload_seeds.py"),
            "-d",
            "-D",
            client_db_path,
            "-s",
            SERVER_URL,
            "-v",
            (START_TIME + timedelta(minutes=2 * EPOCH_LENGTH)).isoformat(),
            (START_TIME + timedelta(minutes=8 * EPOCH_LENGTH)).isoformat(),
        ]
    )
    assert client_proc.returncode == 0

    # See if they arrived in the server database
    (epochs, seeds) = server_db.get_epoch_seeds_tuple()
    assert (
        epoch_from_time(START_TIME + timedelta(minutes=2 * EPOCH_LENGTH)) - 1
        not in epochs
    )
    assert epoch_from_time(START_TIME + timedelta(minutes=2 * EPOCH_LENGTH)) in epochs
    assert epoch_from_time(START_TIME + timedelta(minutes=8 * EPOCH_LENGTH)) in epochs
    assert (
        epoch_from_time(START_TIME + timedelta(minutes=8 * EPOCH_LENGTH)) + 1
        not in epochs
    )
    assert bytes.fromhex("deadbeef06") in seeds
