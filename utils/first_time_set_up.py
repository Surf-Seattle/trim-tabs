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
                if not all([set(x) == {'name', 'goofy'} for x in control_surfaces]):
                    logger.info(f'[SETUP] yaml file list of dicts did not contain the expected keys, set-up required.')
                    return True

    def __init__(self):
        logger.info(f'[SETUP] checking {self.control_surfaces_path}')
        if self.setup_required:
            control_surface_config = [
                {
                    'name': surface_name,
                    'goofy': goofy_surface
                }
                for surface_name, goofy_surface
                in self.create_control_surfaces()
            ]
            with open(self.control_surfaces_path, 'w') as control_surface_config_file:
                yaml.dump(
                    control_surface_config,
                    control_surface_config_file,
                    default_flow_style=False,
                    sort_keys=False
                )

            print('')
            print(f'File written: {self.control_surfaces_path}')
            print('')

    def create_control_surfaces(self):
        print('-'*60)
        print('Configure Control Surfaces'.center(60))
        print('-'*60)
        print('')
        accept_names = None
        while accept_names != 'y':
            surface_names = self.get_control_surface_names()

            if not surface_names:
                print('')
                print('!! you must configure at least 1 control surface.')
                print('')
                continue

            print('')
            print(' REVIEW SURFACE NAMES '.center(60, '-'))
            print('')
            print('You have entered the following control surface names:')
            for surface_name in surface_names:
                print(f'\t- {surface_name}')
            print('')
            print('Remember, order matters!')
            print('If you want to re-order the control surfaces, you will need to start over.')
            print('')
            print('Are you happy with the names as shown?')
            print('  "y" -- Yes, I am happy with these names.')
            print('  "N" -- No, I want to re-enter the control surface names.')
            print('')
            accept_names = input('>>> ')
            if accept_names in ('y', "N"):
                pass
            else:
                print('')
                print('!! please enter a valid response.')
                print('')

        accept_goofy = None
        while accept_goofy not in ('y', 'N'):
            goofy_names = self.get_goofy_control_surface_mapping(surface_names)
            print('')
            print(' REVIEW GOOFY MAPPING '.center(60, '-'))
            print('')
            print('You have created the following goofy mapping:')
            for name, goofy_name in zip(surface_names, goofy_names):
                print(f'\t {name} <--> {goofy_name}')
            print('')
            print('Are you happy with the mapping as shown?')
            print('  "y" -- Yes, I am happy with this mapping.')
            print('  "N" -- No, I want to re-enter the mapping values.')
            print('')
            accept_goofy = input('>>> ')
            if accept_goofy in ('y', 'N'):
                pass
            else:
                print('')
                print('!! please enter a valid response.')
                print('')

        return zip(surface_names, goofy_names)

    def get_control_surface_names(self):

        print('* each control surface represents a single trim tab')
        print('* enter the trim tabs in the order that you would like')
        print('  them to appear in the UI (from left to right).')

        i = 1
        control_surface_names = []
        while True:

            print('')
            print(f'Enter the name for a control surface #{i}')
            surface_name = input('>>> ')

            # no surface names with the same
            if not surface_name.isalpha():
                print('')
                print('!! This name is not valid.')
                print('!! Use ONLY letters.')
                print('!! No spaces or other characters allowed.')
            elif surface_name.upper() in control_surface_names:
                print('')
                print('!! This name has already been entered.')
                print('!! Please enter a new name for this control surface.')
            else:
                control_surface_names.append(surface_name.upper())
                i += 1
                print('')
                print('Would you like to add another control surface? [y/N]')
                more_surfaces = None
                while more_surfaces not in ('y', 'N'):
                    more_surfaces = input('>>> ')
                    if more_surfaces == 'N':
                        break
                    elif more_surfaces == 'y':
                        pass
                    else:
                        more_surfaces = None
                        print('')
                        print('!! Please enter either "y" or "N"')
                        print('!! "y" to add another control surface.')
                        print('!! "N" to not add additional control surfaces.')
                        print('')
                if more_surfaces == 'N':
                    break
        return control_surface_names

    def get_goofy_control_surface_mapping(self, control_surface_names):
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
        remaining_options = control_surface_names.copy()
        goofy_surface_names = []
        for control_surface_name in control_surface_names:
            while True:
                print('')
                print(f'Enter the goofy counterpart of: {control_surface_name}')
                print(f'choose from: {remaining_options}')
                goofy_name = input('>>> ')
                clean_goofy_name = goofy_name.upper().strip()
                if clean_goofy_name in remaining_options:
                    goofy_surface_names.append(clean_goofy_name)
                    remaining_options.remove(clean_goofy_name)
                    break
                else:
                    print('')
                    print(f'!! "{clean_goofy_name}" was not one of the valid options. try again.')
        return goofy_surface_names


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

        # get the name
        while True:

            print('')
            print('enter a name for this profile:')
            name = input('>>> ')
            if name.replace(' ', '').isalpha():
                break
            else:
                print('')
                print('!! that is not a valid profile name.')
                print('!! use only letters and spaces.')
                print('!! please try again.')

        username = name.lower().replace(' ', '_')

        # get the control surface values
        control_surface_values = {
            control_surface_name: None
            for control_surface_name in SetUpControlSurfaces.surface_names()
        }
        for surface_name in list(control_surface_values):
            while True:
                surface_value = input(f'enter {surface_name} integer value between 0 and 100 (inclusive): ')
                if '.' in surface_value:
                    print('')
                    print('!! only enter integer values')
                elif surface_value.strip().isdigit():
                    control_surface_values[surface_name] = int(surface_value.strip())
                    break
                else:
                    print(surface_value, type(surface_value))
        return {
            'name': name,
            'username': username,
            'control_surfaces': control_surface_values
        }

    def __init__(self) -> None:
        logger.info(f'[SETUP] checking {PROFILES_DIR}')
        self.validate_existing_profiles()
        if self.setup_required:
            logger.info(f'[SETUP] at least one profile need to be configured.')
            self.create_profiles()
