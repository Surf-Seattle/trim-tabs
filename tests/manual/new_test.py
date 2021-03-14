import RPi.GPIO as GPIO

from utils import pins
from utils.utilities import (
    constant,
    get_actuators,
    get_relay_time,
    cli_get_new_position,
)


def fully_retract() -> None:
    """Fully retract all of the enabled actuators."""
    for actuator_name, actuator_config in actuators.items():
        print(f"Retracting {actuator_name} acturator.")
        pins.high(
            actuator_config["retract"], duration=get_constant("full_retract_duration")
        )


def update_actuator_position(name: str, current_position: int) -> int:
    """Get and move actuator to new position."""
    new_position = cli_get_new_position(f"enter {name.capitalize()} position.\n>>> ")

    if new_position != current_position:
        # extend or retract the actuator

        pins.high(
            actuators[name]["extend"]
            if new_position > current_position
            else actuators[name]["retract"],
            get_relay_time(current_position, new_position),
        )

        print(f"{name.capitalize()} moved from {current_position} to {new_position}.")

    else:
        # the actuator does not need to move
        print(f"{name.capitalize()} already at {current_position}.")

    return new_position


# initialize postion variable
actuators = get_actuators()
position = {actuator_name: 0 for actuator_name in actuators}

# prepare the pins
pins.init()

# full retract the actuators
fully_retract()

while True:
    # alternate updating the positions of the enabled
    # actuators until a keyboard esacpe is detected

    try:
        for actuator in actuators:
            position[actuator] = update_actuator_position(actuator, position[actuator])

    except KeyboardInterrupt as e:
        GPIO.cleanup()
        break
