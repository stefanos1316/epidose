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

from epidose.back_end import ha_server
from flask import json
import pytest
import types


####################################
### TEST HEALTH AUTHORITY SERVER ###
####################################


@pytest.fixture(scope="function")
def client():
    args = types.SimpleNamespace()
    args.database = ":memory:"
    args.debug = True
    args.verbose = True
    with ha_server.app.test_client() as client:
        ha_server.app.config["TESTING"] = True
        with ha_server.app.app_context():
            ha_server.initialize(args)
        yield client
    ha_server.db.close()


def to_json(response):
    """ Return a response as JSON. """
    assert response.status_code == 200
    return json.loads(response.get_data(as_text=True))


def test_version(client):
    rv = client.get("/version")
    assert to_json(rv)["version"] == ha_server.API_VERSION


def test_add_contagious(client):
    rv = client.post(
        "/add_contagious",
        json={
            "authorization": "xyzzy",
            "data": [
                {"epoch": 42, "seed": "deadbeef"},
                {"epoch": 43, "seed": "baadf00d"},
            ],
        },
    )
    assert rv.status_code == 200
    seeds = {}
    count = 0
    for (epoch, seed) in ha_server.db.get_epoch_seeds():
        seeds[epoch] = seed
        count += 1
    assert count == 2
    assert seeds[42] == bytes.fromhex("deadbeef")
    assert seeds[43] == bytes.fromhex("baadf00d")
