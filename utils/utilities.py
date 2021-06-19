import os
import yaml
import click

from datetime import datetime
from shutil import copyfile

import utils


class Configuration:
    control_surfaces_path = os.path.join(utils.CONFIG_DIR, 'control_surfaces.yml')

    def __init__(self) -> None:
        utils.logger.debug(f'[UTILITIES] Reading: {self.control_surfaces_path}')
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
            return os.path.join(utils.PROFILES_DIR, f"{cls.username(name)}.yml")
        else:
            return os.path.join(utils.PROFILES_DIR, f"{username}.yml")

    @classmethod
    def config_exists(cls, name: str = None, username: str = None):
        utils.logger.info(f'[UTILITIES] {cls.get_path(name, username)} exists: {os.path.exists(cls.get_path(name, username))}')
        return os.path.exists(cls.get_path(name, username))

    @classmethod
    def read_config(cls, name: str = None, username: str = None):
        utils.logger.info(f'[UTILITIES] reading config: {cls.get_path(name, username)}')
        return yaml.safe_load(open(cls.get_path(name, username), 'r'))

    @classmethod
    def count(cls) -> int:
        utils.logger.info('[UTILITIES] counting configs')
        return len(os.listdir(utils.PROFILES_DIR))

    @classmethod
    def read_configs(cls):
        utils.logger.info('[UTILITIES] reading all configs')
        for config_file in os.listdir(utils.PROFILES_DIR):
            if config_file.endswith('.yml'):
                yield yaml.safe_load(open(os.path.join(utils.PROFILES_DIR, config_file), 'r'))

    @classmethod
    def initial_config(cls, name) -> dict:
        return {
            'created': datetime.now().strftime('%d-%m-%Y %H:%M:%S'),
            'name': name,
            'username': cls.get_username(name),
        }

    def __init__(self, name: str = None, username: str = None):
        utils.logger.info(f'[UTILITIES] Initializing profile: {name or username}')
        self.given_name = name
        self.username = username or self.get_username(self.given_name)
        self.exists = self.config_exists(username=self.username)
        self.path = self.get_path(username=self.username)

        if self.exists:
            utils.logger.info('[UTILITIES] \t- this profile exists')
            self._config = self.read_config(username=self.username)
            self._name = self._config['name']
        else:
            utils.logger.info('[UTILITIES] \t- this profile DOES NOT exist')
            self._config = self.initial_config(self.given_name)

    def create(self, control_surface_values: dict):
        utils.logger.info(f'[UTILITIES] Creating profile for: "{self.given_name}"')
        utils.logger.info(f'[UTILITIES] \t- control surface values: {control_surface_values}')
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
            utils.logger.info(f'[UTILITIES] {self.username} already exists!')

    def delete(self) -> None:
        if self.config_exists(username=self.username):
            os.remove(self.path)
            utils.logger.info(f"[UTILITIES] deleted profile: {self.path}")
        else:
            utils.logger.info(f'[UTILITIES] cannot delete profile which does not exist: {self.username}')

    def update(self, new_config) -> None:
        if self.config_exists(username=self.username):
            utils.logger.info(f'[UTILITIES] updating: {self.path}')
            self._config.update(new_config)
            with open(self.path, 'w') as outfile:
                yaml.dump(self._config, outfile, default_flow_style=False, sort_keys=False)
        else:
            utils.logger.info(f'[UTILITIES] cannot update a profile which does not exist: {self.username}')


def first_time_setup_check():
    """Ensure all the necessary directories and files are in place to run the application."""
    # create necessary `~/.surf` directories if they don't exist
    for required_prelogging_dir in [utils.HOME_DIR, utils.LOGS_DIR]:
        if not os.path.isdir(required_prelogging_dir):
            print(f"[logger not yet available] `{required_prelogging_dir}` does not exist, creating it now.")
            os.mkdir(required_prelogging_dir)

    if not utils.logger:
        utils.logger = utils.create_logger()
        utils.logger.info("[logger now available]")

    for required_directory in [utils.PROFILES_DIR, utils.CONFIG_DIR]:
        if not os.path.isdir(required_directory):
            utils.logger.info(f"`{required_directory}` does not exist, creating it now.")
            os.mkdir(required_directory)

    # ensure necessary configuration files are present
    for required_config_file in ['control_surfaces.yml', 'operating_modes.yml']:
        if not os.path.isfile(os.path.join(utils.CONFIG_DIR, required_config_file)):
            update_config_from_template(required_config_file)

    # ensure profiles exist
    if not os.listdir(utils.PROFILES_DIR):
        copy_template_profiles()  # if none exist, the templates will be used


def update_config_from_template(file_name: str) -> None:
    """Copy a configuration file template into the CONFIG_DIR"""
    templates_dir = os.path.join('utils', 'config_templates')
    template_files = (
        os.listdir(templates_dir)
        if file_name == 'all' else
        [file_name]
    )
    for file_name in template_files:
        source_file = os.path.join(templates_dir, file_name)
        target_file = os.path.join(utils.CONFIG_DIR, file_name)
        replace_file(source_file, target_file)


def update_operating_mode_value(mode: str, concurrency: int, context: str, new_value: str) -> None:
    """Update a value in CONFIG_DIR/operating_mode.yml"""
    config_path = os.path.join(utils.CONFIG_DIR, 'operating_modes.yml')
    if not os.path.isfile(config_path):
        update_config_from_template('operating_modes.yml')

    operating_modes = yaml.safe_load(open(config_path, 'r'))
    if mode not in operating_modes:
        return f"'{mode}' is not an existing operating-mode, those are: {set(mode)}"
    if concurrency not in operating_modes[mode]:
        return f"'{mode}' does not have a {concurrency} surface concurrency, it has: {set(operating_modes[mode])}"
    if context not in operating_modes[mode][concurrency]:
        return f"'{mode}' does not have a {context} context with {concurrency} surface concurrency, " \
               f"it has: {set(operating_modes[mode])}"

    utils.logger.info(f"Setting {mode}.{concurrency}.{context} to {new_value} in '{config_path}'")
    operating_modes[mode][concurrency][context] = float(new_value)
    open(config_path, 'w').write(yaml.dump(operating_modes, default_flow_style=False, sort_keys=False))


