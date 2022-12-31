# rpi-sensehat-mqtt

This a Python application for the [Raspberry Pi](https://www.raspberrypi.com) (RPi) that allows interfacing with the [SenseHAT](https://www.raspberrypi.com/products/sense-hat/) over [MQTT](https://en.wikipedia.org/wiki/MQTT). 

<p align="center">
    <img src="assets/rpi_sensehat.png" width="60%">
</p>

Of note, the project is a fork of [mirkodcompataretti's rpi-sense-hat](https://github.com/mirkodcomparetti/rpi-sensehat_mqtt) that ended up being heavily modified to reflect my own idea of implementation, which can be illustrated as follows:

<p align="center">
    <img src="assets/concept.png" width="50%">
</p>

That is, the `rpi-sensehat-mqtt` application publishes **sensor** and **joystick** data to the MQTT broker to be consumed by a home automation server (e.g., [Home Assistant](https://www.home-assistant.io/)). In addition, it also subcribes to an **LED** topic to display payloads published to the broker. For instance, when an homr automation publishes a message to the LED topic, the SenseHAT will consume it and display it on the LED matrix.

## Table of Contents

1. [Install](#install)
1. [Usage](#usage)
1. [Run as a Service](#run-as-a-service)
1. [Log Rotation](#log-rotation)
1. [Emulator](#emulator)
1. [Related Docs](#related-docs)

## Install

This application can be installed in two non-exclusive ways. In the first and more typical scenario, you own a [SenseHAT module](https://www.raspberrypi.com/products/sense-hat/) and a compatible [RPi board](https://www.raspberrypi.com/products/) and want to use `rpi-sensehat-mqtt` to interface with the SenseHAT over MQTT. In the second and less typical case, you either do not own a RPi or the SenseHAT or both but you want to run a *virtual* SenseHAT on your Linux desktop environment and interface with it over MQTT. If your case is latter one, then take a look at the section [Emulator](#emulator); otherwise, keep on reading.

For the installation procedure, it is assumed that your Raspberry Pi is running the latest version of the [Raspberry Pi OS](https://www.raspberrypi.com/software/) but the instructions might be compatible with similar distributions for the RPi. To install and use `rpi-sensehat-mqtt`, follow the procedures detailed next:

1. If you have not attached the SenseHAT to the RPi yet, go ahead and turn off your RPi and attach the SenseHAT to it. Then, log into the CLI of your RPi using your standard user (e.g., `pi`) or if running a desktop environment, open a terminal.

1. Run the commands below to install the `sense-hat` package and other packages we will need. Make sure that `I2C` was enabled afterwards; Otherwise, run `sudo raspi-config` and manually turn it on in the `Interfaces` section of the utility.  You will need to reboot your RPi for the changes to take effect.

    ```sh
    sudo apt update
    sudo apt install sense-hat git python3 python3-pip
    # reboot for the changes to take effect
    sudo reboot now
    ```

1. Test the `sense-hat` installation by running one or more of the Python demos at `/usr/src/sense-hat/examples/python-sense-hat` (press `ctrl+c` to stop):

    ```sh
    ./usr/src/sense-hat/examples/python-sense-hat/rainbow.py
    ```

1. (Optional.) [Callibrate the magnetometer](https://www.raspberrypi.com/documentation/accessories/sense-hat.html#calibration). This will install *many* additional packages and will take some time to complete.

1. Go to your user's home directory and clone this repository:

    ```sh
    cd ~
    git clone https://github.com/cgomesu/rpi-sensehat-mqtt.git
    cd rpi-sensehat-mqtt/
    ```

1. Update Python's package manager (`pip`) and install the required packages from `requirements.txt`:

    ```sh
    pip3 install --upgrade pip
    pip3 install -r requirements.txt
    ```

    You might notice that this will install the additional packages in your user's `~/.local/bin` directory, so they will not be available globally, which is good. The drawback is that `~/.local/bin` is not part of the default `$PATH`, which is where your OS will look for executables. To fix this in the current session, run the following:

    ```sh
    export PATH="$PATH:$HOME/.local/bin"
    ```

    To make `~/.local/bin` reachable to your user permanently, you need to append `export PATH="$PATH:$HOME/.local/bin"` to your `~/.bashrc` or `~/.profile`.

1. Finally, edit the `CONFIG.ini` file to match your preferences. This is were most of the configuration options are stored for users to edit.

    ```sh
    cd ~/rpi-sensehat-mqtt/
    nano CONFIG.ini
    ```

1. If everything is looking good, you can try running the main script.  However, it won't output meaningful on the terminal. All messages are logged into `logs/rpi_sensehat_mqtt.log`. So, open another terminal and make it follow new messages added to the log file:

    ```sh
    tail -f ~/rpi-sensehat-mqtt/logs/rpi_sensehat_mqtt.log
    ```

    Then, go back to the previous terminal and run the main script:

    ```sh
    ./rpi_sensehat_mqtt.py
    ```

    As mentioned, you should not notice anything on the terminal if the application is running as intended. However, your SenseHAT should disaply the `welcome_message` once it has initialized.  If the application closes without you sending an interrupt signal (e.g., `ctrl+c`), there's likely a configuration issue.  Check the log messages to learn about what the script is doing and any error messages.  By default, it will only store `INFO` level messages.  If you need a more verbose log, edit `LOG_LEVEL` to `'DEBUG'` instead.

1. Once you got the application running successfully, take a look at [Run as a Service](#run-as-a-service) and [Log Rotation](#log-rotation) to make it run automatically in the background and have your OS manage the log file.

You should be all set at this point. So, head to [Usage](#usage) to learn the specifics about how to interface with the SenseHAT via MQTT.

[top](#table-of-contents)

## Usage

The main logic is in the `rpi_sensehat_mqtt.py` script and most of the configurable variables (e.g., MQTT address and credentials, sensor publish resolution) are in the `CONFIG.ini` [INI](https://en.wikipedia.org/wiki/INI_file) file.  **You must edit the latter before running the former**.  (Advanced usage variables can be found in `src/constants/constants.py` and as constants in individual modules. Do not change them unless you know what you are doing.)

The main script can be executed in two ways, namely by using the shebang or calling `python3` directly:

```sh
./rpi_sensehat_mqtt.py
```

```sh
python3 rpi_sensehat_mqtt.py
```

To run the script in the background, refer to the [Run as a Service](#run-as-a-service) section.

### MQTT

The main purpose of this application is to interface with the SenseHAT via [MQTT](https://en.wikipedia.org/wiki/MQTT). By default, it will publish/subscribe to the following topic level structure:

```mqtt
zone/room/client_name
```

in which `zone`, `room`, and `client_name` can be configured in `CONFIG.ini`. For example, if the `CONFIG.ini` contains

```ini
zone = downstairs
room = livingroom
client_name = sensehat01
```

then the application will publish/subscribe to the following topic:

```mqtt
downstairs/livingroom/sensehat01
```

As outlined before, the application creates three independent connections with the MQTT broker, namely (a) one to publish sensor data, (b) one to publish joystick directions, and (c) one to subscribe to a LED matrix sub-topic. In all three cases, payloads must be in [JSON](https://en.wikipedia.org/wiki/JSON#Syntax) (or be a `dict` or key:value pairs) data format.  The specifics of each are explained next.

- The payload of the **sensor** connection is published to the following subtopic `sensor/status`, as follows:

    ```mqtt
    downstairs/livingroom/sensehat01/sensor/status
    ```

    and has the following structure:

    ```json
    {
        "time" : "time_value",
        "pressure" : "pressure_value",
        "temperature" : {
            "from_humidty" : "temp_value",
            "from_pressure" : "temp_value"
        },
        "humidity" : "humidity_value",
        "gyroscope" : {
            "pytch" : "pytch_value",
            "roll" : "roll_value",
            "yaw" : "yaw_value"
        },
        "compass" : {
            "north" : "north_value"
        },
        "acceleration" : {
            "x" : "x_value",
            "y" : "y_value",
            "z" : "z_value"
        },
    }

    ```

- The payload of the **joystick** connection is published to the following subtopic `joystick/status`, as follows:

    ```mqtt
    downstairs/livingroom/sensehat01/joystick/status
    ```

    and has the following structure:

    ```json
    {
        "direction" : "direction"
    }
    ```

- Finally, the **LED** connection subscribes to the following subtopic `led/cmd`, as follows:

    ```mqtt
    downstairs/livingroom/sensehat01/led/cmd
    ```

    and it consumes payloads with the following structure:

    ```json
    {
        "led_method" : {
            "arg1" : "value1",
            "arg2" : "value2",
            "argN" : "valueN",
        }
    }
    ```

    in which `led_method` is the name of a valid [LED matrix setter method of a SenseHat object](https://pythonhosted.org/sense-hat/api/#led-matrix) (e.g., `"show_message"`); the various `"arg"` keys are the name of valid arguments (`text_string`, `text_colour`); and `value` is the value that each argument should be set to (`"Hello!"`, `[255,0,0]`).  This is organized in such a way because the logic will check whether the `led_method` is valid and then pass its value as `**kwargs` to the method.

    Of note, the payload can contain more than one method as well:

    ```json
    {
        "led_method1" : {
            "arg1" : "value1",
        },
        "led_method2" : {
            "arg1" : "value1",
            "arg2" : "value2"
        }
    }
    ```

    Here is an example of payload consumed by the LED client and what it displays on the LED matrix as a result:

    ```json
    {
        "load_image" : {
            "file_path" : "/home/pi/rpi-sensehat-mqtt/assets/battery/battery-75.png",
        }
    }
    ```
    <p align="center"><img src="assets/sensehat_load_image.png" width="50%"></p>

[top](#table-of-contents)

## Run as a Service

To run `rpi_sensehat_mqtt.py` in the background, you can make use of the systemd unit file in the `systemd/` dir. To enable and start it, follow these instructions:

1. (Optional.) Edit the unit file to your liking and **double check the paths** to ensure they are pointing to the right ones--namely, check the paths in `ExecStart`.

    ```sh
    cd ~/rpi-sensehat-mqtt/systemd/
    nano rpi_sensehat_mqtt.service
    ```

1. Enable the unit file and start it (requires `root` permission):

    ```sh
    sudo systemctl enable "$HOME"/rpi-sensehat-mqtt/systemd/rpi_sensehat_mqtt.service
    sudo systemctl start rpi_sensehat_mqtt.service
    ```

1. You may check its status afterwards:

    ```sh
    systemctl status rpi_sensehat_mqtt.service
    ```

    And remember to take a look at its logs if the service is not running correctly.

If the service is up and running, you are all set here.

[top](#table-of-contents)

## Log Rotation

The `rpi_sensehat_mqtt.py` script stores log messages in the `logs/rpi_sensehat_mqtt.log` file and if unchcked, such a file will grow forever. You can always manually remove old entries but this is best done by making use of your OS log rotation utility, namely [`logrotate`](https://linux.die.net/man/8/logrotate). To do so, follow the steps next:

1. (Optional.) Edit the preconfigured logrotate file to your liking. Of note, if you're not following the guide here and placed the log files elsewhere, make sure to point to their correct location in the logrotate file.

    ```sh
    cd ~/rpi-sensehat-mqtt/logrotate.d/
    nano rpi_sensehat_mqtt
    ```

1. Copy the logrotate file to the directory monitored by `logrotate` (this requires `root` permission):

    ```sh
    sudo cp ./rpi_sensehat_mqtt /etc/logrotate.d/
    ```

That is it. The log file should be rotated automatically during the next logrotate run--this is usually done automatically by your OS.

[top](#table-of-contents)

## Emulator

If you do not own a RPi or a SenseHAT or both, you can emulate the SenseHAT on pretty much any system via the [SenseHAT Emulator](https://github.com/astro-pi/python-sense-emu/). This is particularly useful for development but you can also use your virtual SenseHAT to send (and to receive) messages from the MQTT broker just as if you had a physical SenseHAT. Check the [`sense-emu` installation instructions](https://sense-emu.readthedocs.io/en/v1.1/install.html?highlight=cairo#alternate-platforms) and give it a try.

In `apt` based distros (e.g., Debian, Ubuntu, Rasbperry Pi OS), this can be done via terminal as follows:

- Install prerequisites:

    ```sh
    sudo apt install python3 python3-pip python3-gi python3-gi-cairo
    ```

- Install `sense-emu` via `pip3` for the current user:

    ```sh
    pip3 install --upgrade pip
    pip3 install sense-emu
    ```

- Ensure that `$HOME/.local/bin` is reachable in your user's `$PATH`:

    ```sh
    export PATH="$PATH:$HOME/.local/bin"
    ```

- (Optional.) The command above will only make your user's `.local/bin` dir reachable for the duration of the current session. To permanently add it to your `$PATH`, append the command to your `~/.bashrc` or `~/.profile`.

- Lunch the SenseHAT GUI:

    ```sh
    sense_emu_gui &
    ```

- Now in your `rpi-sensehat-mqtt` dir, set (edit and save) `SENSEHAT_EMULATION` in `src/constants/constants.py` as follows:

    ```Python
    SENSEHAT_EMULATION = True
    ```

You are done. Now just run `rpi-sensehat-mqtt.py` as described in [Usage](#usage) and interface with the SenseHAT via the GUI (`sense_emu_gui`).

[top](#table-of-contents)

## Related Docs

- [RPi SenseHAT](https://www.raspberrypi.com/documentation/accessories/sense-hat.html)
- [SenseHAT Python API](https://pythonhosted.org/sense-hat/)
- [SenseHAT Emulator](https://github.com/astro-pi/python-sense-emu/)

[top](#table-of-contents)
