"""
Module that contains custom errors for the senseHAT application
"""

class SenseHatException(Exception):
    def __init__(self, message:str):
        self._message = message
    @property
    def message(self):
        return self._message

# subclasses here, as needed:
class InvalidAttribute(SenseHatException):
    def __init__(self, message: str, attribute:str):
        super().__init__(message)
        self._attribute = attribute
    @property
    def attribute(self):
        return self._attribute

class MethodError(SenseHatException):
    def __init__(self, message: str, error:str):
        super().__init__(message)
        self._error = error
    @property
    def error(self):
        return self._error

# MQTT errors
class InvalidMqttAttr(InvalidAttribute):
    def __init__(self, message: str, attribute: str):
        super().__init__(message, attribute)

class MqttDecodingError(MethodError):
    def __init__(self, message: str, error: str):
        super().__init__(message, error)

# SENSEHAT errors
class InvalidSenseAttr(InvalidAttribute):
    def __init__(self, message: str, attribute: str):
        super().__init__(message, attribute)

# CONFIGURATION errors
class InvalidConfigAttr(InvalidAttribute):
    def __init__(self, message: str, attribute: str):
        super().__init__(message, attribute)

class InvalidConfigFile(SenseHatException):
    def __init__(self, message:str, path_file:str):
        super().__init__(message)
        self._path_file = path_file
    @property
    def path_file(self):
        return self._path_file

class ConfigParseError(MethodError):
    def __init__(self, message: str, error: str):
        super().__init__(message, error)