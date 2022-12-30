# rpi-sensehat-mqtt

This a Python application for the [Raspberry Pi](https://www.raspberrypi.com) (RPi) that allows interfacing with the [SenseHAT](https://www.raspberrypi.com/documentation/accessories/sense-hat.html) over [MQTT](https://en.wikipedia.org/wiki/MQTT). Of note, the project is a fork of [mirkodcompataretti's rpi-sense-hat](https://github.com/mirkodcomparetti/rpi-sensehat_mqtt) that ended up being heavily modified to reflect my own idea of implementation.

# Table of Contents

1. [Install](#install)
1. [Usage](#usage)
1. [Run as a Service](#run-as-a-service)
1. [Log Rotation](#log-rotation)
1. [Emulator](#emulator)
1. [Related Docs](#related-docs)

## Install

This application can be installed in two non-exclusive ways. In the first and more typical scenario, you own a [SenseHAT module](https://www.raspberrypi.com/products/sense-hat/) and a compatible [RPi board](https://www.raspberrypi.com/products/) and want to use `rpi-sensehat-mqtt` to interface with the SenseHAT over MQTT. In the second and less typical case, you either do not own a RPi or the SenseHAT or both but you want to run a *virtual* SenseHAT on your Linux desktop environment and interface with it over MQTT. If your case is latter one, then take a look at the section [Emulator](#emulator); otherwise, keep on reading.

To install and use `rpi-sensehat-mqtt`, follow the procedures detailed next:

[top](#)

## Usage

- TBA

[top](#)

## Run as a Service

- TBA

[top](#)

## Log Rotation

- TBA

[top](#)

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


[top](#)

## Related Docs

- [RPi SenseHAT](https://www.raspberrypi.com/documentation/accessories/sense-hat.html)
- [SenseHAT Python API](https://pythonhosted.org/sense-hat/)
- [SenseHAT Emulator](https://github.com/astro-pi/python-sense-emu/)

[top](#)
