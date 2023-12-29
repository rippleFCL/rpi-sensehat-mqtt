#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
This script contains the main logic of the rpi-sensehat-mqtt project.
Edit the 'CONFIG.ini' configuration file before running it. Refer to
the documentation to learn how to use the application using either
a physical SenseHAT or a virtual one.

Author: @cgomesu
Repo: https://github.com/cgomesu/rpi-sensehat-mqtt
"""

# local imports
import src.constants as const
import src.errors as err
import src.utils as utils
import src.mqtt as mqtt
import src.sensehat as sensehat
# external imports
import logging
from signal import signal, SIGINT, SIGHUP, SIGTERM, pause
import sys
import threading

# start a logging instance for this module using constants
logging.basicConfig(filename=const.LOG_FILENAME, format=const.LOG_FORMAT, datefmt=const.LOG_DATEFMT)
logger = logging.getLogger(__name__)
logger.setLevel(const.LOG_LEVEL)
logger.debug("Initilized a logger object.")

# methods for sense object threads
def streaming_sensor():
    logger.info("Starting sensor publishing loop.")
    while not stop_streaming.is_set():
        logger.debug("Updating and publishing sensor data.")
        mqtt_pub_sensor.publish(sense_sensor.sensors_data())
        logger.debug(f"Waiting for signal or timeout ({config.resolution}).")
        stop_streaming.wait(config.resolution)
        if not stop_streaming.is_set():
            logger.warning(f"Reached wait timeout.")

def streaming_led():
    logger.info("Starting LED message loop.")
    while not stop_streaming.is_set():
        if not mqtt_sub_led.messages.empty():
            logger.debug("Received a payload. Parsing it.")
            try:
                payload = mqtt_sub_led.decoded_message()
            except err.MqttDecodingError as mderr:
                logger.warning(f"Could not decode mqtt message. Skipping it. Error: {mderr.error}")
                continue
            logger.debug(f"Decoded payload: '{payload}'")
            if not isinstance(payload, dict):
                logger.warning(f"The payload is not a dictionary. Skipping it.")
                continue
            # payload should be in {'method' : [*args]} format
            for f in payload.keys():
                f_args = payload[f] if payload[f] else []
                try:
                    # https://pythonhosted.org/sense-hat/api/#led-matrix
                    # if a valid setter, call with kwargs; else, log and skip.
                    if f=='set_rotation': sense_led.sense.set_rotation(*f_args)
                    elif f=='flip_h': sense_led.sense.flip_h(f_args)
                    elif f=='flip_v': sense_led.sense.flip_v(f_args)
                    elif f=='set_pixels': sense_led.sense.set_pixels(*f_args)
                    elif f=='set_pixel': sense_led.sense.set_pixel(*f_args)
                    elif f=='load_image': sense_led.sense.load_image(*f_args)
                    elif f=='clear': sense_led.sense.clear(*f_args)
                    elif f=='show_message': sense_led.sense.show_message(*f_args)
                    elif f=='show_letter': sense_led.sense.show_letter(*f_args)
                    elif f=='wait': stop_streaming.wait(f_args)
                    else: logger.warning(f"The method '{f}' in the payload '{payload}' is not supported.")
                except TypeError as terr:
                    logger.info(f"Unable to call '{f}' with args '{f_args}': {terr}")
                except Exception as oerr:
                    # catch other exceptions that might propagate from SenseHat methods
                    logger.warning(f"There was a non-specific error running method '{f}': {oerr}")
        # wait a second before displaying any new messages from the mqtt topic
        stop_streaming.wait(2)

def streaming_joystick():
    logger.info("Starting joystick directions loop.")
    while not stop_streaming.is_set():
        logger.debug(f"Waiting for joystick directions.")
        # pass stop_streaming flag to prevent locks in wait_directions method
        sense_joystick.wait_directions(stop_streaming)
        if not sense_joystick.directions.empty():
            logger.debug(f"A joystick direction was detected. Publishing direction from queue.")
            mqtt_pub_joystick.publish(sense_joystick.joystick_data())

# methods of the main logic
def start(*signals):
    logger.info("Starting service.")
    # trap signals from args using stop function as handler
    for s in signals: signal(s, stop)
    # global lists of objects
    global senses, mqtts, threads
    senses = []
    mqtts = []
    threads = []
    # thread helpers
    global stop_streaming
    stop_streaming = threading.Event()

def stop(signum, frame=None):
    logger.info(f"Received a signal '{signum}' to stop.")
    # cleanup procedures
    stop_streaming.set()
    # disconnect and stop threads
    for m in mqtts:
        if m.is_enabled: m.disable()
    # turn off sensehat led and so on
    for s in senses:
        if s.is_enabled: s.disable()
    # exit the application
    sys.exit(signum)

def main():
    # startup procedure to trap INT, HUP, TERM signals
    start(SIGINT, SIGHUP, SIGTERM)
    # create a config object
    global config
    try:
        config = utils.Configuration()
    except err.InvalidConfigFile as cferr:
        logger.info(f"Unable to load settings because the config file does not exist: {cferr.path_file}.")
        stop(1)
    except err.ConfigParseError as cperr:
        logger.info(f"Unable to parse settings in the config file: {cperr.error}.")
        stop(1)
    except err.InvalidConfigAttr as caerr:
        logger.info(f"Check your config file. There's an invalid attribute: {caerr.attribute}.")
        stop(1)
    # create sensehat objects
    global sense_sensor, sense_led, sense_joystick
    sense_sensor = sensehat.SenseHatSensor(rounding=config.sensehat_rounding,
        acceleration_multiplier=config.sensehat_acceleration_multiplier,
        gyroscope_multiplier=config.sensehat_gyroscope_multiplier)
    sense_led = sensehat.SenseHatLed(set_rotation=config.sensehat_set_rotation,
        low_light=config.sensehat_low_light)
    sense_joystick = sensehat.SenseHatJoystick()
    senses.extend([sense_sensor, sense_led, sense_joystick])
    # create mqtt objects
    global mqtt_pub_sensor, mqtt_sub_led, mqtt_pub_joystick
    try:
        mqtt_pub_sensor = mqtt.MqttClientPub(broker_address=config.mqtt_broker_address,
            zone=config.mqtt_zone,
            room=config.mqtt_room,
            client_name=config.mqtt_client_name,
            type='sensor',
            client_id=f"{config.mqtt_client_name}_sensor",
            user=config.mqtt_user,
            password=config.mqtt_password)
        mqtt_sub_led = mqtt.MqttClientSub(broker_address=config.mqtt_broker_address,
            zone=config.mqtt_zone,
            room=config.mqtt_room,
            client_name=config.mqtt_client_name,
            type='led',
            client_id=f"{config.mqtt_client_name}_led",
            user=config.mqtt_user,
            password=config.mqtt_password)
        mqtt_pub_joystick = mqtt.MqttClientPub(broker_address=config.mqtt_broker_address,
            zone=config.mqtt_zone,
            room=config.mqtt_room,
            client_name=config.mqtt_client_name,
            type='joystick',
            client_id=f"{config.mqtt_client_name}_joystick",
            user=config.mqtt_user,
            password=config.mqtt_password)
        mqtts.extend([mqtt_pub_sensor, mqtt_sub_led, mqtt_pub_joystick])
    except err.InvalidMqttAttr as maerr:
        logger.info(f"Check your config becayse the following MQTT attribute is invalid: '{maerr.attribute}'")
        stop(1)
    # thread handlers
    thread_sensor = threading.Thread(target=streaming_sensor)
    thread_led = threading.Thread(target=streaming_led)
    thread_joystick = threading.Thread(target=streaming_joystick)
    threads.extend([thread_sensor, thread_led, thread_joystick])
    # finished setting up, then print welcome message if set (this blocking)
    if config.welcome_msg: sense_led.sense.show_message(config.welcome_msg)
    # start threads and wait for interrupt signal in this one
    logger.debug(f"Starting threads '{threads}'.")
    for t in threads: t.start()
    logger.info(f"Main thread is done. Waiting for interrupt.")
    pause()

if __name__ == "__main__":
    main()
