"""
Command line prompts which walk a first-time user through setting
up their `~/.surf/config/control_surfaces.yml` file as well as one
or more files in `~/.surf/profiles`.

This removes the need for manual file manipulation before the script runs.
"""
import os
import yaml

from utils import (
    logger,
    CONFIG_DIR,
    PROFILES_DIR
)


class SetUpControlSurfaces:
    control_surfaces_path = os.path.join(CONFIG_DIR, 'control_surfaces.yml')

    @classmethod
    def surface_names(self) -> list:
        return [surface['name'] for surface in yaml.safe_load(open(self.control_surfaces_path, 'r'))]

    @property
    def setup_required(self) -> bool:
        if not os.path.isfile(self.control_surfaces_path):
            logger.info(f'[SETUP] file does not exist, set-up required.')
            return True
        else:
            try:
                control_surfaces = yaml.safe_load(open(self.control_surfaces_path, 'r'))
            except Exception:
                logger.info(f'[SETUP] file could not be loaded as a yaml file, set-up required.')
                return True
            else:
                if not isinstance(control_surfaces, list):
                    logger.info(f'[SETUP] yaml file did not contain a list as expected, set-up required.')
                    return True
                if not all([isinstance(x, dict) for x in control_surfaces]):
                    logger.info(f'[SETUP] yaml file did not contain a list of dicts as expected, set-up required.')
                    return True
                if not all([set(x) == {'name', 'goofy', 'pins'} for x in control_surfaces]):
                    logger.info(f'[SETUP] yaml file list of dicts did not contain the expected keys, set-up required.')
                    return True

    def __init__(self):
        logger.info(f'[SETUP] checking {self.control_surfaces_path}')
        if self.setup_required:
            control_surface_config = [
                {
                    'name': surface_name,
                    'goofy': goofy_surface,
                    'pins': {
                        'extend': pin_config['extend'],
                        'retract': pin_config['retract'],
                    }
                }
                for surface_name, goofy_surface, pin_config
                in self.create_control_surfaces()
            ]
            with open(self.control_surfaces_path, 'w') as control_surface_config_file:
                yaml.dump(
                    control_surface_config,
                    control_surface_config_file,
                    default_flow_style=False,
                    sort_keys=False
                )

            print(f'\nFile written: {self.control_surfaces_path}\n')

    def create_control_surfaces(self):
        print('-'*60)
        print('Configure Control Surfaces'.center(60))
        print('-'*60)
        print('')
        print('* each control surface represents a single trim tab')
        print('* enter the trim tabs in the order that you would like')
        print('  them to appear in the UI (from left to right).')
        surface_names = self.get_control_surface_names()
        return zip(
            surface_names,
            self.get_goofy_control_surface_mapping(surface_names),
            self.get_pin_numbers(surface_names)
        )

    def get_control_surface_names(self):
        """Get the name of the control surfaces"""

        def get_count() -> str:
            """get the number of control surfaces to configure"""
            while True:
                control_surface_count = input('\nhow many control surfaces will be configured: ')
                if control_surface_count.strip().isdigit():
                    return int(control_surface_count)
                else:
                    print('\n!! please enter an integer\n')

        def get_name(i: int, n: int, already_used_names: list) -> str:
            """Get the name of one of the surfaces to be configured"""
            while True:
                surface_name = input(f'enter the name of control surface {i+1} of {n}: ')
                if not surface_name.isalpha():
                    print('\t!! This name is not valid.')
                    print('\t!! Use ONLY letters.')
                    print('\t!! No spaces or other characters allowed.')
                elif surface_name in already_used_names:
                    print('\t!! This name has already been used.')
                else:
                    return surface_name

        while True:
            control_surface_count = get_count()
            control_surface_names = []
            for i in range(control_surface_count):
                control_surface_names.append(
                    get_name(i, control_surface_count, control_surface_names)
                )
            print('\n' + ' REVIEW SURFACE NAMES '.center(60, '-') + '\n')
            print('You have entered the following control surface names:')
            for surface_name in control_surface_names:
                print(f'\t- {surface_name}')
            print('\nRemember, order matters!')
            print('If you want to re-order the control surfaces, you will need to start over.')
            print('\nAre you happy with the names as shown?')
            print('  "y" -- Yes, I am happy with these names.')
            print('  "N" -- No, I want to re-enter the control surface names.\n')
            accept_names = input('>>> ')
            if accept_names == 'y':
                return control_surface_names
            elif accept_names != 'N':
                print('\n!! please enter a valid response.\n')

    def get_goofy_control_surface_mapping(self, control_surface_names):

        def get_goofy_counterpart(main_surface: str, choose_from: list) -> str:
            while True:
                print('')
                print(f'Choose from: {choose_from}')
                goofy_name = input(f'Enter the goofy counterpart of {main_surface}: ')
                clean_goofy_name = goofy_name.upper().strip()
                if clean_goofy_name in remaining_options:
                    return clean_goofy_name
                else:
                    print(f'\n!! "{clean_goofy_name}" was not one of the valid options. try again.')

        print('')
        print('-'*60)
        print('"Goofy" Control Surface Mapping'.center(60))
        print('-'*60)
        print('')
        print('* each control surface needs a goofy counterpart.')
        print('* a control surface will flip its value with its goofy')
        print('  counterpart when flipping between goofy and regular.')
        print('* a control surface can be its own goofy counterpart if')
        print('  its value should not be changed between goofy and regular.')

        while True:
            remaining_options = control_surface_names.copy()
            goofy_surface_names = []
            for control_surface_name in control_surface_names:
                goofy_surface_names.append(get_goofy_counterpart(control_surface_name, remaining_options))
                remaining_options.remove(goofy_surface_names[-1])

            print('')
            print(' REVIEW GOOFY MAPPING '.center(60, '-'))
            print('')
            print('You have created the following goofy mapping:')
            for name, goofy_name in zip(control_surface_names, goofy_surface_names):
                print(f'\t {name} <--> {goofy_name}')
            print('')
            print('Are you happy with the mapping as shown?')
            print('  "y" -- Yes, I am happy with this mapping.')
            print('  "N" -- No, I want to re-enter the mapping values.')
            print('')
            accept_goofy = input('>>> ')
            if accept_goofy == 'y':
                return goofy_surface_names
            elif accept_goofy != 'N':
                print('\n!! please enter a valid response.\n')

    def get_pin_numbers(self, control_surface_names) -> dict:

        def get_pin(surface_name: str, extend_or_retract: str) -> int:
            """Get the expand or retract pin for a control surface from the user."""
            assert extend_or_retract in ('extend', 'retract')
            while True:
                pin_number = input(f'enter {surface_name} {extend_or_retract} pin numer: ')
                if pin_number.strip().isdigit():
                    return int(pin_number)
                else:
                    print('')
                    print('!! only enter integer values.')
        print('')
        print('-'*60)
        print('Control Surface Pin Mapping'.center(60))
        print('-'*60)
        print('')
        print('* each control surface needs to be configured to two pins on the rasberry pi.')
        print('* one pin will extend the control surface when set high.')
        print('* the other will retract the control surface when set high.')
        print('')
        while True:
            pin_mapping = [
                {
                    'extend': get_pin(pin_name, 'extend'),
                    'retract': get_pin(pin_name, 'retract'),
                }
                for pin_name in control_surface_names
            ]

            print('\n' + ' REVIEW PIN MAPPING '.center(60, '-') + '\n')
            print('You have created the following pin mapping:')
            for surface_name, pins in zip(control_surface_names, pin_mapping):
                print(f'\t{surface_name}')
                print(f'\t\textend pin: {pins["extend"]}')
                print(f'\t\tretract pin: {pins["retract"]}')
            print('\nAre you happy with the mapping as shown?')
            print('  "y" -- Yes, I am happy with this mapping.')
            print('  "N" -- No, I want to re-enter the pin numbers.\n')
            accept_pins = input('>>> ')
            if accept_pins == 'y':
                return pin_mapping
            elif accept_pins != 'N':
                print('\n!! please enter a valid response.\n')


