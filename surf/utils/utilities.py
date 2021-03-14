import os
import yaml


def constant(name: str) -> float:
    """Retrieve a value from constants.yml"""
    constants = yaml.safe_load(
        open(os.path.dirname(__file__) + "/../config/constants.yml", "r")
    )
    return constants[name]


def get_actuators() -> dict:
    """Retrieve the contents of actuators.yml"""
    actuators = yaml.safe_load(
        open(os.path.dirname(__file__) + "/../config/actuators.yml", "r")
    )
    return {k: v for k, v in actuators.items() if v["enabled"]}


def get_relay_time(actuator_position, new_position) -> float:
    """Determine how long a pin needs to be high."""
    relay_time = (
        abs(actuator_position - new_position) / 100 * constant("full_retract_duration")
    )
    print(f"relay time: {relay_time}")
    return relay_time


def cli_get_new_position(initial_promt: str) -> int:
    """Get a valid new actuator position from a command line input."""
    prompt = initial_promt
    int_input = ""
    while not int_input.isdigit():
        int_input = input(prompt)
        if not int_input.isdigit():
            prompt = "please enter an integer!\n>>>"

    if int(int_input) > 100:
        return 100
    elif int(int_input) < 0:
        return 0
    else:
        return int(int_input)
