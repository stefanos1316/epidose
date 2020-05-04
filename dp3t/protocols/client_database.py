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

from peewee import BigIntegerField, BlobField, IntegerField, Model, SqliteDatabase
from time import time

#################################
### GLOBAL PROTOCOL CONSTANTS ###
#################################

EPOCH_START = 0


db = SqliteDatabase(None)


class BaseModel(Model):
    class Meta:
        database = db


class State(BaseModel):
    singleton = IntegerField(default=1, unique=True)
    # Time (in seconds since Unix Epoch) ephid was last changed
    last_ephid_change = BigIntegerField()


class EpochIds(BaseModel):
    """Pairs of seeds and ephids employed per epoch by this device."""

    epoch = BigIntegerField(unique=True, primary_key=True, index=True)
    seed = BlobField()
    ephid = BlobField()


class DailyObservations(BaseModel):
    """Observations for each day."""

    # Represented as seconds since Unix Epoch to day's beginning
    day = BigIntegerField(index=True)
    # Hashed observation
    observation = BlobField()


# Available tables
MODELS = [State, EpochIds, DailyObservations]


class ClientDatabase:
    """Simple reference implementation of the client database."""

    def __init__(self, db_path=":memory:"):
        """Setup the database access and schema."""

        db.init(db_path)
        db.create_tables(MODELS)
        self.state, created = State.get_or_create(
            singleton=0, last_ephid_change=EPOCH_START
        )

    def close(self):
        """Close the dabase connection. Useful to reset state in testing."""
        db.drop_tables(MODELS)
        db.close()

    def get_last_ephid_change(self):
        """Return the last time the ephemeral id was changed."""
        return self.state.last_ephid_change

    def set_last_ephid_change(self, t=time()):
        """Set ephid change time to the specified (default current) time."""
        self.state.last_ephid_change = t
        self.state.save()

    def add_epoch_ids(self, add_epoch, add_seed, add_ephid):
        """Add the seed and ephid for the specified epoch."""
        EpochIds.create(epoch=add_epoch, seed=add_seed, ephid=add_ephid)

    def get_epoch_seeds(self, start_epoch, end_epoch):
        """Return the seeds for the specified epoch range."""
        query = EpochIds.select(EpochIds.seed).where(
            EpochIds.epoch.between(start_epoch, end_epoch - 1)
        )
        return [rec.seed for rec in query]

    def get_epoch_ephid(self, epoch):
        """Return the ephID for the specified epoch."""
        rec = EpochIds.get_or_none(EpochIds.epoch == epoch)
        if rec:
            return rec.ephid
        else:
            return None

    def delete_past_epoch_ids(self, last_retained_epoch):
        """Delete identifiers associated with past epochs."""
        query = EpochIds.delete().where(EpochIds.epoch < last_retained_epoch)
        query.execute()

    def add_observation(self, add_day, add_observation):
        """Add a hashed observation for the specified day."""
        DailyObservations.create(day=add_day, observation=add_observation)

    def get_observations(self):
        """Return as an iterable all past observations."""
        query = DailyObservations.select(DailyObservations.observation)
        return map(lambda rec: rec.observation, query)

    def delete_past_observations(self, last_retained_day):
        """Delete observations of past days."""
        query = DailyObservations.delete().where(
            DailyObservations.day < last_retained_day
        )
        query.execute()
