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
            # TODO: log connection
        else:
            # Connection error
            # TODO: log connection error with code {rc}
            pass

    def __on_disconnect(self, client, userdata, rc):
        if rc != 0:
            # MQTT disconnected
            self.is_connected = False
            # TODO: log disconnection

    def __on_publish(self, client, userdata, mid):
        self.published_mid = mid
        # TODO: log that the message of 'mid' was successfully sent to the broker

    def __on_log(client, userdata, level, buff):
        # TODO: log 'buff' to the logger to store exceptions catch by the client
        pass

    def publish(self, data:dict):
        """
        Publish data in dict format to the MQTT broker.
        """
        # TODO: validate data. for now, assume data follow excepted structure
        """
        data = {
            zone : {
                room : {
                    sensor : {
                        "time": int(round(time.time() * 1000)),
                        "pressure": round(self.sense.get_pressure(), 3),
                        "temperature": {
                            "01": round(self.sense.get_temperature(), 3),
                            "02": round(self.sense.get_temperature_from_pressure(), 3),
                        },
                        "humidity": round(self.sense.get_humidity(), 3),
                        "gyroscope": {
                            "pitch": '?',
                            "roll": '?',
                            "yaw": '?',
                        },
                        "compass":
                            "north": '?',
                        "acceleration": {
                            "x": round(self.sense.get_accelerometer_raw().get("x") * 9.80665, 3),
                            "y": round(self.sense.get_accelerometer_raw().get("y") * 9.80665, 3),
                            "z": round(self.sense.get_accelerometer_raw().get("z") * 9.80665, 3),
                        }
                    },
                },
            },
        }
        """
        json_data = json.dumps(data)
        self.__client.publish(topic=self._topic, payload=json_data, qos=0, retain=True)
        # TODO: log attempt to publish a message
    
    def disable(self):
        """
        Method that disables the client in this class object.
        To be used in exit, interrupts, and cleanup procedures.
        """
        # TODO: log call to disable this client
        # disconnect and stop object's client
        if self.is_initialized:
            self.__client.disconnect()
            self.__client.loop_stop()