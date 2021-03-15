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


class ActiveBar(ThemableBehavior, MDBoxLayout):
    are_we_goofy = BooleanProperty(False)
    profile_name = StringProperty()

    def toggle_goofy(self) -> None:
        if self.are_we_goofy:
            self.enable_goofy()
        else:
            self.disable_goofy()

    def enable_goofy(self) -> None:
        logger.info('[UI] Enabling Goofy')
        self.are_we_goofy = True
        self.ids.goofy_button.icon = 'toggle-switch'
        self.ids.goofy_button.text = 'Un Goofy'
        self.parent.ids.control_panel.goofy_values()

    def disable_goofy(self) -> None:
        logger.info('[UI] Disabling Goofy')
        self.are_we_goofy = False
        self.ids.goofy_button.icon = 'toggle-switch-off'
        self.ids.goofy_button.text = 'Get Goofy'
        self.parent.ids.control_panel.goofy_values()

    def refresh_save_button(self) -> None:
        if self.parent.ids.control_panel.initial_values:
            if self.parent.ids.control_panel.initial_values == self.parent.ids.control_panel.current_values:
                self.disable_save_changes()
            else:
                self.enable_save_changes()

    def enable_save_changes(self) -> None:
        logger.debug('[UI]\tEnabling "Save Changes"')
        self.ids.save_changes_button.disabled = False

    def disable_save_changes(self) -> None:
        logger.debug('[UI]\tDisabling "Save Changes"')
        self.ids.save_changes_button.disabled = True

    def save_changes(self):
        logger.debug('[UI] Save Changes Clicked, Saving Changes...')
        u.Profile(username=self.parent.username).update({
            'control_surfaces': self.parent.ids.control_panel.current_values,
            'goofy': self.are_we_goofy,
        })
        self.parent.ids.control_panel.reset_initial_values()
        self.refresh_save_button()
        self.parent.list_item.update_values(self.parent.ids.control_panel.current_values)

    def retract(self):
        """The Retract Button in the ActiveBar was pressed."""
        logger.debug('[UI] Retract Clicked, Retracting Tabs...')
        u.get_root_screen(self).screen_manager.get_screen("ACTIVE").deactivate()  # disable active screen controls
        u.get_root_screen(self).navigation_bar.set_current(0)  # shift nav-bar to PROFILES tab
        u.get_root_screen(self).screen_manager.current = "PROFILES"  # shift to the active profiles screen
        u.get_root_screen(self).screen_manager.get_screen("ACTIVE").list_item.deactivate()  # deactivate the list item
        self.hide()  # hide the ActiveBar

    def hide(self):
        u.hide_widget(self)

    def show(self, config):
        logger.info(f'config = {config}')
        self.profile_name = config['name']
        u.hide_widget(self, dohide=False)
