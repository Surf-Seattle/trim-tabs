import time
import RPi.GPIO as GPIO
from typing import List
import yaml
import os

from .utilities import get_actuators


def set_as_output(pins: List[int]) -> None:
    """Configure the a list of pins as an output."""
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pins, GPIO.OUT)


def init() -> None:
    """Set the configured pins as output."""
    print(" PINS ".center(30, "-"))
    for actuator_name, actuator_config in get_actuators().items():
        set_as_output([actuator_config[x] for x in ["extend", "retract"]])
        set_as_output([actuator_config[x] for x in ["extend", "retract"]])
    print(f"({actuator_config['extend']}) {actuator_name}.extract")
    print(f"({actuator_config['retract']}) {actuator_name}.retract")
    print("-" * 30)


def high(pin: int, duration: int = None) -> None:
    """Set a pin high."""
    GPIO.output(pin, True)
    if duration:
        time.sleep(duration)
        low(pin)


def low(pin: int, duration: int = None) -> None:
    """Set a pin low."""
    GPIO.output(pin, False)
    if duration:
        time.sleep(duration)
        high(pin)
