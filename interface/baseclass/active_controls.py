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
        if not self.default_y_position:
            self.default_y_position = self.y

        self.refresh()
        self.ids.retract_button.disabled = False
        self.y = self.default_y_position
        # u.hide_widget(self, dohide=False)

    def hide(self):
        """Show the ActiveBar widget when the tabs are retracted."""
        self.y = 5000
        # u.hide_widget(self)

    def refresh(self) -> None:
        """
        Update the Active Profile Name and Enable or Disable the Goofy and Regular Buttons.
        Attributes of the ACTIVE screen control_panel are used to refresh the ActiveBar
        """
        # self.md_bg_color = "#ffd54f"
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
        logger.debug('STEP -1: updating the satusbar')
        self.profile_name = "wait..."
        self.ids.goofy_button.disabled = True
        self.ids.regular_button.disabled = True
        self.ids.retract_button.disabled = True
        self.ids.goofy_button.md_bg_color = self.ids.goofy_button.md_bg_color[:3] + [0]

        logger.debug('STEP 0: setting active screen `deactivating` to True')
        u.get_root_screen(self).screen_manager.get_screen("ACTIVE").deactivating = True
        logger.debug('STEP 1')
        u.get_root_screen(self).navigation_bar.set_current(0)  # shift nav-bar to PROFILES tab
        logger.debug('STEP 2')
        u.get_root_screen(self).screen_manager.current = "PROFILES"  # shift to the active profiles screen
        logger.debug('STEP 3')
        u.get_root_screen(self).screen_manager.get_screen("ACTIVE").list_item.deactivate()  # deactivate the list item
        logger.debug('[UI] Retract Complete.')




