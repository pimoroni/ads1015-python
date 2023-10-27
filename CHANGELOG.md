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
