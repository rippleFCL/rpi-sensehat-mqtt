"""
Module that parses an initialization (INI) config file
"""

from os import path
from random import randint
from configparser import ConfigParser, Error

class Configuration():
    """
    Class that generates a configuration object from an initialization (INI) file
    """
    
    # class fallbacks for required variables
    # DEFAULT
    RESOLUTION = 300
    # MQTT
    CLIENT_ID = 'SenseHAT_RND'+str(randint(0,99))
    MQTT_BROKER_ADDRESS = 'mqtt://127.0.0.1:1883'
    MQTT_CHANNEL = "hass"
    MQTT_ZONE = "downstairs"
    MQTT_ROOM = "living-room"
    MQTT_SENSOR = "sensehat"
    # LOG
    LOG_DIR = './logs/'
    LOG_FILE = 'rpi_sensehat_mqtt.log'
    LOG_FORMAT = '%(asctime)s.%(msecs)03d %(levelname)s\t[%(name)s] %(message)s'
    LOG_DATEFMT = '%Y-%m-%dT%H:%M:%S'
    LOG_LEVEL = 'INFO'

    def __init__(self, config_dir = './', config_file = 'CONFIG.ini'):
        self.config_full_path_file = config_dir + config_file
        if not path.isfile(self.config_full_path_file):
            # TODO: log error here
            raise OSError(filename=self.config_full_path_file)
        self.__raw_config = None
        self.__load_config()
        # TODO: validate data here

    def __load_config(self):
        config_parser = ConfigParser()
        try:
            config_parser.read(self.configPath)
            self.__raw_config = config_parser
        except Error as err:
            # TODO: log err here
            # TODO: raise a custom error for main app to catch passing err
            pass

    # Getters for the configuration keys in the config file
    # Each getter validades and assigns fallbacks when appropriate
    @property
    def resolution(self):
        if 'resolution' in self.__raw_config['DEFAULT']:
            resolution = self.__raw_config['DEFAULT'].getint('resolution', Configuration.RESOLUTION)
            if resolution > 0:
                return resolution
        return Configuration.RESOLUTION
    
    @property
    def welcome_msg(self):
        if 'welcome_msg' in self.__raw_config['DEFAULT']:
            welcome_msg = self.__raw_config['DEFAULT'].getint('welcome_msg', None)
            return welcome_msg
        return None
    
    @property
    def mqtt_client_id(self):
        if 'mqtt' in self.__raw_config.sections():
            client_id = self.__raw_config['mqtt'].get('client_id', Configuration.CLIENT_ID)
            return client_id
        return Configuration.CLIENT_ID

    @property
    def mqtt_broker_address(self):
        if 'mqtt' in self.__raw_config.sections():
            broker_address = self.__raw_config['mqtt'].get('broker_address', Configuration.MQTT_BROKER_ADDRESS)
            return broker_address
        return Configuration.MQTT_BROKER_ADDRESS

    @property
    def mqtt_user(self):
        if 'mqtt' in self.__raw_config.sections():
            user = self.__raw_config['mqtt'].get('user', None)
            return user
        return None

    @property
    def mqtt_password(self):
        if 'mqtt' in self.__raw_config.sections():
            password = self.__raw_config['mqtt'].get('password', None)
            return password
        return None

    @property
    def mqtt_credentials_enabled(self):
        # assume that user is None if MQTT does not use credentials
        return True if self.mqtt_user else False
    
    @property
    def mqtt_channel(self):
        if 'mqtt' in self.__raw_config.sections():
            channel = self.__raw_config['mqtt'].get('channel', Configuration.MQTT_CHANNEL)
            return channel
        return Configuration.MQTT_CHANNEL

    @property
    def mqtt_zone(self):
        if 'mqtt' in self.__raw_config.sections():
            zone = self.__raw_config['mqtt'].get('zone', Configuration.MQTT_ZONE)
            return zone
        return Configuration.MQTT_ZONE

    @property
    def mqtt_room(self):
        if 'mqtt' in self.__raw_config.sections():
            room = self.__raw_config['mqtt'].get('room', Configuration.MQTT_ROOM)
            return room
        return Configuration.MQTT_ROOM

    @property
    def mqtt_sensor(self):
        if 'mqtt' in self.__raw_config.sections():
            sensor = self.__raw_config['mqtt'].get('sensor', Configuration.MQTT_SENSOR)
            return sensor
        return Configuration.MQTT_SENSOR

    @property
    def log_filename(self):
        if 'log' in self.__raw_config.sections():
            log_filename = \
                self.__raw_config['log'].get('dir', Configuration.LOG_DIR) \
                + self.__raw_config['log'].get('dir', Configuration.LOG_FILE)
            if path.isfilename(log_filename):
                return log_filename
        return Configuration.LOG_DIR

    @property
    def log_format(self):
        if 'log' in self.__raw_config.sections():
            log_format = self.__raw_config['log'].get('format', Configuration.LOG_FORMAT)
            return log_format
        return Configuration.LOG_FORMAT

    @property
    def log_datefmt(self):
        if 'log' in self.__raw_config.sections():
            log_datefmt = self.__raw_config['log'].get('datefmt', Configuration.LOG_DATEFMT)
            return log_datefmt
        return Configuration.LOG_DATEFMT

    @property
    def log_level(self):
        if 'log' in self.__raw_config.sections():
            log_level = self.__raw_config['log'].get('level', Configuration.LOG_LEVEL)
            return log_level
        return Configuration.LOG_LEVEL