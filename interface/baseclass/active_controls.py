from kivymd.theming import ThemableBehavior
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import (
    BooleanProperty,
    StringProperty,
    NumericProperty
)

from utils import (
    logger,
    utilities as u
)

from utils.controller import controller


class ActiveBar(ThemableBehavior, MDBoxLayout):
    profile_name = StringProperty()
    default_y_position = NumericProperty()

    def show(self):
        """Show the ActiveBar widget when a profile is activated."""
        self.profile_name = "wait..."
        self.ids.goofy_button.disabled = True
        self.ids.regular_button.disabled = True
        self.ids.retract_button.disabled = True
        u.hide_widget(self, dohide=False)

    def hide(self):
        """Show the ActiveBar widget when the tabs are retracted."""
        u.hide_widget(self)

    def refresh(self) -> None:
        """
        Update the Active Profile Name and Enable or Disable the Goofy and Regular Buttons.
        Attributes of the ACTIVE screen control_panel are used to refresh the ActiveBar
        """
        self.ids.retract_button.disabled = False
        self.profile_name = controller.active_profile
        logger.info(controller.values)
        if controller.values['PORT'] > controller.values['STARBOARD']:
            self.ids.regular_button.disabled = True
            self.ids.goofy_button.disabled = False
        elif controller.values['PORT'] < controller.values['STARBOARD']:
            self.ids.regular_button.disabled = False
            self.ids.goofy_button.disabled = True
        else:
            self.ids.regular_button.disabled = True
            self.ids.goofy_button.disabled = True

    def invert(self) -> None:
        """The Invert Button in the ActiveBar was pressed."""
        u.get_root_screen(self).screen_manager.get_screen("ACTIVE").ids.control_panel.invert()
        self.refresh()

    def update_profile(self) -> None:
        """The Save Button in the ActiveBar was pressed"""
        u.get_root_screen(self).screen_manager.get_screen("ACTIVE").ids.control_panel.update_profile()
        self.refresh()

    def retract(self):
        """The Retract Button in the ActiveBar was pressed."""
        logger.debug('[UI] Retract Clicked, Retracting Tabs...')
        self.profile_name = "wait..."
        self.ids.goofy_button.disabled = True
        self.ids.regular_button.disabled = True
        self.ids.retract_button.disabled = True
        # TODO: would love to change the color of the active bar during retracting
        # TODO: would love the buttons to be invisible during this period
        #       i tried but could figure it out

        # by setting this `deactivating` it will trigger behavior on the `on_enter` of the active screen
        u.get_root_screen(self).screen_manager.get_screen("ACTIVE").deactivating = True

        u.get_root_screen(self).navigation_bar.set_current(0)  # shift nav-bar to PROFILES tab
        u.get_root_screen(self).screen_manager.current = "PROFILES"  # shift to the active profiles screen
        u.get_root_screen(self).screen_manager.get_screen("ACTIVE").list_item.deactivate()  # deactivate the list item




