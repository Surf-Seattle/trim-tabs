import time
import RPi.GPIO as GPIO
from typing import List, Set
import yaml
import os
import logging

from utils import CONFIG_DIR


class Constants:
    path = os.path.join(CONFIG_DIR, 'constants.yml')

    def __init__(self):
        for constant_name, constant_value in yaml.safe_load(open(self.path, 'r')).items():
            setattr(self, constant_name, constant_value)


constants = Constants()


class Controller:
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

    def invert(self) -> None:
        self.move_to(
            {
                regular: self.surfaces[goofy].position
                for regular, goofy in self.goofy_map.items()
            }
        )

    def retract(self, blindly: bool = False) -> None:
        if blindly:
            self.high(
                self.retract_pins,
                duration=self.full_retract_duration,
            )
        else:
            self.move_to(
                {
                    surface_name: 0
                    for surface_name in self.surfaces
                },
                full_travel_duration=self.full_retract_duration,
            )

    def move_to(self, new_positions: dict, full_travel_duration: float = constants.full_extend_duration) -> None:
        """
        Given a dict of surface names and positions, move the surfaces to those positions.

        :param new_positions: a dictionary with surface names as keys and new positions as values.
                              positions must be float values >= 0 and <= 1
        :param full_travel_duration: how many seconds of travel it would take to go from position 0 to position 1
        """
        assert all([0 <= new_position <= 1 for new_position in new_positions.values()])

        # prevent moving to the current position
        for surface_name, new_position in new_positions.copy().items():
            if self.surfaces[surface_name].position == new_position:
                self.logger.info(f"{surface_name} already at {new_position}")
                del new_positions[surface_name]

        # if all the given positions are the same as the current positions, don't do anything.
        if not new_positions:
            self.logger.info("no change required, all positions already satisfied.")
            return

        # transform inputs into easy to follow durations/steps
        change_manifest = self.create_manifest(new_positions, full_travel_duration)

        # explain to the user what is about to happen
        for surface_name, manifest in change_manifest.items():
            self.logger.info(
                f"{manifest['action']}ing {surface_name} from "
                f"{self.surfaces[surface_name].position} to {new_positions[surface_name]}"
            )

        # set all of the target pins high to start
        self.logger.info(change_manifest)
        self.logger.info(self.surfaces[surface_name])
        for surface_name, manifest in change_manifest.items():
            if manifest["action"] == 'retract':
                self.surfaces[surface_name].retract_pin.high()
            elif manifest["action"] == 'extend':
                self.surfaces[surface_name].extend_pin.high()

        # then after each interval gap, turn off the satisfied pins
        self.logger.info('----')
        self.logger.info(
            {
                surface_name: manifest["duration"]
                for surface_name, manifest in change_manifest.items()
            }
        )
        deactive_surfaces_after = self.deactive_surfaces_after(
            {
                surface_name: manifest["duration"]
                for surface_name, manifest in change_manifest.items()
            }
        )
        for partial_duration, surface_names in deactive_surfaces_after:
            self.logger.info(f'sleeping for {round(partial_duration, 4)} seconds...')
            time.sleep(partial_duration)
            for surface_name in surface_names:
                manifest = change_manifest[surface_name]
                getattr(self.surfaces[surface_name], f"{manifest[1]}_pin").low()
                self.surfaces[surface_name].position = new_positions[surface_name]

    def high(self, pin_numbers: List[str], duration: float = None) -> None:
        """
        Given a list of pin-numbers, set each of those pins HIGH.

        :param pin_numbers: a list of pin numbers
        :param duration: optionally, how many seconds the pins show be kept high. If not given, left high indefinitely.
        """
        for surface in self.surfaces.values():
            for pin in list(surface):
                if pin.number in pin_numbers:
                    pin.high()

        if duration:
            self.logger.info(f'sleeping for {round(duration, 4)} seconds...')
            time.sleep(duration)
            self.low(pin_numbers)

    def low(self, pin_numbers: List[str]) -> None:
        """Given a list of pin-numbers, set each of those pins LOW."""
        for surface in self.surfaces.values():
            for pin in list(surface):
                if pin.number in pin_numbers:
                    pin.low()

    @property
    def positions(self) -> dict:
        """A dict of the name each of the controllers `Surface` instances and its current position."""
        return {surface.name: surface.position for surface in self.surfaces.values()}

    @property
    def goofy_map(self) -> dict:
        """A dictionary which maps the names of surfaces and the name of their configured goofy surface."""
        return {
            control_surface['name']: control_surface['goofy']
            for control_surface in self.config
            if control_surface['name'] != control_surface['goofy']
        }

    @property
    def retract_pins(self) -> List[int]:
        """A list of the retract-pin numbers for each of the controllers `Surface` instances."""
        return [
            surface.retract_pin.number
            for surface in self.surfaces.values()
        ]

    @property
    def extend_pins(self) -> List[int]:
        """A list of the retract-pin numbers for each of the controllers `Surface` instances."""
        return [
            surface.extend_pin.number
            for surface in self.surfaces.values()
        ]

    def create_manifest(self, new_positions: List[float], full_travel_duration: float) -> dict:
        """
        Convert the new_positions directory into the change_manifest

        Examples:
            - context: the current position of "A" is 0.1 and "B" is 0.5
            - given: {"A": 0.4, "B": 0.9} and full_travel_duration=2
              return: {"A": (0.6, 'extend'), "B": (0.4, 'retract')}

        :param new_positions: a dictionary of surface names and their new positions
        :param full_travel_duration: how long in seconds a surface takes to travel from position 0 to 1
        :return: a dictionary which identifies the duration and pin for each surface
        """
        # step one is to convert the new_positions dict into a durations dictionary
        # each value in this dict is positive if `extend` and negative if `retract`
        surface_durations = {
            surface_name: (new_position - self.surfaces[surface_name].position) * full_travel_duration
            for surface_name, new_position in new_positions.items()
        }
        # here the durations are made absolute, and the `extend` or `retract` information stored as strings
        change_manifest = {
            surface_name: {
                "duration": abs(duration),
                "action": "extend" if duration > 0 else "retract"
            }
            for surface_name, duration in surface_durations.items()
        }
        return change_manifest

    @staticmethod
    def duration_differences(durations: Set[float]) -> List[float]:
        """
        Given a set of durations, return the list of the differences between them.

        Here are two examples to help make sense of that:
            - given the durations {1, 5, 10}, this function will return [1, 4, 5]
            - given the durations {2, 3, 4}, this function will return [2, 1, 1]

        This is used to determine how long `time.sleep()` needs to be called in between
        setting pins high and then setting them low again so that complex surface movements
        can be performed at the same time, rather than having to move one, then another, then another.

        :param durations: a set containing the durations
        :return: an list which divides up those differences (order matters)
        """
        # order the durations from smallest to largest
        remaining_durations = sorted(list(durations))
        duration_differences = []
        logging.getLogger('Debuggin').info(f"remaining_durations = {remaining_durations}")
        # execute the following until the `remaining_durations` list is empty...
        while remaining_durations:

            # remove the smallest duration from `duration_differences` and append it to `duration_differences`
            duration_differences.append(remaining_durations.pop(0))

            # loop through the `remaining_durations` and subtract value which was just removed from
            # `remaining_durations` (which was the smallest remaining) from durations still in `remaining_durations`
            remaining_durations = [
                remaining_duration - duration_differences[-1]
                for remaining_duration in remaining_durations
            ]
        return duration_differences

    @classmethod
    def deactive_surfaces_after(cls, surface_durations):
        """
        Restructure a `surface_duration` dict to simplify the execution of pin movements with different durations.

        Examples:
            - given {"A": 10, "B": 4, "C": 1}
              return [(1, ["C"]), (3, ["B"]), (6, ["A"])]

            - given {"A": 10, "B": 4, "C": 4}
              return [(4, ["B", "C"]), (6, ["A"])]

        This takes how long each pin should run, and breaks that down.
        In English, the return of first and second examples (respectively) would be:

            - after 1 second: set C low.
              after 3 more seconds: set B low.
              after 6 more seconds: set  A low.

            - after 4 seconds: set B and C low,
              after 6 more seconds: set  A low.

        Restructuring the durations in this way makes executing complex pin transitions much easier.

        :param surface_durations: a dictionary where the keys are surface names and the values are durations.
        :return: the list of tuples structure described above.
        """
        # the first step is to translate the input dictionary into the duration_differences, and for
        # each difference, create a list of surfaces that should be HIGH for that part of the total duration
        # example: transform {"A": 10, "B": 4, "C": 1} to [(1, ["A", "B", "C"]), (3, ["A", "B"]), (6, ["A"])]
        duration_groups = []
        for duration in cls.duration_differences(surface_durations):
            # the surfaces which will be active during this duration will
            # be those whose `remaining_duration` is greater than this duration.
            duration_groups.append(
                {
                    "duration": duration,
                    "active_surfaces": [
                        surface
                        for surface, remaining_duration in surface_durations.items()
                        if remaining_duration >= duration
                    ]
                }
            )

            # once identifying the surfaces which will be active during this duration subtract that
            # duration from each of the surfaces, so that on the next pass the remaining-durations
            # will represent how much time that surface needs to be active
            surface_durations = {
                surface: remaining_duration - duration
                for surface, remaining_duration in surface_durations.items()
            }

        # the second step is to translate the duration groups into output structure
        # example: transform [(1, ["A", "B", "C"]), (3, ["A", "B"]), (6, ["A"])]
        #                 to [(1, ["C"]), (3, ["B"]), (6, ["A"])]
        deactivate_after = []
        for i, duration_group in enumerate(duration_groups):
            try:
                # to identify which surfaces need to be deactivated after each duration
                # all that you need to do is see which surfaces are in the current duration
                # but not in the next duration.
                deactivate_after.append(
                    (
                        duration_group["duration"],
                        set(duration_group["active_surfaces"]) - set(duration_groups[i+1]["active_surfaces"])
                    )
                )
            except IndexError:
                # do this until you reach the last duration in the list, when there is no longer
                # a "next duration", in which case the remaining surfaces should be deactivated.
                deactivate_after.append(
                    (
                        duration_group["duration"],
                        duration_group["active_surfaces"]
                    )
                )

        return deactivate_after



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

        # configure control variables
        self.position = 0
        self.service_duration = constants.full_extend_duration

    def __dict__(self):
        return {'extend': self.extend_pin, 'retract': self.retract_pin}

    def __list__(self):
        return [self.extend_pin, self.retract_pin]

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
                f"extending {self.name} from {self.position} to {new_position}"
            )
            self.position = new_position
            self.extend_pin.high(duration=duration)
        elif new_position < self.position:
            self.logger.info(
                f"retracting {self.name} from {new_position} to {self.position}"
            )
            self.position = new_position
            self.retract_pin.high(duration=duration)
        else:
            self.logger.info(f"{self.name} csalready at {new_position}")

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
            self.logger.info(f"Pin {self.number} HIGH ({round(duration, 4)} seconds)")
            time.sleep(duration)
            self.low()
        else:
            self.logger.info(f"Pin {self.number} HIGH (indefinitely)")

    def low(self) -> None:
        """
        Set this pin low.

        If a `high` is called with a duration, this method will be called after that duration is over.
        """
        self.logger.info(f"Pin {self.number} LOW")
        GPIO.output(self.number, False)


