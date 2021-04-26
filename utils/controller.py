import time
import RPi.GPIO as GPIO
from typing import List
import yaml
import os
import logging

from utils import CONFIG_DIR, logger


class Constants:
    path = os.path.join(CONFIG_DIR, 'constants.yml')

    def __init__(self):
        for constant_name, constant_value in yaml.safe_load(open(self.path, 'r')).items():
            setattr(self, constant_name, constant_value)


constants = Constants()


class ControlSurfaces:
    path = os.path.join(CONFIG_DIR, 'control_surfaces.yml')

    def __init__(self):
        self.logger = logging.getLogger('Surf.Controller')

        # ensure that the rasberry pi pins are ready to go
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        # pick up some constants
        self.full_extend_duration = constants.full_extend_duration
        self.full_retract_duration = constants.full_retract_duration

        # create the pin attributes
        self.config = yaml.safe_load(open(self.path, 'r'))
        for configured_surface in self.config:
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
            for configured_surface in self.config
        }

    @property
    def goofy_map(self) -> dict:
        return {
            control_surface['name']: control_surface['goofy']
            for control_surface in self.config
            if control_surface['name'] != control_surface['goofy']
        }

    def invert(self) -> None:
        self.move_to(
            {
                regular: self.surfaces[goofy].position
                for regular, goofy in self.goofy_map.items()
            }
        )

    def retract(self, blindly: bool = False) -> None:
        if blindly:
            for surface in self.surfaces.values():
                surface.retract_pin.high()
            time.sleep(constants.full_retract_duration)
            for surface in self.surfaces.values():
                surface.retract_pin.low()
        else:
            self.move_to(
                {
                    surface_name: 0
                    for surface_name in self.surfaces
                },
                full_travel_duration=self.full_retract_duration,
            )

    def move_to(
        self,
        new_positions: dict,
        full_travel_duration: float = constants.full_extend_duration,
        force: bool = False
    ) -> None:
        """Given a dict of surface names and positions, move the surfaces to those positions."""
        assert all([0 <= new_position <= 1 for new_position in new_positions.values()])

        # prevent moving to the current position
        for surface_name, new_position in new_positions.copy().items():
            if self.surfaces[surface_name].position == new_position and not force:
                self.logger.info(f"{surface_name} already at {new_position}")
                del new_positions[surface_name]

        # if all the given positions are the same as the current positions, don't do anything.
        if not new_positions:
            self.logger.info("no change required, all positions already satisfied.")
            return

        # transform inputs into easy to follow durations/steps
        duration_change = {
            surface_name: (new_position - self.surfaces[surface_name].position) * full_travel_duration
            for surface_name, new_position in new_positions.items()
        }
        change_manifest = {
            surface_name: (abs(duration), 'extend' if duration > 0 else 'retract')
            for surface_name, duration in duration_change.items()
        }

        # explain to the user what is about to happen
        for surface_name, manifest in change_manifest.items():
            logger.info(
                f"{manifest[1]}ing {surface_name} from "
                f"{self.surfaces[surface_name].position} to {new_positions[surface_name]}"
            )

        # set all of the target pins high to start
        for surface_name, manifest in change_manifest.items():
            self.logger.info(f'setting {surface_name}.{manifest[1]} high')
            getattr(self.surfaces[surface_name], f"{manifest[1]}_pin").high()

        # then after each interval gap, turn off the satisfied pins
        transform_durations = grouped_runtimes({k: v[0] for k, v in change_manifest.items()})
        for duration, surface_names in transform_durations:
            self.logger.info(f'sleeping for {duration} seconds...')
            time.sleep(duration)
            for surface_name in surface_names:
                manifest = change_manifest[surface_name]
                self.logger.info(f'setting {surface_name}.{manifest[1]} low')
                getattr(self.surfaces[surface_name], f"{manifest[1]}_pin").low()
                self.surfaces[surface_name].position = new_positions[surface_name]

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

    @property
    def positions(self) -> dict:
        return {surface.name: surface.position for surface in self.surfaces.values()}


