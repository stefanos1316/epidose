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

from datetime import datetime, timedelta, timezone
import pytest
from testfixtures import Replace, test_datetime

from dp3t.protocols.unlinkable_db import ContactTracer
from dp3t.protocols.unlinkable import epoch_from_time

START_TIME = datetime(2020, 4, 25, 22, 10, tzinfo=timezone.utc)


@pytest.fixture(scope="function")
def contact_tracer():
    ct = ContactTracer(start_time=START_TIME)
    yield ct
    ct.db.close()


def test_no_seeds_for_receiver():
    ct = ContactTracer(start_time=START_TIME, transmitter=False)
    epoch = epoch_from_time(START_TIME)
    seeds = ct.db.get_epoch_seeds(epoch, epoch + 1)
    assert len(seeds) == 0
    ct.db.close()


def test_seeds_initialized(contact_tracer):
    epoch = epoch_from_time(START_TIME)
    seeds = contact_tracer.db.get_epoch_seeds(epoch, epoch + 1)
    assert len(seeds) == 1


def test_check_next_day_empty(contact_tracer):
    epoch = epoch_from_time(START_TIME + timedelta(days=1))
    seeds = contact_tracer.db.get_epoch_seeds(epoch, epoch + 1)
    assert len(seeds) == 0


def test_check_advance_day_not_firing(contact_tracer):
    with Replace("dp3t.protocols.unlinkable_db.datetime", test_datetime(START_TIME)):
        contact_tracer.check_advance_day()
    epoch = epoch_from_time(START_TIME + timedelta(days=1))
    seeds = contact_tracer.db.get_epoch_seeds(epoch, epoch + 1)
    assert len(seeds) == 0


def test_check_advance_day_firing(contact_tracer):
    close_to_day_end = START_TIME + timedelta(days=1, minutes=-30)
    with Replace(
        "dp3t.protocols.unlinkable_db.datetime", test_datetime(close_to_day_end)
    ):
        contact_tracer.check_advance_day()
    epoch = epoch_from_time(START_TIME)
    seeds = contact_tracer.db.get_epoch_seeds(epoch, epoch + 1)
    assert len(seeds) == 1