class SetUpProfiles:

    @property
    def setup_required(self) -> bool:
        if not os.listdir(PROFILES_DIR):
            logger.info(f'[SETUP] no profiles found in {PROFILES_DIR}.')
            return True

    @staticmethod
    def validate_existing_profiles() -> None:

        if not os.listdir(PROFILES_DIR):
            return

        for profile_file_name in os.listdir(PROFILES_DIR):
            profile_file_path = os.path.join(PROFILES_DIR, profile_file_name)

            # ensure profile config can be read as a yaml file
            try:
                profile_config = yaml.safe_load(open(profile_file_path, 'r'))
            except Exception:
                logger.info(f'[SETUP] {profile_file_name} could not be loaded as a yaml file, it will be deleted.')
                os.remove(profile_file_path)
            else:

                # ensure the profile isnt empty
                if profile_config is None:
                    logger.info(f'[SETUP] {profile_file_name} was empty, it will be deleted.')
                    os.remove(profile_file_path)
                    continue

                # ensure the top level of the profile config has the right keys with the right type of values
                expected_values = [
                    ('name', str),
                    ('username', str),
                    ('control_surfaces', dict),
                ]
                for expect_value_key, expected_value_type in expected_values:
                    if not 'name' in profile_config:
                        logger.info(
                            f'[SETUP] {profile_file_name} did not contain key "{expect_value_key}". '
                            f'deleting this invalid config.'
                        )
                        os.remove(profile_file_path)
                    elif not isinstance(profile_config['name'], str):
                        logger.info(
                            f'[SETUP] {profile_file_name} "{expected_value_type}" value was not a '
                            f'{expected_value_type.__name__}. deleting this invalid config.'
                        )
                        os.remove(profile_file_path)

            # ensure control surface names are valid
            valid_surface_names = SetUpControlSurfaces.surface_names()
            if os.path.isfile(profile_file_path):
                profile_config = yaml.safe_load(open(profile_file_path, 'r'))
                for configured_surface_name, surface_value in profile_config['control_surfaces'].items():
                    if configured_surface_name not in valid_surface_names:
                        logger.info(
                            f'[SETUP] {profile_file_name} contained key {configured_surface_name} in '
                            f'"control_surfaces". this is not a valid control surface name. '
                            f'deleting this invalid config.'
                        )
                        os.remove(profile_file_path)
                    elif not isinstance(surface_value, int):
                        logger.info(
                            f'[SETUP] {profile_file_name} contained key {configured_surface_name} in '
                            f'"control_surfaces" whose value was not an integer. '
                            f'deleting this invalid config.'
                        )
                        os.remove(profile_file_path)

    def create_profiles(self) -> None:
        print('')
        print('-'*60)
        print('Create Trim Tab Profiles')
        print('-'*60)
        print('')
        print('> each trim tab profile is a setting for each control surface')
        print('> associated with a name for that profile.')
        another_profile = None
        while another_profile != 'N':
            profile = self.create_profile()
            profile_path = os.path.join(PROFILES_DIR, f"{profile['username']}.yml")
            with open(profile_path, 'w') as profile_file:
                yaml.dump(
                    profile,
                    profile_file,
                    default_flow_style=False,
                    sort_keys=False
                )

            print('')
            print(f'File written: {profile_path}')
            print('')

            print('Would you like to create another profile?')
            print('  "y" -- Yes, I would like to create another profile.')
            print('  "N" -- No, I am happy with the profiles already created.')
            print('')
            another_profile = input('>>> ')
            if another_profile in ('y', "N"):
                pass
            else:
                print('')
                print('!! please enter a valid response.')
                print('')

    def create_profile(self):
        accept_profile = None
        profile = None
        while accept_profile != 'y':
            profile = self.get_profile_values()
            print(' -- Review Profile --\n')
            print(f'\tname: {profile["name"]}')
            for control_surface_name, surface_value in profile["control_surfaces"].items():
                print(f'\t{control_surface_name}: {surface_value}')
            print('')
            print('Create this profile?')
            print('\t- "y" Yes, create this profile.')
            print('\t- "N" No, discard and try again.')
            while True:
                print('')
                accept_profile = input('>>> ')
                if accept_profile in ('y', 'N'):
                    break
                else:
                    print('')
                    print('!! invalid response, try again.')

        return profile

    def get_profile_values(self):
        """Get the values needed to create a profile from the user."""
        # get the name
        name = self.get_profile_name()
        return {
            'name': name,
            'username': name.lower().replace(' ', '_'),
            'control_surfaces': {
                control_surface_name: self.get_control_surface_value(control_surface_name)
                for control_surface_name in SetUpControlSurfaces.surface_names()
            }
        }

    def get_profile_name(self) -> str:
        """Get the new Profile Name from the User."""
        while True:
            print('')
            name = input('enter a name for this profile:')
            if name.upper() in self.names:
                print('')
                print('!! this name has already been entered for a profile.')
                print('!! enter a name you have not used yet.')
                continue
            elif not name.replace(' ', '').isalpha():
                print('')
                print('!! that is not a valid profile name.')
                print('!! use only letters and spaces.')
                print('!! please try again.')
                continue
            return name.upper()

    def get_control_surface_value(self, surface_name) -> int:
        while True:
            surface_value = input(f'enter {surface_name} integer value between 0 and 100 (inclusive): ')
            if '.' in surface_value:
                print('')
                print('!! only enter integer values')
            elif surface_value.strip().isdigit():
                return int(surface_value.strip())
            else:
                raise Exception('An unexpected situation was encountered.')


    def __init__(self) -> None:
        logger.info(f'[SETUP] checking {PROFILES_DIR}')
        self.validate_existing_profiles()
        self.names = []
        if self.setup_required:
            logger.info(f'[SETUP] at least one profile need to be configured.')
            self.create_profiles()


