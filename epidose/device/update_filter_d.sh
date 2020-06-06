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

# Parse options
while getopts 'vd' c
do
  case $c in
    v)
      VERBOSE_FLAG=1
      ;;
    d)
      DEBUG_FLAG=-d
      ;;
  esac
done

shift $((OPTIND-1))

# Source common functionality (logging, WiFi)
if [ "$DEBUG_FLAG" ] ; then
  # shellcheck source=epidose/common/util.sh
  . "$(dirname "$0")/../common/util.sh"
else
  # shellcheck source=epidose/common/util.sh
  . /usr/lib/dp3t/util.sh
fi

# Wait until a filter file is required
wait_till_filter_needed()
{
  if [ -r "$FILTER" ] ; then
    filter_mtime=$(stat -c '%Y' "$FILTER")
    time_now=$(date +%s)
    filter_age=$((time_now - filter_mtime))
    if [ $filter_age -lt $MAX_FILTER_AGE ] ; then
      log "Filter's age ($filter_age s) is current; no update required"
      to_sleep=$((MAX_FILTER_AGE - filter_age))
      log "Sleeping for $to_sleep s"
      sleep $to_sleep
      log "Waiting up from sleep; new filter is now required"
    fi
    log "Filter's age ($filter_age s) makes it stale; update required"
  else
    log "No filter available; download required"
    mkdir -p "$(dirname $FILTER)"
  fi
}


# Obtain a (new) version of the Cuckoo filter
get_filter()
{
  log "Obtaining new filter from $SERVER_URL"
  while : ; do
    wifi_acquire
    if err=$(curl --silent --show-error --fail --output "$FILTER.new" \
      "$SERVER_URL/filter" 2>&1) ; then
      wifi_release
      # Atomically replace existing filter with new one
      mv "$FILTER.new" "$FILTER"
      log "New filter obtained: $(stat -c %s "$FILTER") bytes"
      return
    else
      wifi_release
      log "Unable to get filter: $err"
      log "Wil retry in $WIFI_RETRY_TIME s"
      sleep $WIFI_RETRY_TIME
    fi
  done
}


if [ -z "$1" ] ; then
  echo "Usage: $0 server-url" 1>&2
  exit 1
fi
SERVER_URL="$1"

while : ; do
  wait_till_filter_needed
  get_filter
  run_python check_infection_risk "$FILTER" || :
done
