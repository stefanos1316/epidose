#!/bin/sh
#
# Report the contents of the specified SQLite contact tracing client database
#
# Copyright Diomidis Spinellis
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


cat <<\EOF | sqlite3 ${1:-/var/lib/dp3t/client-database.db}
SELECT 'Received (and retained) ephemeral id hashes';
SELECT '';
.mode column
.headers on
SELECT DATE(day, "unixepoch") AS Day, SUBSTR(HEX(ephid_hash), 1, 10) AS 'Ephid Hash',
  ocount AS Count, srssi / ocount AS RSSI FROM DailyObservations;

.headers off
SELECT '';
SELECT '';
SELECT 'Stored (and retained) sent ephemeral ids';
SELECT '';
.headers on
SELECT DATETIME(epoch * 60 * 15, "unixepoch") AS Timestamp, epoch AS Epoch,
  SUBSTR(HEX(seed), 1, 10) AS Seed, SUBSTR(HEX(ephid), 1, 10) AS Ephid
  from EpochIds;

EOF
