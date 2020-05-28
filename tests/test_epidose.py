__copyright__ = """
    Copyright 2020 EPFL, Diomidis Spinellis

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

from pathlib import Path
from os import close, unlink
from time import sleep
import requests
from tempfile import mkstemp
import subprocess

FOUND = "E18901F5E514C82F03F039F2C43503D32F24DF988BC5E9CA4F3F9B307EA62A1B"
NOTFOUND = "A18901F5E514C82F03F039F2C43503D32F24DF988BC5E9CA4F3F9B307EA62A1B"

SERVER_URL = "http://127.0.0.1"
SERVER_PORT = "5001"
SERVER_URL = f"{SERVER_URL}:{SERVER_PORT}"


def script_path(script):
    """Return the full path of a script in the epidose/ directory.
    """
    return Path(__file__).parent.parent / "epidose" / script


def data_path(file_name):
    """Return the full path of a test data file in the test-data directory.
    """
    return Path(__file__).parent.parent / "test-data" / file_name


beacon_scripts = (Path(__file__).parent.parent / "epidose/device").glob("b*.py")


def test_round_trip():
    # Create the Cuckoo filter
    handle, server_filter_name = mkstemp(prefix="server-")
    close(handle)
    r = subprocess.check_output(
        [
            script_path("back_end/create_filter.py"),
            "-d",
            "-s",
            data_path("epoch-seeds"),
            server_filter_name,
        ]
    )

    # Instantiate the back-end server
    (server_db_handle, server_db_path) = mkstemp()
    close(server_db_handle)
    server_proc = subprocess.Popen(
        [
            script_path("back_end/ha_server.py"),
            "-d",
            "-f",
            server_filter_name,
            "-p",
            SERVER_PORT,
            "-v",
            "-D",
            server_db_path,
        ]
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

    # Obtain the Cuckoo filter from the server
    handle, client_filter_name = mkstemp(prefix="client-")
    close(handle)
    r = requests.get(f"{SERVER_URL}/filter", allow_redirects=True)
    open(client_filter_name, "wb").write(r.content)

    # Shutdown the server
    res = requests.get(f"{SERVER_URL}/shutdown")
    assert res.ok

    # Wait for the server to finish
    server_proc.wait()

    r = subprocess.run(
        [
            script_path("device/check_infection_risk.py"),
            "-d",
            "-o",
            FOUND,
            client_filter_name,
        ]
    )
    assert r.returncode == 0  # Found

    r = subprocess.run(
        [
            script_path("device/check_infection_risk.py"),
            "-d",
            "-o",
            NOTFOUND,
            client_filter_name,
        ]
    )
    assert r.returncode == 1  # Not found

    unlink(server_filter_name)
    unlink(client_filter_name)