class Surface:
    """
    Control class for a single Surface.

    - Each `ControlSurfaces` instance will have a `Surface` instance for each
      list item defined in ~/.surf/config/control_surfaces.yml
      By default this would be 3 instances, one for PORT, CENTER, and STARBOARD
    - Each `Surface` instance will have two `Pin` instances.
      One which extends the surface when set high, another which retracts the surface when set high.
    """

    increment_by = 0.05

    def __init__(self, name, extend_pin_number: int, retract_pin_number: int) -> None:
        # configure identify variables
        self.name = name
        self.logger = logging.getLogger(f'Surf.{self.name}')

        # configure pins
        self.extend_pin = Pin(self, 'extend', extend_pin_number)
        self.retract_pin = Pin(self, 'retract', retract_pin_number)
        self.pins = [self.extend_pin, self.retract_pin]

        # configure control variables
        self.position = 0
        self.service_duration = constants.full_extend_duration

    def move_to(
        self,
        new_position: float,
        full_travel_duration: float = constants.full_extend_duration
    ) -> None:
        """
        Move this surface from its current position to a new position.

        :param new_position: a value between 0 and 1, representing the new position to which the pin should be moved.
        :param full_travel_duration: the total travel duration in seconds which will be multiplied by the absolute
                                     value of the difference between the surfaces current position and the new_position
                                     to determine how long the appropriate pin should be set high.
        """
        assert 0 <= new_position <= 1, (
            f"`Surface.move_to()` (the '{self.name}' instance) was called with a `new_position` of {new_position}. "
            f"The `new_position` value must be greater than or equal to 0 and less than or equal to 1."
        )

        duration = full_travel_duration * abs(new_position - self.position)
        if new_position > self.position:
            self.logger.info(
                f"extending {self.name} from {self.position} to {new_position} (duration: {round(duration, 2)})"
            )
            self.position = new_position
            self.extend_pin.high(duration=duration)
        elif new_position < self.position:
            self.logger.info(
                f"retracting {self.name} from {new_position} to {self.position} (duration: {round(duration, 2)})"
            )
            self.position = new_position
            self.retract_pin.high(duration=duration)
        else:
            self.logger.info(f"{self.name} is already at {new_position}")

    def increment(self) -> None:
        """Extend this control surface by `increment_by`, supports + and - in the UI Active Screen."""
        if round(self.position + self.increment_by, 2) <= 1:
            self.logger.info(
                f'extending from {self.position} to {round(self.position + self.increment_by, 2)}'
            )
            self.position = round(self.position + self.increment_by, 2)
            self.extend_pin.high(self.service_duration * self.increment_by)

    def decrement(self) -> None:
        """Retract this control surface by `increment_by`, supports + and - in the UI Active Screen."""
        if round(self.position - self.increment_by, 2) >= 0:
            self.logger.info(
                f'retracting from {self.position} to {round(self.position - self.increment_by, 2)}'
            )
            self.position = round(self.position - self.increment_by, 2)
            self.retract_pin.high(self.service_duration * self.increment_by)


class Pin:
    """
    Control class for a single Pin.

    - Each `Surface` instance will have two `Pin` instances.
    - One which extends the surface when set high, another which retracts the surface when set high.
    """

    def __init__(self, surface: Surface, name: str, number: int) -> None:
        self.name = name
        self.number = number
        self.surface = surface
        self.logger = logging.getLogger(f"Surf.{self.surface.name}.{self.name}")
        GPIO.setup([self.number], GPIO.OUT)
        self.logger.info(f"Pin {self.number} {self.name}s {self.surface.name}")

    def high(self, duration: float = None) -> None:
        """
        Set this pin high.

        :param duration: seconds the pin should be set high. if no duration is given the pin will remain high.
        """
        GPIO.output(self.number, True)
        if duration:
            time.sleep(duration)
            self.low()

    def low(self) -> None:
        """
        Set this pin low.

        If a `high` is called with a duration, this method will be called after that duration is over.
        """
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
    return turn_off_after
