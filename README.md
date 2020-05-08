# Epidose: A privacy-preserving epidemic dosimeter based on contact tracing

This repository provides an open source software
reference implementation for an *epidemic dosimeter*.
Just as a radiation dosimeter measures dose uptake of external ionizing
radiation, the epidemic dosimeter tracks potential exposure to viruses
or bacteria associated with an epidemic.
The dosimeter measures a person's exposure to an epidemic, such as COVID-19,
based on exposure to contacts that have been tested positive.
The epidemic dosimeter is designed to be widely accessible
and to safeguard privacy.
Specifically, it is designed to run on the $10 open-hardware
[Raspberry Pi Zero-W](https://www.raspberrypi.org/products/raspberry-pi-zero-w/)
computer, with a minimal user interface, comprising LED indicators
regarding operation and exposure risk
and a physical interlock switch to allow the release of contact data.
The software is based on the [DP3T](https://github.com/DP-3T/documents)
contact tracing "unlinkable" design and corresponding reference implementation
code, gratefully acknowledging the team's amazing work.

## Rationale
Contact tracing via smartphone apps has been widely touted as an important
way to control and limit the spread of the COVID-19 epidemic.
However, basing contact-tracing on phone apps has several limitations.
[According to market reports](https://en.wikipedia.org/wiki/List_of_countries_by_smartphone_penetration),
while in higher income countries smartphone penetration is over 60%, in
lower income ones it drops significantly, even to less than 20%.
Even in higher income countries, smartphone penetration declines significantly
with [increased age](https://doi.org/10.1109/MCE.2016.2614524)
and reduced income.
Also, Bluetooth-based contact tracing apps may not be able to run on
older smartphone models, and many fear compromised privacy when running
such an app on their phone.
Contact tracing app solutions benefit only those using them by flagging
at an early stage one at risk.
Therefore, older people who are usually less accustomed to technology
(and also run greater risks) and less privileged society members are
at a disadvantage.

Exposure tracking solutions can only be successful if adopted by a
significant percentage of the population.
In lower income regions and countries
(which could be
[devastated by COVID-19](https://www.economist.com/leaders/2020/03/26/the-coronavirus-could-devastate-poor-countries)),
smartphone-based solutions are unlikely to be effective due to a lack
of critical mass.
The proposed epidemic dosimeter addresses the above limitations.

Given its low cost and simplicity (a single LED indicator),
the epidemic dosimeter can be easily and affordably deployed to
lower income countries and marginalized parts of a population
serving billions.
Its resemblance to existing diagnostic devices,
and the ability to distribute it without exchanging documentation
can also allay the fears of those who worry about the privacy implications
of phone apps.
By extension, its existence will also increase the acceptance
of comparable phone apps.

## Overview and Use

<img width="300" alt="Epidemic dosimeter concept drawing" src="https://raw.githubusercontent.com/dspinellis/epidose/master/hardware/concept.png">

The epidemic dosimeter is a lightweight (<100g), low-cost
(mass-produced <40€), self-contained device, housed in a package with a
three-color LED.
One simply picks it up from a distribution point without
providing any personal data, charges it, and carries it around.
When health authorities test people, they associate its contacts with the
test results by attaching the dosimeter to a special beacon.

A single LED indicates the dosimeter’s status.

* Flashing green: Normal operation
* Slow flashing red: User may have been exposed and should contact a
  health provider.
* Rapidly flashing red: User has been tested positive and needs to self
  quarantine. (To be used in areas lacking better means to contact people.)
* Orange: Charging is required.
  It is estimated that the dosimeter would last a full working day without
  charging.

As a possible extension the LED indicator can be extended to more
LEDs to indicate:

* the level of exposure, and
* by tracking other encountered Bluetooth devices, the effectiveness
  of the user's social distancing measures.

## Technology
The epidemic dosimeter works by acting as a
[Bluetooth Low Energy](https://en.wikipedia.org/wiki/Bluetooth_Low_Energy)
(BLE) beacon to transmit periodically-changing random identifiers,
and as a corresponding beacon receiver to track individuals carrying
a dosimeter located in the vicinity.
By basing its code on the DP3T reference implementation it should also
interoperate with the corresponding smartphone applications.
The dosimeter's design calls for it to be pre-configured to
obtain possibly infected contacts and software updates through a
global WiFi sharing network, such as that offered by [fon](https://fon.com/).

## Software architecture
The dosimeter's software is designed around the following components,
as depicted in the diagram at the end of this section.

* `beacon_tx_unlinkable.py`: Continuously running transmitter of ephemeral
  identifiers.
  Each day a new set of identifiers are created, stored in a database,
  and transmitted.  Every 15 minutes the transmitted identifier changes.
  Each day the transmitter also purges from the database ephemeral
  identifiers that no longer need to be retained.
* `beacon_rx_unlinkable.py`: Continuously running receiver of
  identifiers transmitted by other devices.
  These are again stored in a database in hashed format to allow
  the identification of contacts with infected persons.
  Each day the received also purges from the database received hashes
  that no longer need to be retained.
* `create_filter.py`: A program that is run on the server.
  It takes as input epoch identifiers and ephemeral identification hashes
  and produces a [Cuckoo filter](https://en.wikipedia.org/wiki/Cuckoo_filter)
  that can be used to check for possible contacts with infected persons.
* `check_infection_risk.py`: A program that is run on the
  epidemic dosimeter.
  It takes as input the Cuckoo filter, and calculates
  the number of infected contacts found in the database.
  The application updates the indicator LED according to the result.
* [SQLite](https://www.sqlite.org/index.html) database for storing the
  created and received ephemeral identifiers.
* `download_infected.sh`: A script that downloads from the server the
  Cockoo filter for the identifiers of infected contacts.
* `upload_contacts.py`: Subject to an agreement between the user and
  the health authority, implemented through a physical interlock and
  a suitable protocol, this uploads to a health authority's server the
  contacts of a user found to be infected.
* `watchdog.sh`: Monitors the correct operation of all components and
  flashes the green LED to indicate correct operation.
  It also resets the device in case of a failure.
* `update_client.sh`: Runs periodically to download an updated filter,
  check for contacts with infected persons, and perform any required
  software updates.
* `ha_server.py`: The health authority's server, which receives
  lists of infected person's contacts and provides filter updates.
* A device running in testing centers acts as a user interface and
  source of trust.  It allows health professionals, in coordination
  with the epidemic dosimeter's user, handle the uploading of its
  contacts (at that point, or when the test results are out),
  providing a single-use key to authorize and authenticate the upload.

![Software architecture](https://raw.githubusercontent.com/dspinellis/epidose/master/doc/software-architecture.png)

## Hardware parts list
* Raspberry Pi Zero-W
* Li-on rechargeable battery 3.7V / 3400mAh
* Enclosure (3D printed)
* Battery holder
* [Li-on battery charging module with step up boost converter](https://grobotronics.com/lithium-charging-module-with-step-up-boost-converter-3.7v-9v-5v-2a.html)
* I/O PCB
  * RGB LED
  * 330 Ohm current-limiting resistor
  * Physical interlock micro-switch
  * 40-pin connector (receptacle for prototyping, soldered for mass production)
* 8GB microSDHC Class 10 card
* 5V USB charger

## What is implemented
Currently all the device-end functionality has been implemented and
tested, with a device reporting an *infected* status after (manually)
downloading a filter constructed from identifiers actually transmitted
and received over Bluetooth.

The following programs are available in the `examples` directory.

* `beacon_tx_unlinkable.py`
* `beacon_rx_unlinkable.py`
* `create_filter.py`
* `check_infection_risk.py`

All programs can be run with a *--help* argument to obtain usage information.

## What is missing
The server and the device automation and configuration are under construction.
In the following days expect to see code for the following components.

* `download_infected.sh`
* `upload_contacts.py`
* `watchdog.sh`
* `update_client.sh`
* `ha_server.py`

In some places the code takes shortcuts or makes simplifications (e.g.
not using the number of messages and their strength (RSSI) for estimating
the infection risk.)  These are marked in the code with `TODO` comments.

Also missing are the following.

* The health authority user interface
* The circuit diagram and PCB layout diagram for the support electronics
* The design for 3D-printing the enclosure

## Installing the reference implementation

You'll need to install the required libraries and project.
Here is how you can do it under the Ubuntu GNU/Linux distribution.

```bash
sudo apt-get install libbluetooth-dev virtualenv libglib2.0-dev python3-setuptools sqlite3
git clone https://github.com/dspinellis/epidose
cd epidose
virtualenv venv -p /usr/bin/python3
. venv/bin/activate
pip3 install -e .
```

## Running the client code

After installing the project you can run the client code on a Raspberry-Pi Zero-W as follows.

```sh
sudo mkdir -p /var/lib/epidose
nohup sudo venv/bin/python examples/beacon_tx_unlinkable.py -v &
nohup sudo venv/bin/python examples/beacon_rx_unlinkable.py -v &
```

You can then monitor the device's operation with
`tail -f /var/log/beacon_tx` and `tail -f /var/log/beacon_rx`.

You can also obtain a report of what has been stored in the device's
database by running `utils/client-db-report.sh`.

### Database report example
```
Received (and retained) ephemeral id hashes

Day         Ephid Hash  Count       RSSI
----------  ----------  ----------  ----------
2020-05-07  EEF9237FCB  306         -50
2020-05-07  38EBD1F502  287         -50
2020-05-07  5B487CFBD3  131         -48
2020-05-07  EBEA03EC12  585         -48
2020-05-07  7940535B20  595         -51
2020-05-07  1C807D7D6E  1           -52
2020-05-07  43DFA3FEDB  600         -50
2020-05-07  E3618D8B33  371         -51
[...]


Stored (and retained) sent ephemeral ids

Timestamp            Epoch       Seed        Ephid
-------------------  ----------  ----------  ----------
2020-05-07 21:00:00  1765428     504AE4E8AF  F826011CC6
2020-05-07 21:15:00  1765429     8540B29ADD  F3406EBCD8
2020-05-07 21:30:00  1765430     133652DF10  CB4F3126EF
2020-05-07 21:45:00  1765431     3C3C914494  9A93E9BBFC
2020-05-07 22:00:00  1765432     D057DA48EE  71E6980B2A
2020-05-07 22:15:00  1765433     0F9133C578  F1D72EAC4A
2020-05-07 22:30:00  1765434     07A56ABD78  675C1E552A
2020-05-07 22:45:00  1765435     710ACBD99C  7FCBF944A5
[...]
```

To test contact tracing you currently need to follow these steps.

* Obtain a list of contacts.
* Store them into a file.
* Create a Cuckoo filter by running `create_filter.py` on that file.
* Copy the Cuckoo filter on another device.
* Check against contacts by running `check_infection_risk.py`.

## Development

For development, you should install the development and test dependencies:

```bash
pip install -e ".[dev,test]"
```

You should also install the proper pre-commit-hooks so that the files stay
formatted:

```bash
pip install pre-commit
pre-commit install
```

Finally, it's a good idea to clone and regularly integrate the DP-3T
reference implementation, which is the base of this code's cryptographic
protocol.

```sh
git remote add dp3t https://github.com/DP-3T/reference_implementation.git
git fetch
```

### Running the tests

To run the tests, simply call

```sh
pytest
```

If you just installed the test dependencies, you may need to reload the `venv`
(`deactivate` followed by `source venv/bin/ativate`) to ensure that the paths
are picked up correctly.

## More information
* [Decentralized Privacy-Preserving Proximity Tracing](https://github.com/DP-3T/documents)
* [ACM Europe TPC Statement on Principles, Practices for COVID-19 Contact Tracing Applications](https://www.acm.org/binaries/content/assets/public-policy/europe-tpc-contact-tracing-statement.pdf)

## License

This code is licensed under the Apache 2.0 license, as found in the LICENSE
file.
