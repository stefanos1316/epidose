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

import argparse
from dp3t.protocols.server_database import ServerDatabase
from epidose.common.daemon import Daemon
from flask import Flask, abort, jsonify, request, send_from_directory
import logging
from os.path import basename, dirname

API_VERSION = "1"

app = Flask("ha-server")

db = None

FILTER_LOCATION = "/var/lib/epidose/filter.bin"
DATABASE_LOCATION = "/var/lib/epidose/server-database.db"


def shutdown_server():
    func = request.environ.get("werkzeug.server.shutdown")
    if func is None:
        raise RuntimeError("Not running with the Werkzeug Server")
    func()


@app.before_request
def before_request():
    global db
    if not db:
        db = ServerDatabase(DATABASE_LOCATION)
    db.connect(reuse_if_open=True)


@app.after_request
def after_request(response):
    global db
    if not app.config["TESTING"]:
        db.close()
    return response


@app.route("/filter", methods=["GET"])
def filter():
    """Send the Cuckoo filter as a static file.
    In a production deployment this should be handled by the front-end server,
    such as nginx.
    """
    return send_from_directory(dirname(FILTER_LOCATION), basename(FILTER_LOCATION))


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

    global daemon
    daemon = Daemon("ha_server", args)
    # Setup logging
    global logger
    logger = daemon.get_logger()

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

    global DATABASE_LOCATION
    parser.add_argument(
        "-D",
        "--database",
        help="Specify the database location",
        default=DATABASE_LOCATION,
    )

    global FILTER_LOCATION
    parser.add_argument(
        "-f",
        "--filter",
        help="Specify the location of the Cuckoo filter",
        default=FILTER_LOCATION,
    )
    parser.add_argument(
        "-s",
        "--server-name",
        help="Specify the server name (0.0.0.0 for externally visible)",
        default="127.0.0.1",
    )
    parser.add_argument("-p", "--port", help="Set TCP port to listen", type=int)
    parser.add_argument(
        "-v", "--verbose", help="Set verbose logging", action="store_true"
    )
    args = parser.parse_args()

    initialize(args)

    FILTER_LOCATION = args.filter
    DATABASE_LOCATION = args.database

    # Daemonize with gunicorn or other means, because the daemonize
    # module has trouble dealing with the lock files when the app
    # reloads itself.
    app.run(debug=args.debug, host=args.server_name, port=args.port)


if __name__ == "__main__":
    main()
else:
    global logger
    logger = logging.getLogger("gunicorn.error")
