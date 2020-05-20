#!/bin/sh
#
# Upload contacts when authorized by the affected user and the Health Authority
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

export APP_NAME=upload_contacts_d

# Source common functionality (logging, WiFi)
if [ -t 1 ] ; then
  # shellcheck source=epidose/common/util.sh
  . "$(dirname "$0")/../common/util.sh"
else
  # shellcheck source=epidose/common/util.sh
  . /usr/lib/dp3t/util.sh
fi

if [ -z "$1" ] ; then
  echo "Usage: $0 server-url" 1>&2
  exit 1
fi
SERVER_URL="$1"

# Wait for button press and upload contacts
# TODO: Obtain upload authorization and affected period from Health Authority
while : ; do
  # Use development files if running from a terminal
  if [ -t 1 ] ; then
    venv/bin/python epidose/device/device_io.py -w -d -v
    venv/bin/python epidose/device/upload_contacts.py -d -v -s "$SERVER_URL" "$(date +'%Y-%m-%dT%H:%M:%S' --date='30 min ago')" "$(date +'%Y-%m-%dT%H:%M:%S')"
  else
    device_io -w -v
    upload_contacts -v -s "$SERVER_URL" "$(date +'%Y-%m-%dT%H:%M:%S' --date='30 min ago')" "$(date +'%Y-%m-%dT%H:%M:%S')"
  fi
done
