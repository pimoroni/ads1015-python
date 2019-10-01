import sys
import mock
import pytest
from i2cdevice import MockSMBus


class MySMBus(MockSMBus):
    def __init__(self, bus):
        MockSMBus.__init__(self, bus)
        # Set the uppermost bit of the CONFIG register
        # to indicate an "inactive/start" status
        self.regs[1] = 0b10000000


def test_setup():
    sys.modules['smbus'] = mock.Mock()
    import ads1015
    device = ads1015.ADS1015()
    del device


def test_setup_invalid_i2c_address():
    sys.modules['smbus'] = mock.Mock()
    import ads1015
    with pytest.raises(ValueError):
        device = ads1015.ADS1015(i2c_addr=0xfff)
        del device


def test_timeout():
    sys.modules['smbus'] = mock.Mock()
    sys.modules['smbus'].SMBus = MockSMBus
    import ads1015
    device = ads1015.ADS1015()
    with pytest.raises(ads1015.ADS1015TimeoutError):
        device.wait_for_conversion(timeout=0.01)


def test_convert():
    sys.modules['smbus'] = mock.Mock()
    sys.modules['smbus'].SMBus = MySMBus
    import ads1015
    device = ads1015.ADS1015()
    device.wait_for_conversion(timeout=0.01)
