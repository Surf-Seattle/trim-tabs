import os

from kivy.clock import Clock
from kivymd.uix.screen import MDScreen
from kivy.properties import (
    ObjectProperty,
)
from kivy.core.window import Window

from utils import utilities as u


class SurfRootScreen(MDScreen):
    # screen_manager = ObjectProperty()
    # navigation_bar = ObjectProperty()

    def __init__(self, *args, **kwargs):
        MDScreen.__init__(self, *args, **kwargs)
        Clock.schedule_once(self.globalize_screen_manager)
        if os.environ.get('FULLSCREEN', "true") != "true":
            Window.show_cursor = False

    def globalize_screen_manager(self, *args):
        self.screen_manager = [i for i in self.children[0].children if type(i).__name__ == 'ScreenManager'][0]
        self.navigation_bar = [i for i in self.children[0].children if type(i).__name__ == 'NavigationBar'][0]
        self.active_bar = [i for i in self.children[0].children if type(i).__name__ == 'ActiveBar'][0]
        self.active_bar.hide()