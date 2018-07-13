#! /usr/bin/python

import time
import Turta_DS18B20

#Initialize
ds18b20 = Turta_DS18B20.DS18B20Sensor(Turta_DS18B20.TempUnits.Celcius)

print("Detected sensors:")
serials = ds18b20.list_sensors()
for sn in serials:
    print(sn)

try:
    while 1:
        #Read temperature from all connected DS18B20 sensors.
        results = ds18b20.read_temp_from_all_sensors()

        for senRes in results:
            print("SN: " + senRes[0] + ", Temp: " + str(round(senRes[1], 1)))

        #Read temperature from desired sensor.
        print("Temp by SN: " + str(round(ds18b20.read_temp_by_serial("28-000000000000"), 1)))

        time.sleep(2.0)


except KeyboardInterrupt:
    print('Bye.')