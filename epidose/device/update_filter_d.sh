#!/bin/sh
#
# Periodically update the Cuckoo filter of affected users
#
# Copyright 2020 Diomidis Spinellis
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

set -e

# Location of the Cuckoo filter
FILTER=/var/lib/epidose/client-filter.bin

# Maximum allowed filter age before an update (in seconds)
# 6 hours
MAX_FILTER_AGE=$((6 * 60 * 60))

export APP_NAME=update_filter_d

# Pick up utility functions relative to the script's source code
UTIL="$(dirname "$0")/util.sh"


# Source common functionality (logging, WiFi)
# shellcheck source=epidose/device/util.sh
. "$UTIL"

# Wait until a filter file is required
wait_till_filter_needed()
{
  # Checks whether the Cuckoo filter is stale or fresh
  # and returns the time until its valid (in seconds)
  validity_time=$(get_filter_validity_age)
  if [ "$validity_time" -ne 0 ]; then
    log "Sleeping for $validity_time s"
    sleep "$validity_time"
    log "Waking up from sleep; new filter is now required"
  fi
}

while : ; do
  wait_till_filter_needed
  log "Obtaining new filter from $SERVER_URL"
  while : ; do
    wifi_acquire

    # Tries to get a new cuckoo filter from the ha-server
    if ! get_new_filter; then
      wifi_release
      log "Will retry in $WIFI_RETRY_TIME s"
      sleep "$WIFI_RETRY_TIME"
    else
      wifi_release
      break
    fi	    
  done
  run_python check_infection_risk "$FILTER" || :
  # TODO: Also check for software updates
done
