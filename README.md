# rpi-sensehat-mqtt

## Introduction

The files here create a service on the _Raspberry Pi_ that works with the SenseHAT from the [astro-pi](https://astro-pi.org/) project and streams its data over MQTT.

This service works on all the Raspberry Pi flavors, as long as they support the SenseHAT.

## Oficial docs

- [RPi SenseHAT](https://www.raspberrypi.com/documentation/accessories/sense-hat.html)
- [SenseHAT Python Module](https://pythonhosted.org/sense-hat/)

## Folder structure

The files are here structured in this way:

* `rpi_sensehat_mqtt.py` python script to read the sensors and publish over MQTT
* `rpi_sensehat_mqtt.logrotate` configuration for [logrotate](https://manpages.debian.org/stretch/logrotate/logrotate.8.en.html) to rotate the log file of this script
* `rpi_sensehat_mqtt.env` file to define the environmental variables used while running the background service
* `rpi_sensehat_mqtt.service` file to run the background service
* `setconfiguration.sh` script to configure the system and properly propagate the files in the right folders

## How-to

The main python script `rpi_sensehat_mqtt.py` does the following operations when it runs:
* Reads sensor data
* Creates the MQTT message
* Publish it on the broker

The script logs its operations in the file `/var/log/rpi_broadcaster/rpi_sensehat_mqtt.log`.

The script requires a configuration through environmental variables defined in the `rpi_sensehat_mqtt.env` file.
The available configuration parameters are:
* `RPI_SENSEHAT_MQTT_LOGLEVEL="<desired loglevel>"` the desired log level to be used in the log, as defined by the [python library](https://docs.python.org/3/library/logging.html#levels)
* `RPI_SENSEHAT_MQTT_CYCLE=<desired timecycle>` the desired time cycle
* `RPI_SENSEHAT_MQTT_LOCATION="<desired location>"` to set the location in the message
* `RPI_SENSEHAT_MQTT_BROKER="protocol://address:port"` endpoint of the broker
* `RPI_SENSEHAT_MQTT_TOPIC_PREFIX="<desired prefix>"` to set the prefix for all the topics (default `sensehat`): `readings` is used for the readings and `commands` to process input commands
* `RPI_SENSEHAT_MQTT_MEASUREMENT="<desired measurement>"` measurement name
* `RPI_SENSEHAT_MQTT_WELCOME="<desired welcome message>"` welcome message at startup

## Deploy

In order to deploy the configuration, you need to do the following steps

1. On the target machine, clone this repository:
	```
	git clone https://github.com/cgomesu/rpi-sensehat-mqtt.git
	```

2. Run the following command:
	```
	cd rpi-sensehat-mqtt/
	sudo bash ./setconfiguration.sh
	```

3. After this has been successfully executed the new service is already running, and it can be managed using:
	```
	sudo systemctl <command> rpi_sensehat_mqtt.service
	```

