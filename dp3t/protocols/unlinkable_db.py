"""
Reference implementation of the database-based unlinkable DP3T design
"""

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

from datetime import datetime, timedelta

from cuckoo.filter import BCuckooFilter

from dp3t.config import RETENTION_PERIOD, NUM_EPOCHS_PER_DAY

from dp3t.protocols.client_database import ClientDatabase

from dp3t.protocols.unlinkable import (
    CUCKOO_FPR,
    ephid_from_seed,
    epoch_from_time,
    generate_new_seed,
    hashed_observation_from_ephid,
    hashed_observation_from_seed,
)

from os import path

#############################################################
### TYING CRYPTO FUNCTIONS TOGETHER FOR TRACING/RECORDING ###
#############################################################


def day_timestamp(date):
    """Return a Unix timestamp for the day associated with the given date.
    We define this as the time at which the day begins."""
    return int(datetime.combine(date, datetime.min.time()).timestamp())


class TracingDataBatch:
    """
    Simple representation of a batch of keys that is downloaded from
    the backend server to the phone at regular intervals.

    Contrary to the low-cost design, the release time is not needed to prevent
    replay attacks.

    *Example only.* This data structure uses a simple Python cuckoo filter to
    hold the hashed observations. We did not thoroughly check this library.
    Final implementations must at the very least use a portable and
    well-specified version of such a cuckoo filter.
    """

    def __init__(self, tracing_seeds=None, release_time=None, file_path=None):
        """Create a published batch of tracing keys

        Args:
            tracing_seeds ([(reported_epochs, seeds)]): A list of reported epochs/seeds
                per infected user
            release_time (optional): Release time of this batch
        """

        if tracing_seeds and file_path:
            raise ValueError("Must specify only one of tracing_seeds or file_path")

        if tracing_seeds:
            # Compute size of filter and ensure we have enough capacity
            nr_items = sum([len(epochs) for (epochs, _) in tracing_seeds])
            self.capacity = int(nr_items * 1.2)

            self.infected_observations = BCuckooFilter(
                self.capacity, error_rate=CUCKOO_FPR
            )
            for (epochs, seeds) in tracing_seeds:
                for (epoch, seed) in zip(epochs, seeds):
                    self.infected_observations.insert(
                        hashed_observation_from_seed(seed, epoch)
                    )
        elif file_path:
            self.file_size = path.getsize(file_path)
            # TODO Create filter from file
            pass
        else:
            raise ValueError("Must specify at least one of tracing_seeds or file_path")

        self.release_time = release_time

    def tofile(self, f):
        """Save the filter to the specified file object. """
        # This is based on the current implementation of CBucketFile
        # TODO: Submit a pull request to make this part of its API
        self.infected_observations.buckets.tofile(f)


