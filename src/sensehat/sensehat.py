"""
Module to interface with the SenseHAT API
"""

# local imports
from src.constants import constants as const
# external imports
import logging
from sense_hat import SenseHat
import time

# start a loggin instance for this module using constants
logging.basicConfig(filename=const.LOG_FILENAME, format=const.LOG_FORMAT, datefmt=const.LOG_DATEFMT)
logger = logging.getLogger(__name__)
logger.setLevel(const.LOG_LEVEL)
logger.debug("Initilized a logger object.")

class SenseHatJoystick():
    pass

class SenseHatLed():
    pass

class SenseHatSensor():
    """
    Generates a SenseHAT sensor object
    """
    # data keys label convention for the class objects
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
                low_light:bool = True,
                rounding:int = 4,
                acceleration_multiplier:float = 1.0,
                gyroscope_multiplier:float = 1.0):
        self.zone = zone
        self.room = room
        self.sensor = sensor
        self.low_light = low_light
        self.rounding = rounding
        self.acceleration_multiplier = acceleration_multiplier
        self.gyroscope_multiplier = gyroscope_multiplier
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
        # read initial sensor values
        self.data = self.sensors_data()
        logger.info(f"A sensehat object for sensor '{self.sensor}' was initialized.")
    
    def sensors_data(self) -> dict:
        """
        Method that updates all of the private sensor variables and 
        returns a dict containing the current values of each.
        """
        # https://docs.python.org/3/library/time.html#time.asctime
        self.__time = time.asctime()
        # https://pythonhosted.org/sense-hat/api/
        self.__pressure = round(self.__sense.get_pressure(), self.rounding)
        self.__temperature_01 = round(self.__sense.get_temperature(), self.rounding)
        self.__temperature_02 = round(self.__sense.get_temperature_from_pressure(), self.rounding)
        self.__humidity = round(self.__sense.get_humidity(), self.rounding)
        self.__gyroscope_01 = round(
            self.__sense.get_gyroscope_raw().get("x") * self.gyroscope_multiplier,
            self.rounding)
        self.__gyroscope_02 = round(
            self.__sense.get_gyroscope_raw().get("y") * self.gyroscope_multiplier,
            self.rounding)
        self.__gyroscope_03 = round(
            self.__sense.get_gyroscope_raw().get("z") * self.gyroscope_multiplier,
            self.rounding)
        self.__compass_north = round(self.__sense.get_compass(), self.rounding)
        self.__acceleration_01 = round(
            self.__sense.get_accelerometer_raw().get("x") * self.acceleration_multiplier,
            self.rounding)
        self.__acceleration_02 = round(
            self.__sense.get_accelerometer_raw().get("y") * self.acceleration_multiplier,
            self.rounding)
        self.__acceleration_03 = round(
            self.__sense.get_accelerometer_raw().get("z") * self.acceleration_multiplier,
            self.rounding)
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
        logger.info(f"A call to read and assign updated sensor data was made.")
        logger.debug(f"Data: '{data}'")
        return data

    def disable(self):
        """
        If appropriate, this method should be called during cleanup procedures.
        For example, to turn off the LED matrix.
        """
        pass

