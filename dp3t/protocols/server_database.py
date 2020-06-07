"""
Reference implementation of DP3T server database
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

from dp3t.protocols.unlinkable import epoch_from_time

from peewee import (
    BigIntegerField,
    BlobField,
    Model,
    SqliteDatabase,
)

#################################
### GLOBAL PROTOCOL CONSTANTS ###
#################################

db = SqliteDatabase(None)


class BaseModel(Model):
    class Meta:
        database = db


class ContagiousIds(BaseModel):
    """Epochs and seeds associated with contabious users."""

    epoch = BigIntegerField(index=True)
    seed = BlobField()


# Available tables
MODELS = [ContagiousIds]


class ServerDatabase:
    """Simple reference implementation of the server database."""

    def __init__(self, db_path=":memory:"):
        """Setup the database access and schema."""

        # Deferred initialization
        db.init(db_path)

        # Create schema if needed
        db.create_tables(MODELS)

    def connect(self, reuse_if_open=False):
        """Connect to the underlying database. Return whether a new connection
        was opened."""
        ret = db.connect(reuse_if_open)
        if not db.get_tables():
            db.create_tables(MODELS)
        return ret

    def close(self, drop_tables=False):
        """Close the database connection. Useful to reset state in testing.
        Return True if the database was closed."""
        if drop_tables:
            db.drop_tables(MODELS)
        db.close()

    def atomic(self):
        """Context manager that ensures atomic operations (database transactions)."""
        return db.atomic()

    def get_epoch_seeds(self):
        """Return an iterator for the database's (epoch, seed) tuples.
        """
        return (
            ContagiousIds.select(ContagiousIds.epoch, ContagiousIds.seed)
            .tuples()
            .iterator()
        )

    def get_epoch_seeds_tuple(self):
        """Return a tuple of epochs and seeds."""
        epochs = []
        seeds = []
        for (epoch, seed) in self.get_epoch_seeds():
            epochs.append(epoch)
            seeds.append(seed)
        return (epochs, seeds)

    def add_epoch_seed(self, epoch, seed):
        """Add contagious user's epoch and seed.
        """
        ContagiousIds.create(epoch=epoch, seed=seed)

    def delete_expired_data(self, last_retained_day):
        """Delete contagious user data that has expired."""
        last_retained_epoch = epoch_from_time(last_retained_day)
        query = ContagiousIds.delete().where(ContagiousIds.epoch < last_retained_epoch)
        query.execute()
