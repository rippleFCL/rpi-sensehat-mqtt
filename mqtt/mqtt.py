"""
Module that contains application-specific MQTT functions.
This module is meant to be use in conjunction with the paho-mqtt package.
"""

from paho.mqtt import client as mqttc
# from paho.mqtt import subscribe as mqtts
from urllib.parse import urlparse
import json

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
                broker_address,
                client_name,
                channel,
                zone,
                room,
                sensor,
                user=None,
                password=None):
        # TODO: Handle exceptions from urlparse()
        self.broker_url = urlparse(broker_address)
        self.client_name = client_name
        self.channel = channel
        self.zone = zone
        self.room = room
        self.sensor = sensor
        self.user = user
        self.password = password
        # observe scope from this point on
        self.__client = None
        # class object helpers
        self._is_initialized = False
        self._is_connected = False
        self._published_mid = None
        # initialize connection
        self.__connect()
        # connection has been initialized
        self._is_initialized = True
        # TODO: log mqtt client object initialized

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
            self._is_connected = True
            # TODO: log connection
        else:
            # Connection error
            # TODO: log connection error with code {rc}
            pass

    def __on_disconnect(self, client, userdata, rc):
        if rc != 0:
            # MQTT disconnected
            self._is_connected = False
            # TODO: log disconnection

    def __on_publish(self, client, userdata, mid):
        self._published_mid = mid
        # TODO: log that the message of 'mid' was successfully sent to the broker

    def publish(self, data:dict):
        """
        Publish data in dict format to the MQTT broker.
        """
        # TODO: validate data
        """
        raw_mqtt_data = {
            zone : {
                room : {
                    sensor : {
                        "temperature" : temperature,
                        "humidity" : humidity,
                        "pressure" : pressure
                    },
                },
            },
        }
        """
        pass