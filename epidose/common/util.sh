#!/bin/sh
#
# Utilities for shell scripts
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

# Sleep time between retries to get the filter over WiFi (in seconds)
# 15 minutes
export WIFI_RETRY_TIME=$((15 * 60))


if [ -z "$APP_NAME" ] ; then
  echo "APP_NAME not set" 1>&2
  exit 2
fi

# Where logs are sent
# Stdout and stderr will go there if run from a deamon (e.g. from cron)
LOG_FILE="/var/log/$APP_NAME"

# Directory of WiFi users
WIFI_USERS=/var/lock/epidose/wifi-users
# Obtain exclusive access to the above directory
WIFI_USERS_LOCK=/var/lock/epidose/wifi-users.lock

# Log with a timestamp
log()
{
  # Output is redirected to the log file if needed at the script's lop level
  date +'%F %T ' | tr -d \\n
  echo "$@"
}

# Log stdout and stderr if run from a deamon (e.g. from cron)
# LOG_FILE must be set
if ! [ "$DEBUG_FLAG" ] ; then
  exec >>"$LOG_FILE"
  exec 2>&1
fi

log 'Starting up'

# Create lock directory
mkdir -p "$(dirname "$WIFI_USERS_LOCK")"

# Turn WiFi on and wait for for it to associate
# Internal function
_wifi_on()
{
  log "Turn on wifi"
  # No WiFi operations when running in debug mode
  test "$DEBUG_FLAG" && return
  ip link set wlan0 up
  sleep 15
}

# Turn WiFi off
# TODO: Check if "iwconfig wlan0 txpower off" yields additional power savings
# Internal function
_wifi_off()
{
  log "Turn off wifi"
  # No WiFi operations when running in debug mode
  test "$DEBUG_FLAG" && return
  ip link set wlan0 down
}

# On return WiFi will be on and stay on until the last app releases it
wifi_acquire()
{
  (
    # Acquire exclusive access to the WiFi users directory
    flock -n 9 || exit 1
    if ! [ -d "$WIFI_USERS" ] ; then
      # Directory not there; create and turn WiFi on
      mkdir "$WIFI_USERS"
      _wifi_on
    fi
    # Add ourselves to the WiFi users
    touch "$WIFI_USERS/$APP_NAME"
  ) 9>"$WIFI_USERS_LOCK"
}

# Release use of the WiFi.  When the last app releases it it will turn
# off
wifi_release()
{
  (
    # Acquire exclusive access to the WiFi users directory
    flock -n 9 || exit 1
    # Remove ourselves from the WiFi users
    rm "$WIFI_USERS/$APP_NAME"
    # Try to remove the directory; will succeed only if we were the last user
    if rmdir "$WIFI_USERS" 2>/dev/null ; then
      # Directory removed; turn WiFi off
      _wifi_off
    fi
  ) 9>"$WIFI_USERS_LOCK"
}

# Run the specified Python script from the local or installation directory
run_python()
{
  if [ "$DEBUG_FLAG" ] ; then
    prog="$1"
    shift
    venv/bin/python epidose/device/$prog.py --debug "$@"
  else
    "$@"
  fi
}
