from kivymd.theming import ThemableBehavior
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import (
    BooleanProperty,
    StringProperty,
)

from utils import (
    logger,
    utilities as u
)

from utils.controller import controller


class ActiveBar(ThemableBehavior, MDBoxLayout):
    profile_name = StringProperty()

    def show(self):
        """Show the ActiveBar widget when a profile is activated."""
        self.refresh()
        u.hide_widget(self, dohide=False)

    def hide(self):
        """Show the ActiveBar widget when the tabs are retracted."""
        u.hide_widget(self)

    def refresh(self) -> None:
        """
        Update the Active Profile Name and Enable or Disable the Goofy and Regular Buttons.
        Attributes of the ACTIVE screen control_panel are used to refresh the ActiveBar
        """
        self.profile_name = controller.active_profile
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
        """The Goofy or Regular Button in the ActiveBar was pressed."""
        u.get_root_screen(self).screen_manager.get_screen("ACTIVE").ids.control_panel.invert()
        self.refresh()

    def retract(self):
        """The Retract Button in the ActiveBar was pressed."""
        logger.debug('[UI] Retract Clicked, Retracting Tabs...')
        u.get_root_screen(self).screen_manager.get_screen("ACTIVE").deactivate()  # disable active screen controls
        u.get_root_screen(self).navigation_bar.set_current(0)  # shift nav-bar to PROFILES tab
        u.get_root_screen(self).screen_manager.current = "PROFILES"  # shift to the active profiles screen
        u.get_root_screen(self).screen_manager.get_screen("ACTIVE").list_item.deactivate()  # deactivate the list item
        self.hide()  # hide the ActiveBar
        controller.deactivate_profile()




