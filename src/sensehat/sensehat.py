"""
Module to interface with the SenseHAT API

Related doc: https://pythonhosted.org/sense-hat/api/
"""

# local imports
from src.constants import constants as const
from src.utils import validate as val
from src.errors import errors as err
# local emulation settings
if const.SENSEHAT_EMULATION:
    from sense_emu import SenseHat as Sense
    from sense_emu import ACTION_PRESSED, ACTION_HELD, ACTION_RELEASED
else:
    from sense_hat import SenseHat as Sense
    from sense_hat import ACTION_PRESSED, ACTION_HELD, ACTION_RELEASED
# external imports
import logging
from time import asctime
from abc import ABC, abstractmethod
from queue import Queue
from threading import Event

# start a loggin instance for this module using constants
logging.basicConfig(filename=const.LOG_FILENAME, format=const.LOG_FORMAT, datefmt=const.LOG_DATEFMT)
logger = logging.getLogger(__name__)
logger.setLevel(const.LOG_LEVEL)
logger.debug("Initilized a logger object.")

class SenseHat(ABC):
    """
    ABC for SenseHat Joystick, LED, and Sensor subclasses.
    Add any arg or method that should be common to subclasses here.
    """
    def __init__(self):
        # create a private SenseHat object to interact with the sensors API
        self._sense = Sense()
        # helpers
        self._is_enabled = False
    
    @property
    def sense(self):
        return self._sense
    @sense.setter
    def sense(self, sense:Sense):
        self._sense = sense

    @property
    def is_enabled(self):
        return self._is_enabled
    @is_enabled.setter
    def is_enabled(self, boolean:bool):
        self._is_enabled = boolean

    @abstractmethod
    def disable(self):
        """
        Method to be called during cleanup procedures to disable/undo performed operations
        """
        pass

class SenseHatJoystick(SenseHat):
    """
    Generates a SenseHAT Joystick object.
    """
    # class direction conventions
    DIRECTION = 'direction'

    def __init__(self):
        super().__init__()
        # queue for directions made by the joystick
        self._directions = Queue()
        # init flag for the detection of joystick directions
        self._stop_flag = Event()
        self.is_enabled = True
        logger.info("A sensehat object for its joystick matrix was initialized.")
    
    @property
    def directions(self):
        return self._directions
    @directions.setter
    def directions(self, directions:Queue):
        self._directions = directions

    @property
    def stop_flag(self):
        return self._stop_flag
    @stop_flag.setter
    def stop_flag(self, stop_flag:Event):
        self._stop_flag = stop_flag

    def disable(self):
        logger.debug(f"Received a call to disable a joystick sense object.")
        # Nothing else to do because does not change states of physical components
        if self.is_enabled:
            self.is_enabled = False

    # class specific methods
    def wait_directions(self, external_event:Event=False):
        """
        Method to put this class object into wait for stick directions mode.
        Receives an optional external (threading) event to control loop.
        Directions are queued in 'directions', so if not 'directions.empty()',
        dequeue and process them.
        """
        logger.info(f"Waiting for joystick directions.")
        while not external_event.is_set() and not self.stop_flag.is_set():
            for event in self.sense.stick.get_events():
                if event.action == ACTION_RELEASED:
                    logger.info(f"Detected a joystick release for direction '{event.direction}.'.")
                    self.directions.put(event.direction)
                    self.stop_flag.set()
        # reset the stop flag before the next call
        self.stop_flag.clear()

    def joystick_data(self) -> dict:
        if self.directions.empty():
            return {SenseHatJoystick.DIRECTION : ''}
        return {SenseHatJoystick.DIRECTION : self.directions.get()}

