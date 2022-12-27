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
    
    # fallbacks for configuration variables
    # DEFAULT
    RESOLUTION = 300
    # MQTT
    MQTT_CLIENT_ID = 'sensehat_rnd'
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
    # SENSEHAT
    SENSEHAT_LOW_LIGHT = True
    SENSEHAT_ROUNDING = 4
    SENSEHAT_ACCELERATION_MULTIPLIER = 9.80665
    SENSEHAT_GYROSCOPE_MULTIPLIER = 1.0

    def __init__(self, config_dir = './', config_file = 'CONFIG.ini'):
        if not path.isfile(config_dir + config_file):
            # TODO: log error here
            raise OSError(filename=self.config_full_path_file)
        self.config_full_path_file = config_dir + config_file
        # init raw config with None and then set keys and values from INI file via load method
        self.__raw_config = None
        self.__load_raw_config()
        # init config attributes with class defaults and then set valus from raw config via load method
        self.__resolution = Configuration.RESOLUTION
        self.__welcome_msg = None
        self.__mqtt_broker_address = Configuration.MQTT_BROKER_ADDRESS
        self.__mqtt_client_id = Configuration.MQTT_CL+str(randint(0,99))
        self.__mqtt_user = None
        self.__mqtt_password = None
        self.__mqtt_credentials_enabled = False
        self.__mqtt_channel = Configuration.MQTT_CHANNEL
        self.__mqtt_zone = Configuration.MQTT_ZONE
        self.__mqtt_room = Configuration.MQTT_ROOM
        self.__mqtt_sensor = Configuration.MQTT_SENSOR
        self.__log_filename = Configuration.LOG_DIR+Configuration.LOG_FILE
        self.__log_format = Configuration.LOG_FORMAT
        self.__log_datefmt = Configuration.LOG_DATEFMT
        self.__log_level = Configuration.LOG_LEVEL
        self.__sensehat_low_light = Configuration.SENSEHAT_LOW_LIGHT
        self.__sensehat_rounding = Configuration.SENSEHAT_ROUNDING
        self.__sensehat_acceleration_multiplier = Configuration.SENSEHAT_ACCELERATION_MULTIPLIER
        self.__sensehat_gyroscope_multiplier = Configuration.SENSEHAT_GYROSCOPE_MULTIPLIER
        self.__load_config_attributes()
        # TODO: log config object fully initialized

    def __load_raw_config(self):
        config_parser = ConfigParser()
        try:
            config_parser.read(self.configPath)
            self.__raw_config = config_parser
        except Error as err:
            # TODO: log err here
            # TODO: raise a custom error for main app to catch passing err
            pass

    def __load_config_attributes(self):
        # DEFAULT
        # resolution
        if 'resolution' in self.__raw_config['DEFAULT']:
            resolution = self.__raw_config['DEFAULT'].getint('resolution', Configuration.RESOLUTION)
            if resolution > 0:
                self.__resolution = resolution
        # welcome_msg
        if 'welcome_msg' in self.__raw_config['DEFAULT']:
            self.__welcome_msg = self.__raw_config['DEFAULT'].get('welcome_msg', None)
        # MQTT
        # mqtt_client_id
        if 'mqtt' in self.__raw_config.sections():
            self.__mqtt_client_id = self.__raw_config['mqtt'].get('client_id', Configuration.MQTT_CLIENT_ID)
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
        # mqtt_channel
        if 'mqtt' in self.__raw_config.sections():
            self.__mqtt_channel = self.__raw_config['mqtt'].get('channel', Configuration.MQTT_CHANNEL)
        # mqtt_zone
        if 'mqtt' in self.__raw_config.sections():
            self.__mqtt_zone = self.__raw_config['mqtt'].get('zone', Configuration.MQTT_ZONE)
        # mqtt_room
        if 'mqtt' in self.__raw_config.sections():
            self.__mqtt_room = self.__raw_config['mqtt'].get('room', Configuration.MQTT_ROOM)
        # mqtt_sensor
        if 'mqtt' in self.__raw_config.sections():
            self.__mqtt_sensor = self.__raw_config['mqtt'].get('sensor', Configuration.MQTT_SENSOR)
        # log_filename
        if 'log' in self.__raw_config.sections():
            log_filename = \
                self.__raw_config['log'].get('dir', Configuration.LOG_DIR) \
                + self.__raw_config['log'].get('dir', Configuration.LOG_FILE)
            self.__log_filename = log_filename if path.isfilename(log_filename) else \
                Configuration.LOG_DIR+Configuration.LOG_FILE
        # log_format
        if 'log' in self.__raw_config.sections():
            self.__log_format = self.__raw_config['log'].get('format', Configuration.LOG_FORMAT)
        # log_datefmt
        if 'log' in self.__raw_config.sections():
            self.__log_datefmt = self.__raw_config['log'].get('datefmt', Configuration.LOG_DATEFMT)
        # log_level
        if 'log' in self.__raw_config.sections():
            self.__log_level = self.__raw_config['log'].get('level', Configuration.LOG_LEVEL)
        # SENSEHAT
        # sensehat_low_light
        if 'sensehat' in self.__raw_config.sections():
            self.__sensehat_low_light = self.__raw_config['sensehat'].getboolean('low_lebel', Configuration.LOG_LEVEL)
        # sensehat_rounding
        if 'sensehat' in self.__raw_config.sections():
            self.__sensehat_rounding = self.__raw_config['sensehat'].getint('sensehat_rounding', Configuration.SENSEHAT_ROUNDING)
        # sensehat_acceleration_multiplier
        if 'sensehat' in self.__raw_config.sections():
            self.__sensehat_acceleration_multiplier= self.__raw_config['sensehat'].getfloat('sensehat_acceleration_multiplier',
                Configuration.SENSEHAT_ACCELERATION_MULTIPLIER)
        # sensehat_gyroscope_multiplier
        if 'sensehat' in self.__raw_config.sections():
            self.__sensehat_gyroscope_multiplier = self.__raw_config['sensehat'].getfloat('sensehat_gyroscope_multiplier',
                Configuration.SENSEHAT_GYROSCOPE_MULTIPLIER)

    # TODO: Validation could happen in setter logic
    @property
    def resolution(self):
        return self.__resolution
    
    @property
    def welcome_msg(self):
        return self.__welcome_msg
    
    @property
    def mqtt_client_id(self):
        return self.__mqtt_client_id

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
    def mqtt_channel(self):
        return self.__mqtt_channel

    @property
    def mqtt_zone(self):
        return self.__mqtt_zone

    @property
    def mqtt_room(self):
        return self.__mqtt_room

    @property
    def mqtt_sensor(self):
        return self.__mqtt_sensor

    @property
    def log_filename(self):
        return self.__log_filename

    @property
    def log_format(self):
        return self.__log_format

    @property
    def log_datefmt(self):
        return self.__log_datefmt

    @property
    def log_level(self):
        return self.__log_level
    
    @property
    def sensehat_low_light(self):
        return self.__sensehat_low_light
    
    @property
    def sensehat_rounding(self):
        return self.__sensehat_rounding

    @property
    def sensehat_acceleration_multiplier(self):
        return self.__sensehat_acceleration_multiplier

    @property
    def sensehat_gyroscope_multiplier(self):
        return self.__sensehat_gyroscope_multiplier
