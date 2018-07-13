# Turta Helper for Raspbian
# Distributed under the terms of the MIT license.

# Python Driver for Maxim DS18B20 Temperature Sensor
# Version 1.00 (Initial Release)
# Updated: July 14th, 2018

# For hardware info, visit www.turta.io
# For questions e-mail turta@turta.io

# You'll need to add the following line to the /boot/config.txt
# dtoverlay=w1-gpio,gpiopin=21
# Then change the gpiopin parameter to the relevant BCM GPIO number.
# If you're using more than one GPIO pin for OneWire,
# add multiple dtoverlay lines and modify the gpiopin parameters.
# A reboot will be required after config.txt modification.

import glob
import os
from enum import IntEnum

#Enumerations

class TempUnits(IntEnum):
    Celcius = 1
    Fahrenheit = 2

class DS18B20Sensor:
    """DS18B20 Sensor"""
    #Global variable to keep temperature unit.
    convertToFahrenheit = False

    def __init__(self, temp_unit):
        """Initiates the OneWire bus to get temperature from DS18B20 sensors."""

        #Check argument type.
        if not isinstance(temp_unit, TempUnits):
            raise TypeError('temp_unit must be an instance of TempUnits Enum')

        #Set temperature unit.
        self.convertToFahrenheit = True if temp_unit == 2 else False

        #Execute shell commands to initialize OneWire interface.
        os.system("modprobe w1-gpio")
        os.system("modprobe w1-therm")
        return

    def list_sensors(self):
        """Returns available DS18B20 sensor serial numbers on the OneWire bus."""
        #Search for DS18B20 sensors.
        sensors = glob.glob('/sys/bus/w1/devices/28-*')
        sensorList = []

        #Trim sensor paths to get serial numbers.
        for sensor in sensors:
            sensorList.append(sensor[20:])

        #Return sensor serial numbers, starting with "28-".
        return sensorList

    def _c_to_f(self, celcius):
        """Converts given Celcius value to Fahrenheit value."""
        return celcius * 1.8 + 32

    def read_temp_from_first_sensor(self):
        """Returns temperature from the first detected DS18B20 sensor."""
        sensors = self.list_sensors()

        for sensor in sensors:
            with open("/sys/bus/w1/devices/" + sensor + "/w1_slave") as sf:
                response = sf.readlines()

                #If CRC is OK:
                if response[0].strip()[-3:] == "YES":
                    tempPosition = response[1].find("t=")
                    #And if temperature data exists:
                    if tempPosition != -1:
                        temperature = float(response[1][tempPosition + 2:]) / 1000.0

                        #Return temperature.
                        return self._c_to_f(temperature) if self.convertToFahrenheit else temperature

        #Return -100 if no sensor is available.
        return -100

    def read_temp_from_all_sensors(self):
        """Returns temperatures from all detected DS18B20 sensors as SN & temperature in a 2D array."""
        results = []
        sensors = self.list_sensors()

        for sensor in sensors:
            with open("/sys/bus/w1/devices/" + sensor + "/w1_slave") as sf:
                response = sf.readlines()

                #If CRC is OK:
                if response[0].strip()[-3:] == "YES":
                    tempPosition = response[1].find("t=")
                    #And if temperature data exists:
                    if tempPosition != -1:
                        temperature = float(response[1][tempPosition + 2:]) / 1000.0

                        #Add sensor serial number and temperature to the array.
                        results.append([sensor, self._c_to_f(temperature) if self.convertToFahrenheit else temperature])

        #Return results.
        return results

    def read_temp_by_serial(self, serial_number):
        """Returns temperature from the queried DS18B20 sensor."""
        #Read temperatures from all detected sensors.
        values = self.read_temp_from_all_sensors()

        for senRes in values:
            #If sensor's serial number matches with the given serial number:
            if senRes[0] == serial_number:
                #Return temperature.
                return senRes[1]

        #Return -100 if no sensor is found for the given serial number.
        return -100

    #Disposal
    def __del__(self):
        """Releases the resources."""
        del self.convertToFahrenheit
        return