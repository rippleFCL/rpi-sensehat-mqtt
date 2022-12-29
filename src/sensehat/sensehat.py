"""
Module to interface with the SenseHAT API

Related doc: https://pythonhosted.org/sense-hat/api/
"""

# local imports
from src.constants import constants as const
# emulation settings
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
from signal import pause
from queue import Queue

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
    
    @property
    def sense(self):
        return self._sense
    @sense.setter
    def sense(self, sense:Sense):
        self._sense = sense

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
    LEFT = 'left'
    RIGHT = 'right'
    UP = 'up'
    DOWN = 'down'
    MIDDLE = 'pressed'
    DIRECTIONS = [UP, DOWN, LEFT, RIGHT, MIDDLE]

    def __init__(self):
        super().__init__()
        # queue for directions made by the joystick
        self._directions = Queue()
    
    @property
    def directions(self):
        return self._directions
    @directions.setter
    def directions(self, directions:Queue):
        self._directions = directions

    def disable(self):
        # Nothing to do because does not change states of physical components
        pass

    # class specific methods
    def __pushed_up(self, event):
        if event.action != ACTION_RELEASED:
            self.directions.put(SenseHatJoystick.UP)

    def __pushed_down(self, event):
        if event.action != ACTION_RELEASED:
            self.directions.put(SenseHatJoystick.DOWN)

    def __pushed_left(self, event):
        if event.action != ACTION_RELEASED:
            self.directions.put(SenseHatJoystick.LEFT)

    def __pushed_right(self, event):
        if event.action != ACTION_RELEASED:
            self.directions.put(SenseHatJoystick.RIGHT)
        
    def __middle_click(self, event):
        if event.action != ACTION_RELEASED:
            self.directions.put(SenseHatJoystick.MIDDLE)
    
    def wait_directions(self):
        """
        Method to put this class object into wait for stick directions mode.
        Directions are queued in 'directions', so if not 'directions.empty()',
        dequeue and process them.
        """
        # run these functions whenever the stick is moved
        self.sense.stick.direction_up = self.__pushed_up
        self.sense.stick.direction_down = self.__pushed_down
        self.sense.stick.direction_left = self.__pushed_left
        self.sense.stick.direction_right = self.__pushed_right
        # when joystick is clicked
        self.sense.stick.direction_middle = self.__middle_click
        # wait for interrupt
        logger.info(f"The client/type '{self.client_id}/{self.type}' is waiting for stick directions.")
        pause()

class SenseHatLed(SenseHat):
    """
    Generates a SenseHAT LED object.
    An object of this class has a 'sense' attribute that allows interacting with the SenseHat API directly.
    This is convenient because the SenseHAT API already has many methods for the LED matrix.
    For more info, see https://pythonhosted.org/sense-hat/api/#led-matrix.
    """
    def __init__(self,
                low_light:bool=True):
        super().__init__()
        # LED variables
        self._low_light = low_light
        # clear LED and init pixels list attribute
        self.sense.clear()
        # List containing 64 smaller lists of [R, G, B] pixels (red, green, blue)
        # representing the 8x8 LED matrix.
        self._pixels = self.sense.get_pixels
        logger.info(f"A sensehat object for its LED matrix was initialized.")

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
        # TODO: validade
        self._pixels = pixels

    def disable(self):
        # Must turn off the LED matrix before disabling the object
        self.sense.clear()

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
        # This clas does not change the state of SenseHAT components
        pass

