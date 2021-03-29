import os
import yaml

from datetime import datetime

from utils import (
    logger,
    PROFILES_DIR,
    CONFIG_DIR
)


class Configuration:
    control_surfaces_path = os.path.join(CONFIG_DIR, 'control_surfaces.yml')

    def __init__(self) -> None:
        logger.debug(f'[UTILITIES] Reading: {self.control_surfaces_path}')
        self.control_surfaces = yaml.safe_load(open(self.control_surfaces_path, 'r'))

    def control_surfaces_attribute(self, attr: str) -> list:
        return [surface.get(attr) for surface in self.control_surfaces]

    @property
    def goofy_map(self) -> dict:
        return dict(zip(self.control_surfaces_attribute('name'), self.control_surfaces_attribute('goofy')))


class Profile:

    @classmethod
    def get_username(cls, name: str) -> str:
        return name.lower().strip().replace(' ', '_')

    @classmethod
    def get_path(cls, name: str = None, username: str = None) -> str:
        if name:
            return os.path.join(PROFILES_DIR, f"{cls.username(name)}.yml")
        else:
            return os.path.join(PROFILES_DIR, f"{username}.yml")

    @classmethod
    def config_exists(cls, name: str = None, username: str = None):
        logger.info(f'[UTILITIES] {cls.get_path(name, username)} exists: {os.path.exists(cls.get_path(name, username))}')
        return os.path.exists(cls.get_path(name, username))

    @classmethod
    def read_config(cls, name: str = None, username: str = None):
        logger.info(f'[UTILITIES] reading config: {cls.get_path(name, username)}')
        return yaml.safe_load(open(cls.get_path(name, username), 'r'))

    @classmethod
    def count(cls) -> int:
        logger.info('[UTILITIES] counting configs')
        return len(os.listdir(PROFILES_DIR))

    @classmethod
    def read_configs(cls):
        logger.info('[UTILITIES] reading all configs')
        for config_file in os.listdir(PROFILES_DIR):
            if config_file.endswith('.yml'):
                yield yaml.safe_load(open(os.path.join(PROFILES_DIR, config_file), 'r'))

    @classmethod
    def initial_config(cls, name) -> dict:
        return {
            'created': datetime.now().strftime('%d-%m-%Y %H:%M:%S'),
            'name': name,
            'username': cls.get_username(name),
        }

    def __init__(self, name: str = None, username: str = None):
        logger.info(f'[UTILITIES] Initializing profile: {name or username}')
        self.given_name = name
        self.username = username or self.get_username(self.given_name)
        self.exists = self.config_exists(username=self.username)
        self.path = self.get_path(username=self.username)

        if self.exists:
            logger.info('[UTILITIES] \t- this profile exists')
            self._config = self.read_config(username=self.username)
            self._name = self._config['name']
        else:
            logger.info('[UTILITIES] \t- this profile DOES NOT exist')
            self._config = self.initial_config(self.given_name)

    def create(self, control_surface_values: dict):
        logger.info(f'[UTILITIES] Creating profile for: "{self.given_name}"')
        logger.info(f'[UTILITIES] \t- control surface values: {control_surface_values}')
        assert len(control_surface_values) == len(Configuration().control_surfaces), "wrong number of control surfaces"
        assert all([isinstance(surface_value, int) for surface_value in control_surface_values.values()]), "all values must be integers"
        assert all([0 <= surface_value <= 100 for surface_value in control_surface_values.values()]), "one or more out of bounds value"

        new_config = self.initial_config(name=self.given_name)
        new_config['control_surfaces'] = control_surface_values
        new_config['goofy'] = False

        if not self.exists:
            with open(self.path, 'w') as outfile:
                yaml.dump(new_config, outfile, default_flow_style=False, sort_keys=False)
        else:
            logger.info(f'[UTILITIES] {self.username} already exists!')

    def delete(self) -> None:
        if self.config_exists(username=self.username):
            os.remove(self.path)
            logger.info(f"[UTILITIES] deleted profile: {self.path}")
        else:
            logger.info(f'[UTILITIES] cannot delete profile which does not exist: {self.username}')

    def update(self, new_config) -> None:
        if self.config_exists(username=self.username):
            logger.info(f'[UTILITIES] updating: {self.path}')
            self._config.update(new_config)
            with open(self.path, 'w') as outfile:
                yaml.dump(self._config, outfile, default_flow_style=False, sort_keys=False)
        else:
            logger.info(f'[UTILITIES] cannot update a profile which does not exist: {self.username}')


def get_constant(name: str) -> float:
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
        abs(actuator_position - new_position) / 100 * get_constant("full_retract_duration")
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


def get_parent(ui_element, **kwargs):
    if kwargs.get('classname'):
        if type(ui_element).__name__ == kwargs['classname']:
            return ui_element
        else:
            print(f"looking for {kwargs['classname']}, finding:{ui_element.__class__.__name__}")
            return get_parent(ui_element.parent, **kwargs)


def get_child_of_parent(ui_element, classname):
    if not hasattr(ui_element, 'children'):
        print(f"{ui_element.__class__.__name__} does not have `children` attribute")
        get_child_of_parent(ui_element.parent, classname)
    else:
        print(f"{ui_element.__class__.__name__} has `children` attribute")
        for child in ui_element.children:
            print(f"checking {ui_element.__class__.__name__} child: {child.__class__.__name__}")
            if child.__class__.__name__ == classname:
                return child
        else:
            return get_child_of_parent(ui_element.parent, classname)





def get_active_profile(ui_element):
    screen_manager = get_parent(ui_element, classname='ScreenManager')
    return getattr(screen_manager, 'active_profile', None)


def set_active_profile(ui_element, profile_identifier) -> None:
    screen_manager = get_parent(ui_element, classname='ScreenManager')
    setattr(screen_manager, 'active_profile', profile_identifier)


def get_root_screen(ui_element):
    if ui_element.__class__.__name__ == 'SurfRootScreen':
        return ui_element
    else:
        return get_root_screen(ui_element.parent)


def get_screen(ui_element, screen_name):
    try:
        return [s for s in get_root_screen(ui_element).screen_manager.children if s.name == screen_name][0]
    except IndexError as e:
        print(f'couldnt find {screen_name} in {get_root_screen(ui_element).screen_manager.children}')


def hide_widget(wid, dohide=True):
    if hasattr(wid, 'saved_attrs'):
        if not dohide:
            wid.height, wid.size_hint_y, wid.opacity, wid.disabled = wid.saved_attrs
            del wid.saved_attrs
    elif dohide:
        wid.saved_attrs = wid.height, wid.size_hint_y, wid.opacity, wid.disabled
        wid.height, wid.size_hint_y, wid.opacity, wid.disabled = 0, None, 0, True
