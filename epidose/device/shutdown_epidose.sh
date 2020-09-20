#!/bin/sh
#
# Perform a complete shutdown by turning off power after the OS shutdown
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

export APP_NAME=shutdown_epidose

# Pick up utility functions relative to the script's source code
UTIL="$(dirname "$0")/util.sh"

# Source common functionality (logging, WiFi)
# shellcheck source=epidose/device/util.sh
SERVER_URL=none . "$UTIL"


# Schedule power removal in 30s
run_python device_io --power-off

# Shutdown OS
shutdown -h now "User-initiated shutdown"
