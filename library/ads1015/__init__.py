from i2cdevice import Device, Register, BitField, _int_to_bytes
from i2cdevice.adapter import Adapter, LookupAdapter
import time
import struct

__version__ = '0.0.6'

I2C_ADDRESS_DEFAULT = 0x48  # Default i2c address for Pimoroni breakout
I2C_ADDRESS_ALTERNATE = 0x49  # Default alternate i2c address for Pimoroni breakout
I2C_ADDRESS_ADDR_GND = 0x48  # Address when ADDR pin is connected to Ground
I2C_ADDRESS_ADDR_VDD = 0x49  # Address when ADDR pin is connected to VDD
I2C_ADDRESS_ADDR_SDA = 0x50  # Address when ADDR pin is connected to SDA. Device datasheet recommends using this address last (sec 8.5.1.1)
I2C_ADDRESS_ADDR_SCL = 0x51  # Address when ADDR pin is connected to SCL

I2C_ADDRESSES = [
    I2C_ADDRESS_DEFAULT,
    I2C_ADDRESS_ALTERNATE,
    I2C_ADDRESS_ADDR_GND,
    I2C_ADDRESS_ADDR_VDD,
    I2C_ADDRESS_ADDR_SDA,
    I2C_ADDRESS_ADDR_SCL
]


try:
    ADS1015TimeoutError = TimeoutError
except NameError:
    from socket import timeout as ADS1015TimeoutError


class S16Adapter(Adapter):
    def _decode(self, value):
        return struct.unpack('>h', _int_to_bytes(value, 2))[0]

    def _encode(self, value):
        v = struct.pack('>h', value)
        return (ord(v[0]) << 8) | ord(v[1])


class ConvAdapter(Adapter):
    def _decode(self, value):
        if value & 0x800:
            value -= 1 << 12
        return value

    def _encode(self, value):
        return 0


