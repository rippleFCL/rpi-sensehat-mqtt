"""
Module that contains application-specific MQTT functions.
This module is meant to be use in conjunction with the paho-mqtt package.
"""
# local imports
from src.constants import constants as const
# external imports
import logging
from paho.mqtt import client as mqttc
# from paho.mqtt import subscribe as mqtts
from urllib.parse import urlparse
import json

# start a loggin instance for this module using constants
logging.basicConfig(filename=const.LOG_FILENAME, format=const.LOG_FORMAT, datefmt=const.LOG_DATEFMT)
logger = logging.getLogger(__name__)
logger.setLevel(const.LOG_LEVEL)
logger.debug("Initilized a logger object.")

class MqttSubscribe():
    """
    Class that generates an MQTT sub
    """
    pass

class MqttClient():
    """
    Class that generates an MQTT client.
    Doc: https://www.eclipse.org/paho/index.php?page=clients/python/docs/index.php
    """
    def __init__(self,
                broker_address:str,
                client_name:str,
                channel:str,
                zone:str,
                room:str,
                sensor:str,
                user:str = None,
                password:str = None):
        # TODO: Handle exceptions from urlparse()
        self.broker_url = urlparse(broker_address)
        self.client_name = client_name
        self.channel = channel
        self.zone = zone
        self.room = room
        self.sensor = sensor
        self.user = user
        self.password = password
        # don't make the client public
        self.__client = None
        # class object helpers
        self.is_initialized = False
        self.is_connected = False
        self.published_mid = None
        # initialize connection
        self.__connect()
        # MQTT client object has been fully initialized
        self.topic = str(self.zone)+'/'+str(self.room)+'/'+str(self.sensor)
        self.is_initialized = True
        logger.info(f"An MQTT cliente for the broker '{self.broker_url}' was initialized.")

    def __connect(self):
        # protocol conditional
        if self.broker_url.scheme == 'ws':
            self.__client = mqttc.Client(client_id=self.client_name, transport='websockets')
        else:
            self.__client = mqttc.Client(client_id=self.client_name)
        # custom mqtt functions references
        self.__client.on_connect = self.__on_connect
        self.__client.on_disconnect = self.__on_disconnect
        self.__client.on_publish = self.__on_publish
        self.__client.on_log = self.__on_log
        # TODO: TLS support
        # credentials handling
        if self.user:
            self.__client.username_pw_set(username=self.user, password=self.password)
        # connect to the brok in a non-blocking way
        self.__client.connect_async(host=self.broker_url.hostname, port=self.broker_url.port)
        self.__client.loop_start()

    def __on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            # MQTT connected
            self.is_connected = True
            logger.info(f"The client '{client}' connected successfully to '{self.broker_url}'.")
        else:
            # Connection error
            logger.info(f"The client '{client}' got an error ({rc}) trying to connect to '{self.broker_url}'.")

    def __on_disconnect(self, client, userdata, rc):
        if rc != 0:
            # MQTT disconnected
            self.is_connected = False
            logger.info(f"The client '{client}' was disconnected from '{self.broker_url}'.")

    def __on_publish(self, client, userdata, mid):
        self.published_mid = mid
        logger.info(f"The message of ID '{mid}' was successfully sent to '{self.broker_url}'.")

    def __on_log(client, userdata, level, buff):
        # TODO: set level according to level arg because this might be too verbose
        logger.info(f"[paho-mqtt] {buff}")

    def publish(self, data:dict):
        """
        Publish data in dict format to the MQTT broker.
        """
        # TODO: validate data
        json_data = json.dumps(data)
        self.__client.publish(topic=self.topic, payload=json_data, qos=0, retain=True)
        logger.info(f"A publish request to topic '{self.topic}' was made.")
    
    def disable(self):
        """
        Method that disables the client in this class object.
        To be used in exit, interrupts, and cleanup procedures.
        """
        logger.info(f"Received a call to disable the client '{self.client_name}'.")
        # disconnect and stop object's client
        if self.is_initialized:
            self.__client.disconnect()
            self.__client.loop_stop()