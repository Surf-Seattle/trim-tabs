from kivy.clock import Clock
from kivy.uix.behaviors import ButtonBehavior
from kivy.properties import (
    ColorProperty,
    StringProperty,
    NumericProperty,
    BooleanProperty
)

from kivymd.theming import ThemableBehavior
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog

from utils import (
    logger,
    utilities as u
)
from interface.baseclass.profiles_screen_dialogues import EditProfileDialogue

from .tab_navigation import NavigationBar
from .active_screen import SurfActiveScreen


class SurfListItem(ThemableBehavior, ButtonBehavior, MDBoxLayout):
    name = StringProperty()
    note = StringProperty()
    port_value = NumericProperty()
    center_value = NumericProperty()
    starboard_value = NumericProperty()
    bar_color = ColorProperty((1, 0, 0, 1))
    activate_clicked = BooleanProperty(False)

    def __init__(self, **kwargs):
        logger.info(f'[UI] Initializing ProfilesScreen.ListItem: {kwargs["id"]}')
        super().__init__()
        self.id = kwargs['id']
        self.screen = kwargs['screen']
        self.name = kwargs['name']
        self.username = u.Profile.get_username(kwargs['name'])
        self.port_value = kwargs['port_value']
        self.center_value = kwargs['center_value']
        self.starboard_value = kwargs['starboard_value']
        self._dialogue = None

    def event_handler(self) -> None:
        if self.activate_clicked:
            self.activate_clicked = False
            self.activate()
        else:
            self.show_dialogue()

        # Reset Indicators
        self.activate_clicked = False

    def activate_handler(self) -> None:
        logger.info(f'[UI] Activate Profile: "{self.name}"')
        self.activate_clicked = True

    def activate(self) -> None:

        print(Clock.max_iteration)
        # shift the navigation bar over to the "active" tab
        navbar_in_boxlayout = self.parent.parent.parent.parent.parent
        nav_bar = [i for i in navbar_in_boxlayout.children if isinstance(i, NavigationBar)][0]
        nav_bar.set_current(1)

        # have the screenmanager switch to the active sheet
        screen_manager = self.parent.parent.parent.parent
        screen_manager.current = "ACTIVE"

        active_profile_screen = [i for i in screen_manager.children if isinstance(i, SurfActiveScreen)][0]

        active_profile_screen.activate(
            self.username,
            self,
        )

        # UPDATE "START"" BUTTON TO "STOP"
        self.parent.parent.parent.set_all_list_item_buttons('START')
        self.parent.parent.parent.set_one_list_item_buttons(self.username, 'STOP')

    def deactivate(self) -> None:
        self.ids.activate_button.text = 'START'

    def update_values(self, tab_control_values: dict) -> None:
        self.port_value = str(int(tab_control_values['PORT']))
        self.center_value = str(int(tab_control_values['CENTER']))
        self.starboard_value = str(int(tab_control_values['STARBOARD']))

    @property
    def dialogue(self):
        if not self._dialogue:
            self._dialogue = MDDialog(
                title=f"{self.name}",
                type="custom",
                content_cls=EditProfileDialogue(
                    username=self.username
                ),
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        on_release=self.close_dialogue
                    ),
                    MDFlatButton(
                        text="DELETE",
                        on_release=self.delete_profile
                    ),
                    MDFlatButton(
                        text="SAVE CHANGES",
                        on_release=self.save_profile
                    ),
                ],
            )
        return self._dialogue


    def show_dialogue(self, *args):
        logger.debug(f'[UI] "{self.name}" Edit-Dialogue: Showing')
        self.dialogue.open()

    def close_dialogue(self, *args):
        logger.debug(f'[UI] "{self.name}" Edit-Dialogue: Closing')
        self.dialogue.dismiss(force=True)

    def delete_profile(self, *args):
        logger.debug(f'[UI] "{self.name}" Edit-Dialogue: Delete-Profile-Clicked')
        u.Profile(username=self.username).delete()
        self.dialogue.dismiss(force=True)
        self.screen.refresh_visible_profiles()

    def save_profile(self, *args):
        logger.debug(f'[UI] "{self.name}" Edit-Dialogue: Save-Profile-Clicked')
        surfaces = self.dialogue.content_cls.slider_values
        u.Profile(username=self.username).update({'control_surfaces': surfaces})
        self.port_value = surfaces['PORT']
        self.center_value = surfaces['CENTER']
        self.starboard_value = surfaces['STARBOARD']
        self.close_dialogue()



