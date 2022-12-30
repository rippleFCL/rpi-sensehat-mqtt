"""
Module that contains helper functions to validade user variables
"""

# local imports
from src.constants import constants as const
# external imports
from os import path
from urllib.parse import ParseResult

# MQTT methods
def broker_url(broker_url:ParseResult):
    try:
        # https://docs.python.org/3/library/urllib.parse.html#urllib.parse.urlparse
        proto = broker_url.scheme
        host = broker_url.hostname
        port = broker_url.port
        return proto in const.MQTT_PROTOCOLS
    except ValueError:
        return False

# SENSEHAT methods
def pixels(pixels:list):
    return len(pixels) == 64

# CONFIGURATION methods
def file_exists(path_file:str):
    return path.isfile(path=path_file)

def zone(zone:str):
    return zone.find("/") == -1

def room(room:str):
    return zone(room)

def resolution(resolution:int):
    return resolution >= 0

def rounding(rounding:int):
    return rounding >= 0