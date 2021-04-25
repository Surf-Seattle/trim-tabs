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

        self.surfaces = {
            configured_surface['name']: getattr(self, configured_surface['name'])
            for configured_surface in config
        }

    def extend(self, *args, **kwargs) -> None:
        if isinstance(args[0], list):
            self.extend_uniform(*args, **kwargs)
        elif isinstance(args[0], dict):
            self.extend_jagged(*args, **kwargs)

    def extend_uniform(self, surface_names: List[str], duration: int = None) -> None:
        """Extend one or more control surfaces the same amount."""

        for name, surface in self.surfaces.items():
            if name in surface_names:
                surface.extend_pin.high()
        if duration:
            time.sleep(duration)
            for name, surface in self.surfaces.items():
                if name in surface_names:
                    surface.extend_pin.low()

# A: 10, B: 5, C: 1

# set A, B, C high
# sleep for 1 second
# set C low
# sleep for 4 seconds
# set B low
# sleep for 5 seconds
# set A low

    def extend_jagged(self, surface_transform: dict) -> None:
        """Extend one or more control surfaces for by different amounts."""
        transform_durations = grouped_runtimes(surface_transform)
        for surface_name in surface_transform:
            print(f'setting {surface_name} high')
            self.surfaces[surface_name].extend_pin.high()

        for duration, surface_names in transform_durations:
            print(f'sleeping for {initial[0]} seconds...')
            time.sleep(initial[0])
            for surface_name in surface_names:
                print(f'setting {surface_name} low')
                self.surfaces[surface_name].extend_pin.low()

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


def get_differences(srt):
    run_times = sorted(list(set(srt.values())))
    run_times_adjusted = []
    while run_times:
        run_times_adjusted.append(run_times.pop(0))
        run_times = [rt_ - run_times_adjusted[-1] for rt_ in run_times]
    return run_times_adjusted


def grouped_runtimes(surface_runtimes):
    run_blocks = []
    for runtime_difference in get_differences(surface_runtimes):
        run_blocks.append(
            (
                runtime_difference,
                [
                    surface
                    for surface, surface_runtime in surface_runtimes.items()
                    if surface_runtime >= runtime_difference
                ]
            )
        )
        surface_runtimes = {
            surface: surface_runtime-runtime_difference
            for surface, surface_runtime in surface_runtimes.items()
        }
    turn_off_after = []
    for i, run_block in enumerate(run_blocks):
        try:
            turn_off_after.append(
                (
                    run_block[0],
                    set(run_block[1]) - set(run_blocks[i+1][1])
                )
            )
        except Exception:
            turn_off_after.append(run_block)
    return run_blocks
