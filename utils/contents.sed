#!/usr/bin/sed -nf
#
# Create the README file table of contents
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

# Skip Contents header
/## Contents/b

/^## / {
	# Keep a copy
	h
	# Bullet and hyperlinked text
	s/## \(.*\)/- [\1]/
	# Get back copy
	x
	# Convert into link
	s/## /(#/
	# Convert to lowercase
	s/./\l&/g
	s/$/)/
	s/ /-/g
	# Swap again
	x
	# Append hold space to pattern space
	G
	s/\n//
	p
}
