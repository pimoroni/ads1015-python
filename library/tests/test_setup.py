import sys
import mock


def test_setup():
    sys.modules['smbus'] = mock.Mock()
    import ads1015
    device = ads1015.ADS1015()
    del device
