import time

import smbus2

from ads1015 import ADS1015

bus = smbus2.SMBus(1)

ads1015 = ADS1015()
ads1015.set_mode("single")
ads1015.set_programmable_gain(2.048)
ads1015.set_sample_rate(1600)

channels = ["in0/ref", "in1/ref", "in2/ref"]

reference = ads1015.get_reference_voltage()

print("Reference voltage: {}".format(reference))

while True:
    for channel in channels:
        value = ads1015.get_compensated_voltage(
            channel=channel, reference_voltage=reference
        )
        print("{}: {}".format(channel, value))

    print("")
    time.sleep(0.5)
