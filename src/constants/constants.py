"""
Module that stores constant variables to be used by multiple packages/modules in the application
or that should be edited for development or advanced usage. For module specific constants, it's
preferable set them in module itself and refer to it instead.
"""

# LOGGING
# directory in which the log files will be stored
LOG_DIR = 'logs/'
# name of the file where the log msgs are stored
LOG_FILE = 'rpi_sensehat_mqtt.log'
LOG_FILENAME = LOG_DIR+LOG_FILE
# see 'https://docs.python.org/3/howto/logging.html' for details
LOG_FORMAT = '%(asctime)s.%(msecs)03d [%(levelname)s] [%(name)s] %(message)s'
LOG_DATEFMT = '%Y-%m-%dT%H:%M:%S'
LOG_LEVEL = 'INFO'

# SENSEHAT
# set to True to use sense_emu instead of sense_hat for SenseHat objects,
# then use the graphical app 'sense_emu_gui' to interface with the virtual SenseHAT 
SENSEHAT_EMULATION = False

# MQTT
# TODO: after adding support for TLS, add 'mqtts' and 'wss' here
# list of supported protocols/schema
MQTT_PROTOCOLS = ['mqtt', 'ws', 'tcp']
