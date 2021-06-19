import os
import yaml
import time
import logging
from typing import List, Set

if os.environ.get('USE_PINS', 'true') == 'true':
    import RPi.GPIO as GPIO

from utils import CONFIG_DIR
from utils import utilities as u

# module level variable populated when `start()` is called
# this same instance of the variable can be imported from this
# module anywhere that this module can be imported
controller = None


class Controller:
    path = os.path.join(CONFIG_DIR, 'control_surfaces.yml')
    modes = os.path.join(CONFIG_DIR, 'operating_modes.yml')

    def __init__(self):
        self.active_profile = None
        self.deactivate_required = False

        self.logger = logging.getLogger('Surf.Controller')
        self.mode = os.environ.get('MODE', 'wet')
        self.use_pins = os.environ.get('USE_PINS', 'on') == 'on'

        self.travel_durations = yaml.safe_load(open(self.modes, 'r'))[self.mode]
        if self.use_pins:
            # ensure that the rasberry pi pins are ready to go
            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.BCM)

        # create the pin attributes
        self.config = yaml.safe_load(open(self.path, 'r'))
        self.surface_names = [configured_surface['name'] for configured_surface in self.config]
        for configured_surface in self.config:
            setattr(
                self,
                configured_surface['name'],
                Surface(
                    controller=self,
                    name=configured_surface['name'],
                    extend_pin_number=configured_surface['pins']['extend'],
                    retract_pin_number=configured_surface['pins']['retract'],
                )
            )

        self.surfaces = {
            configured_surface['name']: getattr(self, configured_surface['name'])
            for configured_surface in self.config
        }

        self.logger.info("")
        self.logger.info(f"Operating Mode: '{self.mode}'")
        for action in ('deploy', 'withdraw'):
            for pins in range(1, len(self.extend_pins)+1):
                self.logger.info(
                    f"  > to fully {action} {pins} pin(s) takes: {self.travel_durations[pins][action]} seconds"
                )
        self.logger.info("")

    def activate_profile(self, profile_name: str):
        self.active_profile = profile_name
        self.move_to(
            new_positions={
                surface_name: value/100
                for surface_name, value in u.Profile.read_config(username=profile_name)['control_surfaces'].items()
            }
        )
        return self.values

    def deactivate_profile(self) -> dict:
        self.active_profile = None
        self.retract(blindly=True)
        return self.values

    @property
    def surface_display_order(self) -> list:
        return [surface['name'] for surface in self.config][::-1]

    def invert(self) -> None:
        self.move_to(
            {
                regular: self.surfaces[goofy].position
                for regular, goofy in self.goofy_map.items()
            }
        )
        return self.values

    def retract(self, blindly: bool = False) -> None:
        if blindly:
            self.high(
                self.retract_pins,
                travel=1.0,
                action_mode='withdraw'
            )
        else:
            self.move_to(
                {
                    surface_name: 0
                    for surface_name in self.surfaces
                },
                action_mode='deploy'
            )

    def move_to(self, new_positions: dict, action_mode: str = 'deploy') -> None:
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
        change_manifest = self.create_manifest(new_positions)

        # explain to the user what is about to happen
        for surface_name, manifest in change_manifest.items():
            self.logger.info(
                f"{manifest['action']}ing {surface_name} from "
                f"{self.surfaces[surface_name].position} to {new_positions[surface_name]}"
            )

        # set all of the target pins high to start
        hot_pin_count = 0
        for surface_name, manifest in change_manifest.items():
            if manifest["action"] == 'retract':
                hot_pin_count += 1
                self.surfaces[surface_name].retract_pin.high()
            elif manifest["action"] == 'extend':
                hot_pin_count += 1
                self.surfaces[surface_name].extend_pin.high()

        # then after each interval gap, turn off the satisfied pins
        deactive_surfaces_after_percentage_travel = self.deactive_surfaces_after_percentage_travel(
            {
                surface_name: manifest["travel"]
                for surface_name, manifest in change_manifest.items()
            }
        )
        for partial_travel, surface_names in deactive_surfaces_after_percentage_travel:
            partial_duration = self.duration(partial_travel, action_mode=action_mode)

            self.logger.info(f" > {self.hot_pin_count} pin(s)")
            self.logger.info(f" > traveling {round(partial_travel, 6)*100}% full-travel")
            self.logger.info(f" > takes {round(partial_duration, 6)} seconds.")

            self.logger.info(f'sleeping for {round(partial_duration, 6)} seconds...')
            time.sleep(partial_duration)
            for surface_name in surface_names:
                hot_pin_count -= 1
                manifest = change_manifest[surface_name]
                getattr(self.surfaces[surface_name], f"{manifest['action']}_pin").low()
                self.surfaces[surface_name].position = new_positions[surface_name]

    def high(self, pin_numbers: List[str], travel: float = None, action_mode: str = 'deploy') -> None:
        """
        Given a list of pin-numbers, set each of those pins HIGH.

        :param pin_numbers: a list of pin numbers
        :param travel: optionally, what percent of these pins total travel should be traversed
        :param action_mode: optionally, 'deploy' or 'withdraw'
        """
        self.logger.info(f"Setting pins {pin_numbers} high...")
        for surface in self.surfaces.values():
            for pin in [surface.extend_pin, surface.retract_pin]:
                if pin.number in pin_numbers:
                    pin.high()

        if travel:
            duration = self.duration(travel, action_mode)
            self.logger.info(f'sleeping for {duration, 4} seconds...')
            time.sleep(duration)
            self.low(pin_numbers)

    def low(self, pin_numbers: List[str]) -> None:
        """Given a list of pin-numbers, set each of those pins LOW."""
        self.logger.info(f"Setting pins {pin_numbers} low...")
        for surface in self.surfaces.values():
            for pin in [surface.extend_pin, surface.retract_pin]:
                if pin.number in pin_numbers:
                    pin.low()

    @property
    def positions(self) -> dict:
        """A dict of the name each of the controllers `Surface` instances and its current position."""
        return {surface.name: surface.position for surface in self.surfaces.values()}

    @property
    def values(self) -> dict:
        return {
            surface_name: round(surface_position * 100, 0)
            for surface_name, surface_position in self.positions.items()
        }

    @property
    def hot_pin_count(self) -> int:
        """How many pins are hot right now?"""
        return sum([pin.state for surface in self.surfaces.values() for pin in surface.pins])

    def duration(self, travel_percentage: float, action_mode: str = 'deploy') -> float:
        return travel_percentage * self.travel_durations[self.hot_pin_count][action_mode]

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

    def create_manifest(self, new_positions: List[float]) -> dict:
        """
        Convert the new_positions directory into the change_manifest

        Examples:
            - context: the current position of "A" is 0.1 and "B" is 0.5
            - given: {"A": 0.4, "B": 0.9}
              return: {"A": (0.3, 'extend'), "B": (0.4, 'retract')}

        :param new_positions: a dictionary of surface names and their new positions
        :return: a dictionary which identifies the percentage of total travel and pin for each surface
        """
        # step one is to convert the new_positions dict into a durations dictionary
        # each value in this dict is positive if `extend` and negative if `retract`
        surface_percentage_travel = {
            surface_name: (new_position - self.surfaces[surface_name].position)
            for surface_name, new_position in new_positions.items()
        }
        # here the durations are made absolute, and the `extend` or `retract` information stored as strings
        change_manifest = {
            surface_name: {
                "travel": abs(travel_percentage),
                "action": "extend" if travel_percentage > 0 else "retract"
            }
            for surface_name, travel_percentage in surface_percentage_travel.items()
        }
        return change_manifest

    def travel_differences(self, travels: Set[float]) -> List[float]:
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
        remaining_travels = sorted(list(travels.values()))
        travel_differences = []
        # execute the following until the `remaining_durations` list is empty...
        while remaining_travels:

            # remove the smallest duration from `duration_differences` and append it to `duration_differences`
            travel_differences.append(remaining_travels.pop(0))

            # loop through the `remaining_durations` and subtract value which was just removed from
            # `remaining_durations` (which was the smallest remaining) from durations still in `remaining_durations`
            remaining_travels = [
                remaining_travel - travel_differences[-1]
                for remaining_travel in remaining_travels
            ]
        return travel_differences

    def deactive_surfaces_after_percentage_travel(self, surface_travels):
        """
        Restructure a `surface_percentage_travel` dict to simplify the execution of pin
        movements with different precentage travels.

        Examples:
            - given {"A": 1.0, "B": 0.5, "C": 0.1}
              return [(0.1, ["C"]), (0.4, ["B"]), (0.5, ["A"])]

            - given {"A": 0.4, "B": 0.2, "C": 0.2}
              return [(0.2, ["B", "C"]), (0.2, ["A"])]

        This takes how far each pin has to travel, and breaks that down.
        In English, the return of first and second examples (respectively) would be:

            - after 0.1 percent travel: set C low.
              after 0.4 more percent travel: set B low.
              after 0.5 more percent travel: set  A low.

            - after 0.2 percent travel: set B and C low,
              after 0.2 more percent travel: set  A low.

        Restructuring the durations in this way makes executing complex pin transitions much easier.

        :param surface_durations: a dictionary where the keys are surface names and the values are durations.
        :return: the list of tuples structure described above.
        """
        # the first step is to translate the input dictionary into the duration_differences, and for
        # each difference, create a list of surfaces that should be HIGH for that part of the total duration
        # example: transform {"A": 10, "B": 4, "C": 1} to [(1, ["A", "B", "C"]), (3, ["A", "B"]), (6, ["A"])]
        travel_groups = []
        for travel in self.travel_differences(surface_travels):
            # the surfaces which will be active during this duration will
            # be those whose `remaining_duration` is greater than this duration.
            travel_groups.append(
                {
                    "travel": travel,
                    "active_surfaces": [
                        surface
                        for surface, remaining_duration in surface_travels.items()
                        if remaining_duration >= travel
                    ]
                }
            )

            # once identifying the surfaces which will be active during this duration subtract that
            # duration from each of the surfaces, so that on the next pass the remaining-durations
            # will represent how much time that surface needs to be active
            surface_travels = {
                surface: remaining_duration - travel
                for surface, remaining_duration in surface_travels.items()
            }

        # the second step is to translate the duration groups into output structure
        # example: transform [(1, ["A", "B", "C"]), (3, ["A", "B"]), (6, ["A"])]
        #                 to [(1, ["C"]), (3, ["B"]), (6, ["A"])]
        deactivate_after = []
        for i, travel_group in enumerate(travel_groups):
            try:
                # to identify which surfaces need to be deactivated after each duration
                # all that you need to do is see which surfaces are in the current duration
                # but not in the next duration.
                deactivate_after.append(
                    (
                        travel_group["travel"],
                        set(travel_group["active_surfaces"]) - set(travel_groups[i+1]["active_surfaces"])
                    )
                )
            except IndexError:
                # do this until you reach the last duration in the list, when there is no longer
                # a "next duration", in which case the remaining surfaces should be deactivated.
                deactivate_after.append(
                    (
                        travel_group["travel"],
                        travel_group["active_surfaces"]
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

    def __init__(self, controller: Controller, name, extend_pin_number: int, retract_pin_number: int) -> None:
        # configure the parent variable
        self.controller = controller

        # configure identify variables
        self.name = name
        self.logger = logging.getLogger(f'Surf.{self.name}')

        # configure pins
        self.extend_pin = Pin(self, 'extend', extend_pin_number)
        self.retract_pin = Pin(self, 'retract', retract_pin_number)
        self.pins = [self.extend_pin, self.retract_pin]

        # configure control variables
        self.position = 0

    def __dict__(self):
        return {'extend': self.extend_pin, 'retract': self.retract_pin}

    @property
    def value(self) -> int:
        return self.position * 100

    def move_to(
        self,
        new_position: float,
        action_mode: str = 'deploy'
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

        duration = self.controller.travel_durations[1][action_mode] * abs(new_position - self.position)
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
            self.logger.info(f"{self.name} is already at {new_position}")

    def increment(self) -> None:
        """Extend this control surface by `increment_by`, supports + and - in the UI Active Screen."""
        if round(self.position + self.increment_by, 2) <= 1:
            self.logger.info(
                f'extending from {self.position} to {round(self.position + self.increment_by, 2)}'
            )
            self.position = round(self.position + self.increment_by, 2)
            self.extend_pin.high(self.controller.travel_durations[1]['deploy'] * self.increment_by)
        return self.value

    def decrement(self) -> None:
        """Retract this control surface by `increment_by`, supports + and - in the UI Active Screen."""
        if round(self.position - self.increment_by, 2) >= 0:
            self.logger.info(
                f'retracting from {self.position} to {round(self.position - self.increment_by, 2)}'
            )
            self.position = round(self.position - self.increment_by, 2)
            self.retract_pin.high(self.controller.travel_durations[1]['deploy'] * self.increment_by)
        return self.value


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
        if self.surface.controller.use_pins:
            GPIO.setup([self.number], GPIO.OUT)
        self.logger.info(f"Pin {self.number} {self.name}s {self.surface.name}")
        self.state = 0

    def high(self, duration: float = None) -> None:
        """
        Set this pin high.

        :param duration: seconds the pin should be set high. if no duration is given the pin will remain high.
        """
        self.state = 1
        if self.surface.controller.use_pins:
            GPIO.output(self.number, True)
        if duration:
            self.logger.info(f"Pin {self.number} HIGH ({round(duration, 6)} seconds)")
            time.sleep(duration)
            self.low()
        else:
            self.logger.info(f"Pin {self.number} HIGH (indefinitely)")

    def low(self) -> None:
        """
        Set this pin low.

        If a `high` is called with a duration, this method will be called after that duration is over.
        """
        self.state = 0
        self.logger.info(f"Pin {self.number} LOW")
        if self.surface.controller.use_pins:
            GPIO.output(self.number, False)


def start():
    global controller
    controller = Controller()

