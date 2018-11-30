from i2cdevice import Device, Register, BitField

I2C_ADDRESS_DEFAULT = 0x48
I2C_ADDRESS_ALTERNATE = 0x49

class ADS1015:
    def __init__(self, i2c_addr=I2C_ADDRESS_DEFAULT, i2c_dev=None):
        self._is_setup = False
        self._i2c_addr = i2c_addr
        self._i2c_dev = i2c_dev
        self._ads1015 = Device([I2C_ADDRESS_DEFAULT, I2C_ADDRESS_ALTERNATE], i2c_dev=self._i2c_dev, bit_width=8, registers=(
            Register('CONFIG', 0x01, fields=(
                BitField('operational_status', 0b1000000000000000, adapter=LookupAdapter({
                    'active': 0,
                    'inactive_start': 1
                })),
                BitField('multiplexer',         0b0111000000000000),
                BitField('programmable_gain',   0b0000111000000000, adapter=LookupAdapter({
                    6.144: 0b000,
                    4.096: 0b001,
                    2.048: 0b010,
                    1.024: 0b011,
                    0.512: 0b100,
                    0.256: 0b101
                })),
                BitField('mode',                0b0000000100000000),
                BitField('data_rate_sps',       0b0000000001110000, adapter=LookupAdapter({
                    128: 0b000,
                    250: 0b001,
                    490: 0b010,
                    920: 0b011,
                    1600: 0b100,
                    2400: 0b101,
                    3300: 0b110
                })),
                BitField('comparator_mode',     0b0000000000010000, adapter=LookupAdapter({
                    'traditional': 0b0,  # Traditional comparator with hystersis
                    'window': 0b01
                })),
                BitField('comparator_polarity', 0b0000000000001000, adapter=LookupAdapter({
                    'active_low': 0b0,
                    'active_high': 0b1
                })),
                BitField('comparator_latching',    0b0000000000000100),
                BitField('comparator_queue',    0b0000000000000011, adapter=LookupAdapter({
                    'one': 0b00,
                    'two': 0b01,
                    'four': 0b10,
                    'disabled': 0b11
                }))
            ), bit_width=16),
            Register('CONV', 0x00, fields=(
                BitField('value', 0xFFF0)
            ))
        ))
