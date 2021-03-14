import os
import yaml

from datetime import datetime

from log import logger


class Configuration:
    control_surfaces_path = os.path.join(os.environ['CONFIG_DIR'], 'control_surfaces.yml')

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
            return os.path.join(os.environ['PROFILES_DIR'], f"{cls.username(name)}.yml")
        else:
            return os.path.join(os.environ['PROFILES_DIR'], f"{username}.yml")

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
        return len(os.listdir(os.environ['PROFILES_DIR']))

    @classmethod
    def read_configs(cls):
        logger.info('[UTILITIES] reading all configs')
        for config_file in os.listdir(os.environ['PROFILES_DIR']):
            if config_file.endswith('.yml'):
                yield yaml.safe_load(open(os.path.join(os.environ['PROFILES_DIR'], config_file), 'r'))

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