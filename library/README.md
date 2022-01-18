# ADS1015 4 channel differential/single-ended ADC

[![Build Status](https://travis-ci.com/pimoroni/ads1015-python.svg?branch=master)](https://travis-ci.com/pimoroni/ads1015-python)
[![Coverage Status](https://coveralls.io/repos/github/pimoroni/ads1015-python/badge.svg?branch=master)](https://coveralls.io/github/pimoroni/ads1015-python?branch=master)
[![PyPi Package](https://img.shields.io/pypi/v/ads1015.svg)](https://pypi.python.org/pypi/ads1015)
[![Python Versions](https://img.shields.io/pypi/pyversions/ads1015.svg)](https://pypi.python.org/pypi/ads1015)

# Installing

Stable library from PyPi:

* Just run `sudo pip install ads1015`

Latest/development library from GitHub:

* `git clone https://github.com/pimoroni/ads1015-python`
* `cd ads1015-python`
* `sudo ./install.sh`


# Changelog

0.0.8
-----

* Add thread-safe wrapper around ADC reads

0.0.7
-----

* Fix setting data rate
* Add support for ADS1115
* Add new detect_chip_type function

0.0.6
-----

* Added support for all addresses ads1015 supports
* Genericized implementation away from pimoroni breakout
* Typo fixes in docstring
* Fix get_multiplexer so that it returns a value

0.0.5
-----

* Fix to support alternate i2c address
* Typo fixes in DocString and comment

0.0.4
-----

* Port to i2cdevice>=0.0.6 set/get API

0.0.3
-----

* Fixed timeout in wait_for_conversion
* Aliased timeout exception to ads1015.ADS1015TimeoutError

0.0.2
-----

* Fixed Python 2.7 bug with missing TimeoutError

0.0.1
-----

* Initial Release
