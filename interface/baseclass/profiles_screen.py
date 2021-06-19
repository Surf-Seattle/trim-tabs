from kivy.clock import Clock
from kivy.properties import (
    ObjectProperty,
    BooleanProperty,
    StringProperty,
    NumericProperty
)

from kivymd.uix.screen import MDScreen

from utils import (
    logger,
    utilities as u,
)
from utils.controller import controller

from interface.baseclass.profiles_screen_list_item import SurfListItem


class SurfProfilesScreen(MDScreen):
    list_created = BooleanProperty(False)
    selected_profile_username = None
    app = ObjectProperty()
    pressed = None

    def __init__(self, *args, **kwargs):
        logger.debug('[UI] Initializing: ProfilesScreen')
        MDScreen.__init__(self, *args, **kwargs)
        Clock.schedule_once(self.refresh_visible_profiles)

    def on_pre_enter(self):
        if controller.active_profile:
            controller.deactivate_profile()

    def refresh_visible_profiles(self, *args, **kwargs):
        logger.info('[UI] Refreshing Visible Profiles')
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


    def set_all_list_item_buttons(self, button_text: str) -> None:
        for profile_list_item in self.ids._list.ids:
            profile_list_item.ids.activate_button.text = button_text
