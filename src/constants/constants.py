"""
Module that stores constant variables to be used by MULTIPLE packages/modules in the application.
These are usually arguments for external packages that are imported by multiple modules.

For module specific constants (e.g., class defaults), set and refer to the module itself.
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
