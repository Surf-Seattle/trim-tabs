from kivy.clock import Clock
from kivy.properties import (
    ObjectProperty,
    BooleanProperty,
    StringProperty,
    NumericProperty
)

from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog

from utils import (
    logger,
    utilities as u
)

from interface.baseclass.profiles_screen_list_item import SurfListItem
from interface.baseclass.profiles_screen_dialogues import EditProfileDialogue, AddProfileDialogue


class SurfProfilesScreen(MDScreen):
    _active_dialogue = None
    _profile_dialogue = None
    _add_profile_dialogue = None
    list_created = BooleanProperty(False)
    selected_profile_username = None
    app = ObjectProperty()
    pressed = None

    def __init__(self, *args, **kwargs):
        logger.debug('[UI] Initializing: ProfilesScreen')
        MDScreen.__init__(self, *args, **kwargs)
        Clock.schedule_once(self.refresh_visible_profiles)

    def refresh_visible_profiles(self, *args, **kwargs):
        logger.info('[UI] Refreshing Visible Profiles')
        print('u.Profile.read_configs()')
        print(list(u.Profile.read_configs()))
        configured_usernames = {profile['username'] for profile in u.Profile.read_configs()}
        visible_usernames = {c.id for c in self.ids._list.children}

        for add_username in configured_usernames - visible_usernames:
            logger.debug(f'[UI] Adding Visible Profile: {add_username}')
            profile = u.Profile.read_config(username=add_username)
            profile_item = SurfListItem(
                id=profile['username'],
                screen=self,
                name=profile['name'],
                port_value=profile['control_surfaces']['PORT'],
                center_value=profile['control_surfaces']['CENTER'],
                starboard_value=profile['control_surfaces']['STARBOARD'],
            )
            self.ids._list.add_widget(profile_item)

        for remove_username in visible_usernames - configured_usernames:
            logger.debug(f'[UI] Removing Visible Profile: {remove_username}')
            self.ids._list.remove_widget([c for c in self.ids._list.children if c.id == remove_username][0])

    def get_add_profile_dialogue(self):
        return MDDialog(
            title=f"New Surf Profile",
            type="custom",
            content_cls=AddProfileDialogue(),
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=self.add_profile_dialogue_close
                ),
                MDFlatButton(
                    text="CREATE",
                    on_release=self.add_profile_dialogue_save
                ),
            ],
        )

    def add_profile_dialogue_show(self, *args):
        logger.info('UI: Add Profile Dialogue: SHOW')
        self._add_profile_dialogue = self.get_add_profile_dialogue()
        self._add_profile_dialogue.open()

    def add_profile_dialogue_close(self, *args):
        logger.info('UI: Add Profile Dialogue: CLOSE')
        self._add_profile_dialogue.dismiss(force=True)

    def add_profile_dialogue_save(self, *args):
        logger.info('UI: Add Profile Dialogue: SAVE')
        name = self._add_profile_dialogue.content_cls.ids.name.text
        control_surfaces = self._add_profile_dialogue.content_cls.slider_values
        u.Profile(name).create(control_surfaces)
        self.refresh_visible_profiles()
        self._add_profile_dialogue.dismiss(force=True)

    def set_all_list_item_buttons(self, button_text: str) -> None:
        for profile_list_item in self.ids._list.ids:
            profile_list_item.ids.activate_button.text = button_text

    def set_one_list_item_buttons(self, username: str, button_text: str) -> None:
        for profile_list_item in self.ids._list.children:
            logger.debug(f'checking profile_list_item with username = "{profile_list_item.username}"')
            if profile_list_item.username == username:
                profile_list_item.ids.activate_button.text = button_text
                break
        else:
            logger.warning(f"[UI] profile_list_item with username = '{username}' not found.")
