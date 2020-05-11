#!/usr/bin/env python3

""" Health authority back end REST and static content server """

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

from flask import Flask, abort, jsonify, request
import argparse
from epidose.common import logging
from dp3t.protocols.server_database import ServerDatabase

API_VERSION = "1"

app = Flask("ha-server")

db = None


def shutdown_server():
    func = request.environ.get("werkzeug.server.shutdown")
    if func is None:
        raise RuntimeError("Not running with the Werkzeug Server")
    func()


@app.route("/shutdown")
def shutdown():
    if app.debug:
        shutdown_server()
        return "Server shutting down..."
    else:
        abort(405)


@app.route("/version", methods=["GET"])
def version():
    return jsonify({"version": API_VERSION})


@app.route("/add_contagious", methods=["POST"])
def add_contagious():
    content = request.json
    print(db)
    with db.atomic():
        logger.debug(f"Add new data with authorization {content['authorization']}")
        # TODO: Check authorization
        for rec in content["data"]:
            epoch = rec["epoch"]
            seed = bytes.fromhex(rec["seed"])
            db.add_epoch_seed(epoch, seed)
            logger.debug(f"Add {epoch} {seed.hex()}")
            # TODO: Delete authorization
        return "OK"


def initialize(args):
    """Initialize the server's database and logger. """

    print(args)
    # Setup logging
    global logger
    logger = logging.getLogger("ha_server", args)

    # Connect to the database
    global db
    db = ServerDatabase(args.database)


def main():
    parser = argparse.ArgumentParser(
        description="Health authority back end REST and static content server "
    )
    parser.add_argument(
        "-d", "--debug", help="Run in debug mode logging to stderr", action="store_true"
    )
    parser.add_argument(
        "-D",
        "--database",
        help="Specify the database location",
        default="/var/epidose/dp3t/server-database.db",
    )
    parser.add_argument("-p", "--port", help="Set TCP port to listen", type=int)
    parser.add_argument(
        "-v", "--verbose", help="Set verbose logging", action="store_true"
    )
    args = parser.parse_args()

    initialize(args)

    app.run(debug=args.debug, port=args.port)


if __name__ == "__main__":
    main()