class ADS1015:
    def __init__(self, i2c_addr=I2C_ADDRESS_DEFAULT, alert_pin=None, i2c_dev=None):
        self._is_setup = False
        self._i2c_addr = i2c_addr
        self._i2c_dev = i2c_dev
        self._alert_pin = alert_pin
        self._deprecated_channels = {
            'in0/ref': 'in0/in3',
            'in1/ref': 'in1/in3',
            'in2/ref': 'in2/in3',
            'ref/gnd': 'in3/gnd'
        }
        self._ads1015 = Device(I2C_ADDRESSES, i2c_dev=self._i2c_dev, bit_width=8, registers=(
            Register('CONFIG', 0x01, fields=(
                BitField('operational_status', 0b1000000000000000, adapter=LookupAdapter({
                    'active': 0,
                    'inactive_start': 1
                })),
                BitField('multiplexer', 0b0111000000000000, adapter=LookupAdapter({
                    'in0/in1': 0b000,   # Differential reading between in0 and in1, voltages must not be negative and must not exceed supply voltage
                    'in0/in3': 0b001,   # Differential reading between in0 and in3. pimoroni breakout onboard reference connected to in3
                    'in1/in3': 0b010,   # Differential reading between in1 and in3. pimoroni breakout onboard reference connected to in3
                    'in2/in3': 0b011,   # Differential reading between in2 and in3. pimoroni breakout onboard reference connected to in3
                    'in0/gnd': 0b100,   # Single-ended reading between in0 and GND
                    'in1/gnd': 0b101,   # Single-ended reading between in1 and GND
                    'in2/gnd': 0b110,   # Single-ended reading between in2 and GND
                    'in3/gnd': 0b111    # Single-ended reading between in3 and GND. Should always read 1.25v (or reference voltage) on pimoroni breakout
                })),
                BitField('programmable_gain', 0b0000111000000000, adapter=LookupAdapter({
                    6.144: 0b000,
                    4.096: 0b001,
                    2.048: 0b010,
                    1.024: 0b011,
                    0.512: 0b100,
                    0.256: 0b101
                })),
                BitField('mode', 0b0000000100000000, adapter=LookupAdapter({
                    'continuous': 0,
                    'single': 1
                })),
                BitField('data_rate_sps', 0b0000000001110000, adapter=LookupAdapter({
                    128: 0b000,
                    250: 0b001,
                    490: 0b010,
                    920: 0b011,
                    1600: 0b100,
                    2400: 0b101,
                    3300: 0b110
                })),
                BitField('comparator_mode', 0b0000000000010000, adapter=LookupAdapter({
                    'traditional': 0b0,  # Traditional comparator with hystersis
                    'window': 0b01
                })),
                BitField('comparator_polarity', 0b0000000000001000, adapter=LookupAdapter({
                    'active_low': 0b0,
                    'active_high': 0b1
                })),
                BitField('comparator_latching', 0b0000000000000100),
                BitField('comparator_queue', 0b0000000000000011, adapter=LookupAdapter({
                    'one': 0b00,
                    'two': 0b01,
                    'four': 0b10,
                    'disabled': 0b11
                }))
            ), bit_width=16),
            Register('CONV', 0x00, fields=(
                BitField('value', 0xFFF0, adapter=ConvAdapter()),
            ), bit_width=16),
            Register('THRESHOLD', 0x02, fields=(
                BitField('low', 0xFFFF, adapter=S16Adapter()),
                BitField('high', 0xFFFF, adapter=S16Adapter())
            ), bit_width=32)
        ))
        self._ads1015.select_address(self._i2c_addr)

    def start_conversion(self):
        """Start a conversion."""
        self.set_status('inactive_start')

    def conversion_ready(self):
        """Check if conversion is ready."""
        return self.get_status() != 'active'

    def set_status(self, value):
        """Set the operational status.

        :param value: Set to true to trigger a conversion, false will have no effect.

        """
        self._ads1015.set('CONFIG', operational_status=value)

    def get_status(self):
        """Get the operational status.

        Result will be true if the ADC is actively performing a conversion and false if it has completed.

        """
        return self._ads1015.get('CONFIG').operational_status

    def set_multiplexer(self, value):
        """Set the analog multiplexer.

        Sets up the analog input in single or differential modes.

        If b is specified as gnd the ADC will be in single-ended mode, referenced against Ground.

        If b is specified as in1 or ref the ADC will be in differential mode.

        a should be one of in0, in1, in2, or in3

        This method has no function on the ADS1013 or ADS1014

        'in0/in1' - Differential reading between in0 and in1, voltages must not be negative and must not exceed supply voltage
        'in0/in3' - Differential reading between in0 and in3
        'in1/in3' - Differential reading between in1 and in3
        'in2/in3' - Differential reading between in2 and in3
        'in0/gnd' - Single-ended reading between in0 and GND
        'in1/gnd' - Single-ended reading between in1 and GND
        'in2/gnd' - Single-ended reading between in2 and GND
        'in3/gnd' - Should always read 1.25v (or reference voltage)

        :param value: Takes the form a/b

        """
        if value in self._deprecated_channels.keys():
            value = self._deprecated_channels[value]
        self._ads1015.set('CONFIG', multiplexer=value)

    def get_multiplexer(self):
        """Return the current analog multiplexer state."""
        return self._ads1015.get('CONFIG').multiplexer

    def set_mode(self, value):
        """Set the analog mode.

        In single-mode you must trigger a conversion manually by writing the status bit.

        :param value: One of 'continuous' or 'single'

        """
        self._ads1015.set('CONFIG', mode=value)

    def get_mode(self):
        """Get the analog mode."""
        return self._ads1015.get('CONFIG').mode

    def set_programmable_gain(self, value=2.048):
        """Set the analog gain. This has no function on the ADS1013.

        Sets up the full-scale range and resolution of the ADC in volts.

        The range is always differential, so a value of 6.144v would give a range of +-6.144.

        A single-ended reading will therefore always have only 11-bits of resolution, since the 12th bit is the (unused) sign bit.

        :param value: the range in volts - one of 6.144, 4.096, 2.048 (default), 1.024, 0.512 or 0.256

        """
        self._ads1015.set('CONFIG', programmable_gain=value)

    def get_programmable_gain(self):
        """Return the curren gain setting."""
        return self._ads1015.get('CONFIG').programmable_gain

    def set_sample_rate(self, value=1600):
        """Set the analog sample rate.

        :param value: The sample rate in samples-per-second - one of 128, 250, 490, 920, 1600 (default), 2400 or 3300

        """
        self._ads1015.set('CONFIG', data_rate_sps=value)

    def get_sample_rate(self):
        """Return the current sample-rate setting."""
        self._ads1015.get('CONFIG').data_rate_sps

    def set_comparator_mode(self, value):
        """Set the analog comparator mode.

        In traditional mode the comparator asserts the alert/ready pin when the conversion data exceeds the high threshold and de-asserts when it falls below the low threshold.

        In window mode the comparator asserts the alert/ready pin when the conversion data exceeds the high threshold or falls below the low threshold.

        :param value: Either 'traditional' or 'window'

        """
        self._ads1015.set('CONFIG', comparator_mode=value)

    def get_comparator_mode(self):
        """Return the current comparator mode."""
        self._ads1015.get('CONFIG').comparator_mode

    def set_comparator_latching(self, value):
        self._ads1015.set('CONFIG', comparator_latching=value)

    def get_comparator_latching(self):
        self._ads1015.get('CONFIG').comparator_latching

    def set_comparator_queue(self, value):
        self._ads1015.set('CONFIG', comparator_queue=value)

    def get_comparator_queue(self):
        return self._ads1015.get('CONFIG').comparator_queue

    def wait_for_conversion(self, timeout=10):
        """Wait for ADC conversion to finish.

        Timeout exception is alised as ads1015.ADS1015TimeoutError for convinience.

        :param timeout: conversion timeout in seconds

        :raises TimeoutError in Python 3.x
        :raises socket.timeout in Python 2.x

        """
        t_start = time.time()
        while not self.conversion_ready():
            time.sleep(0.001)
            if (time.time() - t_start) > timeout:
                raise ADS1015TimeoutError("Timed out waiting for conversion.")

    def get_reference_voltage(self):
        """Read the reference voltage that is included on the pimoroni PM422 breakout."""
        return self.get_voltage(channel='in3/gnd')

    def get_voltage(self, channel=None):
        """Read the raw voltage of a channel."""
        if channel is not None:
            self.set_multiplexer(channel)

        self.start_conversion()
        self.wait_for_conversion()

        value = self.get_conversion_value()
        gain = self.get_programmable_gain()
        gain *= 1000.0         # Convert gain from V to mV
        value /= 2048.0        # Divide by total register size
        value *= float(gain)   # Multiply by current gain value to get mV
        value /= 1000.0        # mV to V
        return value

    def get_compensated_voltage(self, channel=None, vdiv_a=8060000, vdiv_b=402000, reference_voltage=1.241):
        """Read and compensate the voltage of a channel."""
        pin_v = self.get_voltage(channel=channel)
        input_v = pin_v * (float(vdiv_a + vdiv_b) / float(vdiv_b))
        input_v += reference_voltage
        return round(input_v, 3)

    def get_conversion_value(self):
        return self._ads1015.get('CONV').value

    def set_low_threshold(self, value):
        self._ads1015.set('THRESHOLD', low=value)

    def get_low_threshold(self):
        self._ads1015.get('THRESHOLD').low

    def set_high_threshold(self, value):
        self._ads1015.set('THRESHOLD', high=value)

    def get_high_threshold(self):
        self._ads1015.get('THRESHOLD').high
