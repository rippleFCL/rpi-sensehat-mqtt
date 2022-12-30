"""
Module that parses an initialization (INI) config file
"""

# local imports
from src.constants import constants as const
from src.errors import errors as err
from src.utils import validate as val
# external imports
import logging
from configparser import ConfigParser, Error

# start a loggin instance for this module using constants
logging.basicConfig(filename=const.LOG_FILENAME, format=const.LOG_FORMAT, datefmt=const.LOG_DATEFMT)
logger = logging.getLogger(__name__)
logger.setLevel(const.LOG_LEVEL)
logger.debug("Initilized a logger object.")

class Configuration():
    """
    Class that generates a configuration object from an initialization (INI) file
    """
    # fallbacks for configuration variables
    # DEFAULT
    RESOLUTION = 300
    # MQTT
    MQTT_CLIENT_NAME = 'sensehat01'
    MQTT_BROKER_ADDRESS = 'mqtt://127.0.0.1:1883'
    MQTT_ZONE = "downstairs"
    MQTT_ROOM = "livingroom"
    # SENSEHAT
    SENSEHAT_LOW_LIGHT = True
    SENSEHAT_ROUNDING = 4
    SENSEHAT_ACCELERATION_MULTIPLIER = 9.80665
    SENSEHAT_GYROSCOPE_MULTIPLIER = 1.0

    def __init__(self, config_dir = './', config_file = 'CONFIG.ini'):
        if not val.file_exists(config_dir + config_file):
            logger.info(f"The INI file '{config_dir + config_file}' does not exist.")
            raise err.InvalidConfigFile(f"The INI file '{config_dir + config_file}' does not exist.",
                                        f"{config_dir + config_file}")
        self.config_full_path_file = config_dir + config_file
        # init raw config with None and then set keys and values from INI file via load method
        self.__raw_config = None
        self.__load_raw_config()
        # init config attributes with class defaults and then set valus from raw config via load method
        self.__resolution = Configuration.RESOLUTION
        self.__welcome_msg = None
        self.__mqtt_broker_address = Configuration.MQTT_BROKER_ADDRESS
        self.__mqtt_client_name = Configuration.MQTT_CLIENT_NAME
        self.__mqtt_user = None
        self.__mqtt_password = None
        self.__mqtt_credentials_enabled = False
        self.__mqtt_zone = Configuration.MQTT_ZONE
        self.__mqtt_room = Configuration.MQTT_ROOM
        self.__sensehat_low_light = Configuration.SENSEHAT_LOW_LIGHT
        self.__sensehat_rounding = Configuration.SENSEHAT_ROUNDING
        self.__sensehat_acceleration_multiplier = Configuration.SENSEHAT_ACCELERATION_MULTIPLIER
        self.__sensehat_gyroscope_multiplier = Configuration.SENSEHAT_GYROSCOPE_MULTIPLIER
        self.__load_config_attributes()
        logger.info(f"A config object for the INI file '{self.config_full_path_file}' was initialized.")

    def __load_raw_config(self):
        config_parser = ConfigParser()
        try:
            config_parser.read(self.config_full_path_file)
            self.__raw_config = config_parser
        except Error as parse_error:
            logger.info(f"Unable to parse the INI file '{self.config_full_path_file}'. Error: '{parse_error.message}'")
            raise err.ConfigParseError(f"Unable to parse the INI file '{self.config_full_path_file}'.", parse_error.message)

    def __load_config_attributes(self):
        # DEFAULT
        # resolution
        if 'resolution' in self.__raw_config['DEFAULT']:
            self.resolution = self.__raw_config['DEFAULT'].getint('resolution', Configuration.RESOLUTION)
        # welcome_msg
        if 'welcome_msg' in self.__raw_config['DEFAULT']:
            self.__welcome_msg = self.__raw_config['DEFAULT'].get('welcome_msg', None)
        
        # MQTT
        # mqtt_client_name
        if 'mqtt' in self.__raw_config.sections():
            self.__mqtt_client_name = self.__raw_config['mqtt'].get('client_name', Configuration.MQTT_CLIENT_NAME)
        # mqtt_broker_address
        if 'mqtt' in self.__raw_config.sections():
            self.__mqtt_broker_address = self.__raw_config['mqtt'].get('broker_address', Configuration.MQTT_BROKER_ADDRESS)
        # mqtt_user
        if 'mqtt' in self.__raw_config.sections():
            self.__mqtt_user = self.__raw_config['mqtt'].get('user', None)
        # mqtt_password
        if 'mqtt' in self.__raw_config.sections():
            self.__mqtt_password = self.__raw_config['mqtt'].get('password', None)
        # mqtt_credentials_enabled
        # assume that user is None if MQTT does not use credentials
        self.__mqtt_credentials_enabled = True if self.mqtt_user else False
        # mqtt_zone
        if 'mqtt' in self.__raw_config.sections():
            self.mqtt_zone = self.__raw_config['mqtt'].get('zone', Configuration.MQTT_ZONE)
        # mqtt_room
        if 'mqtt' in self.__raw_config.sections():
            self.mqtt_room = self.__raw_config['mqtt'].get('room', Configuration.MQTT_ROOM)
        
        # SENSEHAT
        # sensehat_low_light
        if 'sensehat' in self.__raw_config.sections():
            self.__sensehat_low_light = self.__raw_config['sensehat'].getboolean('low_light', Configuration.SENSEHAT_LOW_LIGHT)
        # sensehat_rounding
        if 'sensehat' in self.__raw_config.sections():
            self.sensehat_rounding = self.__raw_config['sensehat'].getint('rounding', Configuration.SENSEHAT_ROUNDING)
        # sensehat_acceleration_multiplier
        if 'sensehat' in self.__raw_config.sections():
            self.__sensehat_acceleration_multiplier= self.__raw_config['sensehat'].getfloat('acceleration_multiplier',
                Configuration.SENSEHAT_ACCELERATION_MULTIPLIER)
        # sensehat_gyroscope_multiplier
        if 'sensehat' in self.__raw_config.sections():
            self.__sensehat_gyroscope_multiplier = self.__raw_config['sensehat'].getfloat('gyroscope_multiplier',
                Configuration.SENSEHAT_GYROSCOPE_MULTIPLIER)

    # Add validations to setter logic whenever necessary and when loading attrb,
    # refer to this setter in the logic
    @property
    def resolution(self):
        return self.__resolution
    @resolution.setter
    def resolution(self, resolution:int):
        if not val.resolution(resolution):
            logger.info(f"Resolution cannot be set to '{resolution}'. Fix config file.")
            raise err.InvalidConfigAttr(f"Cannot set resolution to '{resolution}'.", 'resolution')
        self.__resolution = resolution

    @property
    def welcome_msg(self):
        return self.__welcome_msg
    
    @property
    def mqtt_client_name(self):
        return self.__mqtt_client_name

    @property
    def mqtt_broker_address(self):
        return self.__mqtt_broker_address

    @property
    def mqtt_user(self):
        return self.__mqtt_user

    @property
    def mqtt_password(self):
        return self.__mqtt_password

    @property
    def mqtt_credentials_enabled(self):
        return self.__mqtt_credentials_enabled
    
    @property
    def mqtt_zone(self):
        return self.__mqtt_zone
    @mqtt_zone.setter
    def mqtt_zone(self, zone:str):
        if not val.zone(zone):
            logger.info(f"Zone '{zone}' contains invalid characters. Fix config file.")
            raise err.InvalidConfigAttr(f"Zone '{zone}' contains invalid characters.", 'zone')
        self.__mqtt_zone = zone

    @property
    def mqtt_room(self):
        return self.__mqtt_room
    @mqtt_room.setter
    def mqtt_room(self, room:str):
        if not val.room(room):
            logger.info(f"Room '{room}' contains invalid characters. Fix config file.")
            raise err.InvalidConfigAttr(f"Room '{room}' contains invalid characters.", 'room')
        self.__mqtt_room = room
    
    @property
    def sensehat_low_light(self):
        return self.__sensehat_low_light
    
    @property
    def sensehat_rounding(self):
        return self.__sensehat_rounding
    @sensehat_rounding.setter
    def sensehat_rounding(self, rounding:int):
        if not val.rounding(rounding):
            logger.info(f"Rounding cannot be set to '{rounding}. Fix config file.'")
            raise err.InvalidConfigAttr(f"Rounding cannot be set to '{rounding}.", 'rounding')

    @property
    def sensehat_acceleration_multiplier(self):
        return self.__sensehat_acceleration_multiplier

    @property
    def sensehat_gyroscope_multiplier(self):
        return self.__sensehat_gyroscope_multiplier