class ContactTracer:
    """Simple reference implementation of the contact tracer.

    This class shows how the contact tracing part of a smartphone app would
    operate.

    *Simplification* This class simplifies recording of observations and
    computing the final risk score. Observations are represented by the
    corresponding EphID, and we omit proximity metrics such as duration and
    signal strength. Similarly, the risk scoring mechanism is simple. It only
    outputs the number of unique infected EphIDs that have been observed.

    Actual implementations will probably take into account extra information
    from the Bluetooth backend to do better distance measurements, and
    subsequently use this information to do a better risk computation.

    A note on internal data representation:
     * All internal times are epoch counters, starting from the start of UNIX
       epoch (see :func:`epoch_from_time`)

    All external facing interfaces use datetime.datetime objects.
    """

    def __init__(
        self, start_time=None, db_path=":memory:", receiver=True, transmitter=True
    ):
        """Create an new App object and initialize

        Args:
            start_time (:obj:`datetime.datetime`, optional): Start of the first day
                The default value is the start of the current day.
            db_path: Path where the SQLite database will be stored, or ":memory:"
                for a transient in-memory database (the default)
            receiver: If true (the default) the tracing will handle handle the
                receiver-end housekeeping
            transmitter: If true (the default) the tracing will handle handle the
                transmitter-end housekeeping
        """

        # Database where seeds EphIDs and other data are stored
        self.db = ClientDatabase(db_path)

        if start_time is None:
            start_time = datetime.now()
            start_time = start_time.replace(hour=0, minute=0, second=0, microsecond=0)

        self.start_of_today = start_time
        self.receiver = receiver
        self.transmitter = transmitter

        # Create new ephids and seeds
        self._create_new_day_ephids()

    @property
    def today(self):
        """The current day (datetime.date)"""
        return self.start_of_today.date()

    def _create_new_day_ephids(self):
        """Compute a new set of seeds and ephids for a new day"""

        # The ephids are required by the transmitter
        if not self.transmitter:
            return

        # Generate fresh seeds and store them
        seeds = [generate_new_seed() for _ in range(NUM_EPOCHS_PER_DAY)]
        ephids = [ephid_from_seed(seed) for seed in seeds]

        # Convert to epoch numbers
        first_epoch = epoch_from_time(self.start_of_today)

        with self.db.atomic():
            # Verify the ids have not been already been created
            if self.db.get_epoch_seeds(first_epoch, first_epoch + 1):
                return

            # Store seeds and compute EphIDs
            for relative_epoch in range(0, NUM_EPOCHS_PER_DAY):
                self.db.add_epoch_ids(
                    first_epoch + relative_epoch,
                    seeds[relative_epoch],
                    ephids[relative_epoch],
                )

    def check_advance_day(self, time):
        """ Check and advance the current day based on the passed time, if needed."""

        if time.date() > self.today:
            self.next_day()

    def next_day(self):
        """Setup seeds and EphIDs for the next day, and do housekeeping"""

        # Update current day
        self.start_of_today = self.start_of_today + timedelta(days=1)

        # Generate new EphIDs for new day
        self._create_new_day_ephids()

        # Remove old observations
        if self.receiver:
            last_retained_day = self.today - timedelta(days=RETENTION_PERIOD)
            self.db.delete_past_observations(day_timestamp(last_retained_day))

        # Remove old seeds and ephids
        if self.transmitter:
            days_back = timedelta(days=RETENTION_PERIOD)
            last_valid_time = self.start_of_today - days_back
            last_retained_epoch = epoch_from_time(last_valid_time)
            self.db.delete_past_epoch_ids(last_retained_epoch)

    def get_ephid_for_time(self, time):
        """Return the EphID corresponding to the requested time

        Args:
            time (:obj:`datetime.datetime`): The requested time

        Raises:
            ValueError: If the requested ephid is unavailable
        """
        # Convert to epoch number
        epoch = epoch_from_time(time)

        ephid = self.db.get_epoch_ephid(epoch)
        if not ephid:
            raise ValueError("EphID not available, did you call next_day()?")

        return ephid

    def add_observation(self, ephid, time, rssi=0):
        """Add ephID to list of observations. Time must correspond to the current day

        Args:
            ephID (byte array): the observed ephID
            time (:obj:`datatime.datetime`): time of observation
            rssi: the observation's received signal strength indicator

        Raises:
            ValueError: If time does not correspond to the current day
        """

        if not time.date() == self.today:
            raise ValueError("Observation must correspond to current day")

        epoch = epoch_from_time(time)
        hashed_observation = hashed_observation_from_ephid(ephid, epoch)
        self.db.add_observation(day_timestamp(self.today), hashed_observation, rssi)

    def get_tracing_seeds_for_epochs(self, reported_epochs):
        """Return the seeds corresponding to the requested epochs

        Args:
            reported_epochs: A continuous range of requested epochs
            for contagion reporting

        Raises:
            ValueError: If a requested epoch is unavailable
        """
        seeds = self.db.get_epoch_seeds(reported_epochs[0], reported_epochs[-1] + 1)
        if len(seeds) != len(reported_epochs):
            raise ValueError("A requested epoch is not available")

        return seeds

    def get_tracing_information(self, first_contagious_time, last_contagious_time=None):
        """Return the seeds corresponding to the requested time range

        *Warning:* This function should not be used to retrieve tracing
        information for future epochs to limit the amount of linking
        information available to the server. Unfortunately, this class does not
        have a notion of the exact time, so it is up to the caller to verify
        this constraint.

        Args:
            first_contagious_time (:obj:`datetime.datetime`): The time from which we
                 should start tracing
            last_contagious_time (:obj:`datatime.datatime`, optional): The last time
                 for tracing. Default value: the beginning of the current day.

        Returns:
            epochs: the epochs
            seeds: the corresponding seeds

        Raises:
            ValueError: If the requested key is unavailable or if
                last_contagious_time is before first_contagious_time
        """

        if last_contagious_time is None:
            last_contagious_time = self.start_of_today

        if last_contagious_time < first_contagious_time:
            raise ValueError(
                "Last_contagious_time should be after first_contagious_time"
            )

        start_epoch = epoch_from_time(first_contagious_time)
        end_epoch = epoch_from_time(last_contagious_time)
        reported_epochs = range(start_epoch, end_epoch + 1)

        return reported_epochs, self.get_tracing_seeds_for_epochs(reported_epochs)

    def matches_with_batch(self, batch):
        """Check for contact with infected person given a published filter

        Args:
            infected_observations: A (compact) representation of hashed
                observations belonging to infected persons

        Returns:
            int: How many EphIDs of infected persons we saw
        """

        seen_infected_ephids = 0

        for hashed_observation in self.db.get_observations():
            if hashed_observation in batch.infected_observations:
                seen_infected_ephids += 1

        return seen_infected_ephids
