from ads1015 import ADS1015
ads1015 = ADS1015()
value = ads1015._ads1015.CONV.get_value()
print(value)
