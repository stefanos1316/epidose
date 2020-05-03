"""
Reference implementation of DP3T client database
"""

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

from peewee import BigIntegerField, IntegerField, Model, SqliteDatabase
from time import time

#################################
### GLOBAL PROTOCOL CONSTANTS ###
#################################

DATABASE_PATH = "/var/lib/dp3t/database.db"

EPOCH_START = 0

db = SqliteDatabase(None)


class BaseModel(Model):
    class Meta:
        database = db


class State(BaseModel):
    singleton = IntegerField(default=1, unique=True)
    # Time (in seconds since Epoch) ephid was last changed
    last_ephid_change = BigIntegerField()


class Singleton(type):
    """Ensure single object creation
    See: https://stackoverflow.com/a/6798042/20520
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class ClientDatabase(metaclass=Singleton):
    """Simple reference implementation of the client database."""

    def __init__(self, db_path=DATABASE_PATH):
        """Setup the database access and schema."""

        db.init(db_path)
        db.create_tables([State])
        self.state, created = State.get_or_create(
            singleton=0, last_ephid_change=EPOCH_START
        )

    def get_last_ephid_change(self):
        """Return the last time the ephemeral id was changed."""
        return self.state.last_ephid_change

    def set_last_ephid_change(self, t=time()):
        """Set ephid change time to the specified (default current) time."""
        self.state.last_ephid_change = t
        self.state.save()
