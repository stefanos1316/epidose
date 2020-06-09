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

# Pick up utility functions relative to the script's source code
UTIL="$(dirname "$0")/../common/util.sh"

# Source common functionality (logging, WiFi)
# shellcheck source=epidose/common/util.sh
. "$UTIL"

# Upload contacts via WiFi
upload_contacts()
{
  log "Uploading contacts"
  wifi_acquire
  # TODO: Obtain upload authorization and affected period from Health Authority
  run_python upload_contacts -s "$SERVER_URL" "$(date +'%Y-%m-%dT%H:%M:%S' --date='30 min ago')" "$(date +'%Y-%m-%dT%H:%M:%S')"
  exit_code=$?
  wifi_release
  return $exit_code
}

# Wait for button press and upload contacts
while : ; do
  run_python device_io -w
  while ! upload_contacts ; do
    log "Upload failed; will retry in 30 minutes"
    sleep 1800
  done
done
