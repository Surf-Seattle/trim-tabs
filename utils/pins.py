import time
import RPi.GPIO as GPIO
from typing import List
import yaml
import os

from utils import CONFIG_DIR


class ControlSurfaces:
    path = os.path.join(CONFIG_DIR, 'control_surfaces.yml')

    def __init__(self):
        # ensure that the rasberry pi pins are ready to go
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        # create the pin attributes
        config = yaml.safe_load(open(self.path, 'r'))
        for configured_surface in config:
            setattr(
                self,
                configured_surface['name'],
                Surface(
                    name=configured_surface['name'],
                    extend_pin_number=configured_surface['pins']['extend'],
                    retract_pin_number=configured_surface['pins']['retract'],
                )
            )

        self.surfaces = [
            getattr(self, configured_surface['name'])
            for configured_surface in config
        ]

    def high(self, pin_numbers: List[str], duration: int = None) -> None:
        for surface in self.surfaces:
            for pin in surface.pins:
                if pin.number in pin_numbers:
                    pin.high()
        if duration:
            time.sleep(duration)
            self.low(pin_numbers)

    def low(self, pin_numbers: List[str]) -> None:
        for surface in self.surfaces:
            for pin in surface.pins:
                if pin.number in pin_numbers:
                    pin.low()


class Surface:

    def __init__(self, name, extend_pin_number: int, retract_pin_number: int) -> None:
        self.name = name
        self.extend_pin = Pin(extend_pin_number)
        self.retract_pin = Pin(retract_pin_number)
        self.pins = [self.extend_pin, self.retract_pin]
        self.position = None


class Pin:

    def __init__(self, pin_number: int) -> None:
        GPIO.setup([pin_number], GPIO.OUT)
        self.number = pin_number

    def high(self, duration: int = None) -> None:
        """Set a pin high."""
        GPIO.output(self.number, True)
        if duration:
            time.sleep(duration)
            self.low()

    def low(self) -> None:
        """Set a pin low."""
        GPIO.output(self.number, False)