def update_wave_profile(profile_name: str, values: list) -> None:
    """Update value(s) in wave-profile yml in PROFILES_DIR"""
    username = profile_name.lower()
    path = os.path.join(utils.PROFILES_DIR, f"{username}.yml")
    control_surfaces = yaml.safe_load(open(os.path.join(utils.CONFIG_DIR, 'control_surfaces.yml'), 'r'))
    control_surface_names = [surface["name"] for surface in control_surfaces]
    if len(control_surface_names) != len(values):
        return f"Wrong number of values provided. There are {len(control_surface_names)} control-surfaces, " \
               f"{control_surface_names}, but only {len(values)} values were provided. Provide " \
               f"{len(control_surface_names)} values ordered the same as the control surface names shown."

    if not all([value % 5 == 0 for value in values]):
        return f"Each value needs to be divisible by 5, not all of these values are: {values}"

    if not os.path.isfile(path):
        return f"{path} does not exist."
    else:
        wave_profile = yaml.safe_load(open(path, 'r'))
        new_profile_surface_values = dict(zip(control_surface_names, values))

        click.echo(f"\nConfirm Wave-Profile Update\n")
        is_real_change = any(
            [
                wave_profile['control_surfaces'][surface_name] != new_profile_surface_values[surface_name]
                for surface_name in control_surface_names
            ]
        )

        if not is_real_change:
            return f"Those are already the values of this profile: {wave_profile['control_surfaces']}"

        for surface_name in control_surface_names:
            old_value = wave_profile['control_surfaces'][surface_name]
            new_value = new_profile_surface_values[surface_name]
            if old_value == new_value:
                click.echo(f"\t{surface_name}: {old_value} (no change)")
            else:
                click.echo(f"\t{surface_name}: {old_value} --> {new_value}")

        click.echo("")
        if click.confirm('Do you want to update this wave-profile?', abort=True):
            open(path, 'w').write(
                yaml.dump(
                    {
                        "name": wave_profile["name"],
                        "username": wave_profile["username"],
                        "control_surfaces": new_profile_surface_values
                    },
                    default_flow_style=False,
                    sort_keys=False
                )
            )


def create_new_wave_profile(profile_name: str, values: list) -> None:
    """Create a new wave-profile yml in PROFILES_DIR"""
    username = profile_name.lower()
    path = os.path.join(utils.PROFILES_DIR, f"{username}.yml")
    control_surfaces = yaml.safe_load(open(os.path.join(utils.CONFIG_DIR, 'control_surfaces.yml'), 'r'))
    control_surface_names = [surface["name"] for surface in control_surfaces]
    if len(control_surface_names) != len(values):
        return f"Wrong number of values provided. There are {len(control_surface_names)} control-surfaces, " \
               f"{control_surface_names}, but only {len(values)} values were provided. Provide " \
               f"{len(control_surface_names)} values ordered the same as the control surface names shown."

    if not all([value % 5 == 0 for values in values]):
        return f"Each value needs to be divisible by 5, not all of these values are: {values}"

    new_profile_surface_values = dict(zip(control_surface_names, values))
    if os.path.isfile(path):
        return f"Name already in use, because {path} already exists."
    else:
        click.echo(f"\nConfirm new Wave-Profile detais\n")
        click.echo(f"\tName: {profile_name}")
        click.echo(f"\tFile: {path}")
        for surface_name, surface_value in new_profile_surface_values.items():
            click.echo(f"\t{surface_name}: {surface_value}")
        click.echo("")

    if click.confirm('Do you want to create this wave-profile?', abort=True):
        open(path, 'w').write(
            yaml.dump(
                {
                    "name": profile_name,
                    "username": username,
                    "control_surfaces": new_profile_surface_values
                },
                default_flow_style=False,
                sort_keys=False
            )
        )


def delete_wave_profile(profile_name: str) -> None:
    """Delete a wave-profile yml in PROFILES_DIR"""
    username = profile_name.lower()
    path = os.path.join(utils.PROFILES_DIR, f"{username}.yml")
    if not os.path.isfile(path):
        return f"{path} does not exist, so no need to delete it :)"
    else:
        utils.logger.info(f"Deleting file: {path}")
        os.remove(path)


def copy_template_profiles() -> None:
    """Copy all of the file in utils/profile_templtes to PROFILES_DIR"""
    template_dir = os.path.join('utils', 'profile_templates')
    for template_profile_filename in os.listdir(template_dir):
        replace_file(
            source_file=os.path.join(template_dir, template_profile_filename),
            target_file=os.path.join(utils.PROFILES_DIR, template_profile_filename)
        )


def replace_file(source_file: str, target_file: str) -> None:
    """Copy a file from one directory to another (with helpful logging messages)"""
    if os.path.isfile(target_file):
        utils.logger.info(f'Removing existing: "{target_file}"')
        os.remove(target_file)

    utils.logger.info(f'Copying "{source_file}" to "{target_file}"')
    copyfile(source_file, target_file)


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
        wid.saved_attrs = wid.height, (wid.size_hint_y * 0.45), wid.opacity, wid.disabled
        wid.height, wid.size_hint_y, wid.opacity, wid.disabled = 0, None, 0, True

