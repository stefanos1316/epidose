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
import subprocess

FOUND = "E18901F5E514C82F03F039F2C43503D32F24DF988BC5E9CA4F3F9B307EA62A1B"
NOTFOUND = "A18901F5E514C82F03F039F2C43503D32F24DF988BC5E9CA4F3F9B307EA62A1B"


def script_path(script):
    """Return the full path of a script in the examples directory.
    """
    return Path(__file__).parent.parent / "examples" / script


def data_path(file_name):
    """Return the full path of a test data file in the test-data directory.
    """
    return Path(__file__).parent.parent / "test-data" / file_name


def test_round_trip():
    r = subprocess.check_output(
        [
            script_path("create_filter.py"),
            "-d",
            "-s",
            data_path("epoch-seeds"),
            "/tmp/cuckoo-filter.bin",
        ]
    )
    assert r == b"120\n"  # Reported capacity

    r = subprocess.run(
        [
            script_path("check-infection-risk.py"),
            "-d",
            "-o",
            FOUND,
            "/tmp/cuckoo-filter.bin",
            "120",
        ]
    )
    assert r.returncode == 0  # Found

    r = subprocess.run(
        [
            script_path("check-infection-risk.py"),
            "-d",
            "-o",
            NOTFOUND,
            "/tmp/cuckoo-filter.bin",
            "120",
        ]
    )
    assert r.returncode == 1  # Not found
