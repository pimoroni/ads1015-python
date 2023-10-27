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


@pytest.fixture(scope='function')
def ads1015():
    import ads1015
    yield ads1015
    del sys.modules['ads1015']


@pytest.fixture(scope='function')
def smbus_notimeout():
    sys.modules['smbus'] = mock.Mock()
    sys.modules['smbus'].SMBus = MySMBus
    yield
    del sys.modules['smbus']


@pytest.fixture(scope='function')
def smbus_timeout():
    sys.modules['smbus'] = mock.Mock()
    sys.modules['smbus'].SMBus = MockSMBus
    yield
    del sys.modules['smbus']


@pytest.fixture(scope='function')
def mocksmbus():
    sys.modules['smbus'] = mock.Mock()
    yield sys.modules['smbus']
    del sys.modules['smbus']
