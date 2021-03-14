from kivy.properties import BooleanProperty

from kivymd.app import MDApp
from kivymd.uix.list import OneLineListItem
from kivymd.uix.screen import MDScreen

from log import logger


class SurfSettingsScreen(MDScreen):
    list_created = BooleanProperty(False)

    def __init__(self, *args, **kwargs):
        logger.debug('[UI] Initializing: SettingsScreen')
        MDScreen.__init__(self, *args, **kwargs)

    def on_pre_enter(self):
        if not self.list_created:
            items = [
                "Configure Control Surfaces",
                "Power Off",
            ]
            for i in items:
                list_item = OneLineListItem(
                    text=i, divider="Inset", font_style="H6"
                )
                list_item.bind(on_release=self.shut_down if i == 'Power Off' else self.configure_control_surfaces)
                self.ids._list.add_widget(list_item)

            self.list_created = True

    def configure_control_surfaces(self, obj):
        logger.info('UI: Configure Control Surfaces: THIS DOESNT DO ANYTHING YET')

    def shut_down(self, *args):
        logger.info('UI: Shutting Down')
        MDApp.get_running_app().stop()