class SetUpConstants:
    config_path = os.path.join(CONFIG_DIR, 'constants.yml')

    @property
    def setup_required(self) -> bool:
        if not os.path.exists(self.config_path):
            logger.info(f'[SETUP] {self.config_path} does not exist.')
            return True

        try:
            constants = yaml.safe_load(open(self.config_path, 'r'))
        except Exception:
            logger.info(f'[SETUP] {self.config_path} could not be read as a yaml file, it will be deleted.')
            os.remove(self.config_path)
            return True
        else:
            if constants is None:
                logger.info(f'[SETUP] {self.config_path} is empty, it will be deleted.')
                return True

            expected_values = [
                ('full_extend_duration', float),
                ('full_retract_duration', float),
            ]
            for constant_name, constant_value_type in expected_values:
                if constant_name not in constants:
                    logger.info(f'[SETUP] definition of "{constant_name}" was missing, file will be deleted.')
                    return True
                elif not isinstance(constants[constant_name], constant_value_type):
                    logger.info(f'[SETUP] definition of "{constant_name}" was the wrong type, file will be deleted.')
                    return True

    def get_constants(self):
        while True:
            constants = {
                'full_extend_duration': self.create_float_constant('full_extend_duration'),
                'full_retract_duration': self.create_float_constant('full_retract_duration'),
            }
            print('\n' + ' Review Constants '.center(60, '-') + '\n')
            print('\nConstants:')
            for constant_name, constant_value in constants.items():
                print(f'\t- {constant_name}: {constant_value}')
            print('')
            print('Happy with these values?')
            print('\t- "y" Yes, proceed with these values.')
            print('\t- "N" No, discard and try again.')
            while True:
                print('')
                accept_constants = input('>>> ')
                if accept_constants == 'y':
                    return constants
                elif accept_constants != 'N':
                    print('\n!! invalid response, try again.\n')

    def create_float_constant(self, constant_name: str) -> float:
        while True:
            constant_value_str = input(f'Enter the value of "{constant_name}" to 2 decimal places: ')
            try:
                return float(constant_value_str)
            except Exception:
                print('!! enter a decimal')

    def __init__(self) -> None:
        logger.info(f'[SETUP] checking {self.config_path}')
        if self.setup_required:
            logger.info(f'[SETUP] configuration of constants is required.')
            with open(self.config_path, 'w') as constant_file:
                yaml.dump(
                    self.get_constants(),
                    constant_file,
                    default_flow_style=False,
                    sort_keys=False
                )
            print(f'\nFile written: {self.config_path}\n')