class SenseHatLed(SenseHat):
    """
    Generates a SenseHAT LED object.
    An object of this class has a 'sense' attribute that allows interacting with the SenseHat API directly.
    This is convenient because the SenseHAT API already has many methods for the LED matrix.
    For more info, see https://pythonhosted.org/sense-hat/api/#led-matrix.
    """
    def __init__(self,
                set_rotation:int=0,
                low_light:bool=True):
        super().__init__()
        # LED variables
        self._set_rotation = set_rotation
        self._low_light = low_light
        # clear LED and init pixels list attribute
        self.sense.clear()
        self.sense.set_rotation(self.set_rotation)
        self.sense.low_light = self.low_light
        # List containing 64 smaller lists of [R, G, B] pixels (red, green, blue)
        # representing the 8x8 LED matrix.
        self._pixels = self.sense.get_pixels()
        self.is_enabled = True
        logger.info(f"A sensehat object for its LED matrix was initialized.")

    @property
    def set_rotation(self):
        return self._set_rotation
    @set_rotation.setter
    def set_rotation(self, degree:int):
        self._set_rotation = degree
        self.sense.set_rotation(self.set_rotation)

    @property
    def low_light(self):
        return self._low_light
    @low_light.setter
    def low_light(self, state:bool):
        self._low_light = state
        self.sense.low_light = self.low_light

    @property
    def pixels(self):
        return self._pixels
    @pixels.setter
    def pixels(self, pixels:list):
        if not val.pixels(pixels):
            logger.info(f"The following pixels LED of length '{len(pixels)}' is invalid: '{pixels}'.")
            raise err.InvalidSenseAttr(f"The pixels LED of length '{len(pixels)}' is invalid.", 'pixels')
        self._pixels = pixels

    def disable(self):
        logger.debug(f"Received a call to disable an LED sense object.")
        # Must turn off the LED matrix before disabling the object
        if self.is_enabled:
            self.sense.clear()
            self.is_enabled = False

class SenseHatSensor(SenseHat):
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
    GYROSCOPE_01 = 'pitch'
    GYROSCOPE_02 = 'roll'
    GYROSCOPE_03 = 'yaw'
    COMPASS = 'compass'
    COMPASS_NORTH = 'north'
    ACCELERATION = 'acceleration'
    ACCELERATION_01 = 'x'
    ACCELERATION_02 = 'y'
    ACCELERATION_03 = 'z'

    def __init__(self,
                rounding:int = 4,
                acceleration_multiplier:float = 1.0,
                gyroscope_multiplier:float = 1.0):
        super().__init__()
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
        # read initial sensor values
        self.data = self.sensors_data()
        self.is_enabled = True
        logger.info(f"A sensehat object for its sensors was initialized.")
    
    def sensors_data(self) -> dict:
        """
        Method that updates all of the private sensor variables and 
        returns a dict containing the current values of each.
        """
        # https://docs.python.org/3/library/time.html#time.asctime
        self.__time = asctime()
        self.__pressure = round(self.sense.get_pressure(), self.rounding)
        self.__temperature_01 = round(self.sense.get_temperature(), self.rounding)
        self.__temperature_02 = round(self.sense.get_temperature_from_pressure(), self.rounding)
        self.__humidity = round(self.sense.get_humidity(), self.rounding)
        self.__gyroscope_01 = round(self.sense.get_gyroscope_raw().get("x") * self.gyroscope_multiplier, self.rounding)
        self.__gyroscope_02 = round(self.sense.get_gyroscope_raw().get("y") * self.gyroscope_multiplier, self.rounding)
        self.__gyroscope_03 = round(self.sense.get_gyroscope_raw().get("z") * self.gyroscope_multiplier, self.rounding)
        self.__compass_north = round(self.sense.get_compass(), self.rounding)
        self.__acceleration_01 = round(self.sense.get_accelerometer_raw().get("x") * self.acceleration_multiplier, self.rounding)
        self.__acceleration_02 = round(self.sense.get_accelerometer_raw().get("y") * self.acceleration_multiplier, self.rounding)
        self.__acceleration_03 = round(self.sense.get_accelerometer_raw().get("z") * self.acceleration_multiplier, self.rounding)
        # generate and update data structure
        data = {
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
            },
        }
        logger.info(f"A call to read and assign updated sensor data was made.")
        logger.debug(f"Data: '{data}'")
        return data

    def disable(self):
        logger.debug(f"Received a call to disable a sensor sense object.")
        # This clas does not change the state of SenseHAT components, so nothing else to do here
        if self.is_enabled:
            self.is_enabled = False
