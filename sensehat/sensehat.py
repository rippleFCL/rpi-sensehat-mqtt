"""
Module to interface with the SenseHAT API
"""

from sense_hat import SenseHat
import time

class SenseHatJoystick():
    pass

class SenseHatLed():
    pass

class SenseHatSensor():
    """
    Generates a SenseHAT sensor object
    """
    # class defaults
    # number of decimals for float variables
    ROUNDING = 4
    # converts Gs (default) to meters/square second; set to 1 for default
    ACCELERATION_MULTIPLYER = 9.80665
    # convert the rotational intensity in radians/second (default) to something else; set to 1 for default
    GYROSCOPE_MULTIPLYER = 1
    # data keys
    TIME = 'time'
    PRESSURE = 'pressure'
    TEMPERATURE = 'temperature'
    TEMPERATURE_01 = 'from_humidity'
    TEMPERATURE_02 = 'from_pressure'
    HUMIDITY = 'humidity'
    GYROSCOPE = 'gyroscope'
    GYROSCOPE_01 = 'pytch'
    GYROSCOPE_02 = 'roll'
    GYROSCOPE_03 = 'yaw'
    COMPASS = 'compass'
    COMPASS_NORTH = 'north'
    ACCELERATION = 'acceleration'
    ACCELERATION_01 = 'x'
    ACCELERATION_02 = 'y'
    ACCELERATION_03 = 'z'

    def __init__(self,
                zone:str,
                room:str,
                sensor:str,
                low_light:bool = True):
        self.zone = zone
        self.room = room
        self.sensor = sensor
        self.low_light = low_light
        # sensors variables
        self.__time = None
        self.__pressure = None
        self.__temperature_01 = self.__temperature_02 = None
        self.__humidity = None
        self.__gyroscope_01 = self.__gyroscope_02 = self.__gyroscope_03 = None
        self.__compass_north = None
        self.__acceleration_01 = self.__acceleration_02 = self.__acceleration_03 = None
        # create a private SenseHat object to interact with the sensors API
        self.__sense = SenseHat()
        # read initial sensor valus
        self.data = self.sensors_data()
        # TODO: log sensehat object initialized
    
    def sensors_data(self) -> dict:
        """
        Method that updates all of the private sensor variables and 
        returns a dict containing the current values of each.
        """
        # https://docs.python.org/3/library/time.html#time.asctime
        self.__time = time.asctime()
        # https://pythonhosted.org/sense-hat/api/
        self.__pressure = round(self.__sense.get_pressure(), SenseHatSensor.ROUNDING)
        self.__temperature_01 = round(self.__sense.get_temperature(), SenseHatSensor.ROUNDING)
        self.__temperature_02 = round(self.__sense.get_temperature_from_pressure(), SenseHatSensor.ROUNDING)
        self.__humidity = round(self.__sense.get_humidity(), SenseHatSensor.ROUNDING)
        self.__gyroscope_01 = round(
            self.__sense.get_gyroscope_raw().get("x") * SenseHatSensor.GYROSCOPE_MULTIPLYER,
            SenseHatSensor.ROUNDING)
        self.__gyroscope_02 = round(
            self.__sense.get_gyroscope_raw().get("y") * SenseHatSensor.GYROSCOPE_MULTIPLYER,
            SenseHatSensor.ROUNDING)
        self.__gyroscope_03 = round(
            self.__sense.get_gyroscope_raw().get("z") * SenseHatSensor.GYROSCOPE_MULTIPLYER,
            SenseHatSensor.ROUNDING)
        self.__compass_north = round(self.__sense.get_compass(), SenseHatSensor.ROUNDING)
        self.__acceleration_01 = round(
            self.__sense.get_accelerometer_raw().get("x") * SenseHatSensor.ACCELERATION_MULTIPLYER,
            SenseHatSensor.ROUNDING)
        self.__acceleration_02 = round(
            self.__sense.get_accelerometer_raw().get("y") * SenseHatSensor.ACCELERATION_MULTIPLYER,
            SenseHatSensor.ROUNDING)
        self.__acceleration_03 = round(
            self.__sense.get_accelerometer_raw().get("z") * SenseHatSensor.ACCELERATION_MULTIPLYER,
            SenseHatSensor.ROUNDING)
        # generate and update data structure
        data = {
            self.zone : {
                self.room : {
                    self.sensor : {
                        SenseHatSensor.TIME : self.__time,
                        SenseHatSensor.PRESSURE : self.__pressure,
                        SenseHatSensor.TEMPERATURE : {
                            SenseHatSensor.TEMPERATURE_01 : self.__temperature_01,
                            SenseHatSensor.TEMPERATURE_02 : self.__temperature_02
                        },
                        SenseHatSensor.HUMIDITY : self.__humidity,
                        SenseHatSensor.GYROSCOPE : {
                            SenseHatSensor.GYROSCOPE_01 : self.__gyroscope_01,
                            SenseHatSensor.GYROSCOPE_02 : self.__gyroscope_02,
                            SenseHatSensor.GYROSCOPE_03 : self.__gyroscope_03
                        },
                        SenseHatSensor.COMPASS : {
                            SenseHatSensor.COMPASS_NORTH : self.__compass_north
                        },
                        SenseHatSensor.ACCELERATION : {
                            SenseHatSensor.ACCELERATION_01 : self.__acceleration_01,
                            SenseHatSensor.ACCELERATION_02 : self.__acceleration_02,
                            SenseHatSensor.ACCELERATION_03 : self.__acceleration_03
                        }
                    }
                }
            }
        }
        return data

