from kivy.properties import BooleanProperty

from kivymd.app import MDApp
from kivymd.uix.list import OneLineListItem
from kivymd.uix.screen import MDScreen

from utils import logger
from utils.controller import controller


class SurfSettingsScreen(MDScreen):
    list_created = BooleanProperty(False)

    def __init__(self, *args, **kwargs):
        logger.debug('[UI] Initializing: SettingsScreen')
        MDScreen.__init__(self, *args, **kwargs)

    def on_pre_enter(self):
        if not self.list_created:
            items = [
                ("Power Off", self.shut_down)
            ]
            for display_text, callback in items:
                list_item = OneLineListItem(
                    text=display_text,
                    divider="Inset",
                    font_style="H6",
                    on_release=callback,
                    theme_text_color="Custom",
                    text_color=[156, 0, 0, 0]
                )
                self.ids._list.add_widget(list_item)

            self.list_created = True

    def shut_down(self, *args):
        logger.info('UI: Shutting Down')
        controller.deactivate_profile()
        MDApp.get_running_app().stop()
