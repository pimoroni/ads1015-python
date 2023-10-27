import pytest


def test_setup(ads1015, mocksmbus):
    device = ads1015.ADS1015()
    del device


def test_setup_invalid_i2c_address(ads1015, mocksmbus):
    with pytest.raises(ValueError):
        device = ads1015.ADS1015(i2c_addr=0xFFF)
        del device


def test_autodetect(ads1015, smbus_notimeout):
    device = ads1015.ADS1015()
    assert device.detect_chip_type() == "ADS1015"


def test_timeout(ads1015, smbus_timeout):
    device = ads1015.ADS1015()
    with pytest.raises(ads1015.ADS1015TimeoutError):
        device.wait_for_conversion(timeout=0.01)


def test_convert(ads1015, smbus_notimeout):
    device = ads1015.ADS1015()
    device.wait_for_conversion(timeout=0.01)


def test_deprecated_inputs(ads1015, smbus_notimeout):
    """Test that we can read the value of the multiplexer register
    without getting a deprecated input name back."""
    device = ads1015.ADS1015()
    for pin in ["in0/in3", "in1/in3", "in2/in3", "in3/gnd"]:
        device.set_multiplexer(pin)
        assert device.get_multiplexer() == pin

    device.set_multiplexer("ref/gnd")
    assert device.get_multiplexer() == "in3/gnd"
