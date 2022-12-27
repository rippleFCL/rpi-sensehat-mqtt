"""
Module that contains custom errors for the senseHAT application
"""

class SenseHatException(Exception):
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return f"{self.message}"
    @property
    def message(self):
        return self.message

# subclasses here, as needed:
