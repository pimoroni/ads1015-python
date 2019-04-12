import time
from ads1015 import ADS1015


ads1015 = ADS1015()
ads1015.set_multiplexer('in0/ref')
ads1015.set_mode('single')
ads1015.set_programmable_gain(2.048)

while True:
    ads1015.set_status('active')
    while ads1015.get_status():
        time.sleep(0.001)

    # value = ads1015._ads1015.CONV.get_value()
    value = ads1015.get_conversion_value()
    print(value)
    time.sleep(0.5)
