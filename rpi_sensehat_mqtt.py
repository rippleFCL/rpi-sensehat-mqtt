#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
This scripts reads sensors from the SenseHAT and publishes them on an MQTT broker.
Author: @cgomesu
Repo: https://github.com/cgomesu/rpi-sensehat-mqtt
"""

# local imports
import src.constants as const
# import src.errors as errors
import src.utils as utils
import src.mqtt as mqtt
import src.sensehat as sensehat
# external imports
import logging
from signal import signal, SIGINT, SIGHUP, SIGTERM
import sys
from threading import Event

# start a loggin instance for this module using constants
logging.basicConfig(filename=const.LOG_FILENAME, format=const.LOG_FORMAT, datefmt=const.LOG_DATEFMT)
logger = logging.getLogger(__name__)
logger.setLevel(const.LOG_LEVEL)
logger.debug("Initilized a logger object.")

# initialize global objects
mqttc = None
mqtts = None
shat_sensors = None
shat_led = None
shat_joystick = None
stop_streaming = Event()
data = None

def start(*signals)->None:
    logger.info("Starting service.")
    # trap signals from args using stop function as handler
    for s in signals: signal(s, stop)

def stop(signum, frame=None)->None:
    logger.info(f"Received a signal '{signum}' to stop.")
    # cleanup procedures
    stop_streaming.set()
    # disconnect and stop threads
    if mqttc: mqttc.disable()
    if mqtts: mqtts.disable()
    # turn off sensehat led and so on
    if shat_sensors: shat_sensors.disable()
    if shat_led: shat_led.disable()
    if shat_joystick: shat_joystick.disable()
    # exit the application
    sys.exit(signum)

def main()->None:
    # startup procedure passing INT, HUP, TERM signals
    start(SIGINT, SIGHUP, SIGTERM)
    # TODO: catch exceptions in object initialization and loop logic
    # create a config object
    config = utils.Configuration()
    # create mqtt client and sensehat objects
    shat_sensors = sensehat.SenseHatSensor(low_light=config.sensehat_low_light,
                                            rounding=config.sensehat_rounding,
                                            acceleration_multiplier=config.sensehat_acceleration_multiplier,
                                            gyroscope_multiplier=config.sensehat_gyroscope_multiplier)
    mqttc = mqtt.MqttClientPub(broker_address=config.mqtt_broker_address,
                                zone=config.mqtt_zone,
                                room=config.mqtt_room,
                                client_id=config.mqtt_client_id,
                                type='sensor',
                                user=config.mqtt_user,
                                password=config.mqtt_password)
    # main loop logic for sensor testing
    logger.info("Starting main sensor publishing loop.")
    while not stop_streaming.is_set():
        logger.debug("Updating and publishing sensor data.")
        mqttc.publish(shat_sensors.sensors_data(), 'status')
        logger.debug(f"Waiting for signal or timeout ({config.resolution}).")
        stop_streaming.wait(config.resolution)
        if not stop_streaming.is_set():
            logger.debug(f"Reached wait timeout.")
    # if it escapes loop, stop the application with code 0
    logger.debug("Stop streaming event was set to True.")
    stop(0)


if __name__ == "__main__":
    main()
