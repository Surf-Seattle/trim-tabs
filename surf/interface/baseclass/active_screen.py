from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import (
    NumericProperty,
    StringProperty,
    BooleanProperty,
    DictProperty
)

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import GridLayout
from kivymd.uix.screen import MDScreen

import utilities as u
from log import logger
from .tab_navigation import NavigationBar


class SurfActiveScreen(MDScreen):
    username = StringProperty()

    def __init__(self, *args, **kwargs):
        logger.debug('[UI] Initializing: ActiveScreen')
        MDScreen.__init__(self, *args, **kwargs)
        Clock.schedule_once(self.post_init)

    def post_init(self, *args, **kwargs):

        # shortcuts
        # self.ui_notes = self.ids.notes.ids.notes
        self.ui_retract = self.ids.buttons.ids.retract_button
        self.ui_goofy = self.ids.buttons.ids.goofy_button
        self.ui_save_changes = self.ids.buttons.ids.save_changes_button
        self.deactivate()

    def activate(self, username: str, profile_list_item) -> None:
        """Enable Controls, Set values to those of a given profile."""
        # username
        self.username = username
        self.list_item = profile_list_item

        # update the button controls
        self.ui_retract.disabled = False
        self.ui_goofy.disabled = False
        self.ids.buttons.refresh_save_button()

        config = u.Profile.read_config(username=username)

        # update the Control Panel
        self.ids.control_panel.enable_controls(config['control_surfaces'])
        if config['goofy']:
            self.ids.buttons.disable_goofy()
        else:
            self.ids.buttons.enable_goofy()

    def deactivate(self) -> None:
        """Disable Controls, Set values to 'Off'."""
        self.username = ''
        # update the notes input
        # self.ui_notes.disabled = True
        # self.ui_notes.hint_text = "No Wave Profile is currently active. Activate a wave profile to begin."
        # update the button controls
        self.ui_retract.disabled = True
        self.ui_goofy.disabled = True
        self.ui_save_changes.disabled = True
        self.ui_save_changes.disabled = True
        # update the Control Panel
        self.ids.control_panel.disable_controls()


class ControlPanel(BoxLayout):
    tabs_rendered = BooleanProperty(False)
    column_count = NumericProperty()
    tab_control_ids = DictProperty({})
    initial_values = DictProperty({})

    def __init__(self, *args, **kwargs):
        logger.debug('[UI] Initializing: ActiveScreen.TabControls')
        BoxLayout.__init__(self, *args, **kwargs)
        Clock.schedule_once(self.create_controls)

    def create_controls(self, *args, **kwargs) -> None:
        logger.debug('[UI] ActiveScreen.TabControls: creating tab controls...')
        config = u.Configuration()
        self.column_count = len(config.control_surfaces)

        for control_surface_name in config.control_surfaces_attribute('name')[::-1]:
            logger.info(f'[UI] Adding "{control_surface_name}" TabControl to ControlPanel.')
            tab_control = TabControl(
                id=control_surface_name,
                screen=self,
                value=0,
            )
            self.tab_control_ids[control_surface_name] = tab_control
            self.ids.interactive_controls.add_widget(tab_control)

    def disable_controls(self) -> None:
        for tab_control_widget in self.tab_control_ids.values():
            tab_control_widget.disable()

    def enable_controls(self, tab_values: dict) -> None:
        if not self.initial_values:
            self.initial_values = tab_values

        for tab_control_name, tab_control_widget in self.tab_control_ids.items():
            tab_control_widget.set_value(tab_values[tab_control_name])

    def reset_initial_values(self) -> None:
        logger.debug(f'[UI] ControlPanel.initial_values reset to: {self.current_values}')
        self.initial_values = self.current_values

    def goofy_values(self) -> None:
        current_values = self.current_values.copy()
        for current_name, goofy_name in u.Configuration().goofy_map.items():
            self.tab_control_ids[goofy_name].set_value(current_values[current_name])


    @property
    def current_values(self) -> dict:
        return {
            tab_control_name: tab_control_widget.get_value()
            for tab_control_name, tab_control_widget in self.tab_control_ids.items()
        }


class TabControl(MDBoxLayout):
    id = StringProperty()
    value = NumericProperty()
    display = StringProperty()
    max = NumericProperty()
    min = NumericProperty()

    def __init__(self, **kwargs):
        super().__init__()
        self.id = kwargs['id']
        self.screen = kwargs['screen']
        self.ids.control_surface_value.text = str(int(kwargs['value']))
        self.min = 0
        self.max = 100

    @property
    def prevent_increment(self) -> bool:
        return self.get_value() == self.max or self.get_value() + 5 > self.max

    @property
    def prevent_decrement(self) -> bool:
        return self.get_value() == self.min or self.get_value() - 5 < self.min

    def increment(self, *args) -> None:
        if self.prevent_increment:
            logger.debug('')
            logger.info(f'[UI] Prevented Incrementing "{self.id}", {self.get_value()} is too high.')
        else:
            logger.debug('')
            logger.debug(f"[UI] Incrementing '{self.id}' value.")
            self.set_value(self.get_value() + 5)
            active_screen = self.parent.parent.parent.parent.parent.parent
            active_screen.ids.buttons.refresh_save_button()

    def decrement(self, *args) -> None:
        if self.prevent_decrement:
            logger.debug('')
            logger.info(f'[UI] Prevented Decrementing "{self.id}", {self.get_value()} is too low.')
        else:
            logger.debug('')
            logger.debug(f"[UI] Decrementing '{self.id}' value.")
            self.set_value(self.get_value() - 5)
            active_screen = self.parent.parent.parent.parent.parent.parent
            active_screen.ids.buttons.refresh_save_button()

    def disable(self) -> None:
        """Disable This """
        self.set_value("0")
        self.disable_increment()

    def set_value(self, new_value) -> None:
        logger.info(f"[UI] Updating '{self.id}' value from '{self.get_value()}' to '{new_value}'")
        self.ids.control_surface_value.text = str(int(new_value))
        self.refresh_controls()

    def get_value(self) -> None:
        return int(self.ids.control_surface_value.text)

    def refresh_controls(self) -> None:
        if self.prevent_increment:
            logger.debug(f'[UI] Reached or Exceeded "{self.id}" Maximum Value')
            self.disable_increment()
            self.enable_decrement()
        elif self.prevent_decrement:
            logger.debug(f'[UI] Reached or Subverted "{self.id}" Minimum Value')
            self.disable_decrement()
            self.enable_increment()
        else:
            logger.debug(f'[UI] Neither "{self.id}" Limit Activated')
            self.enable_decrement()
            self.enable_increment()

    def disable_increment(self) -> None:
        logger.debug(f'[UI]\tDisabling "{self.id}" Increment Button')
        self.ids.increment_control.disabled = True

    def disable_decrement(self) -> None:
        logger.debug(f'[UI]\tDisabling "{self.id}" Decrement Button')
        self.ids.decrement_control.disabled = True

    def enable_increment(self) -> None:
        logger.debug(f'[UI]\tEnabling "{self.id}" Increment Button')
        self.ids.increment_control.disabled = False

    def enable_decrement(self) -> None:
        logger.debug(f'[UI]\tEnabling "{self.id}" Decrement Button')
        self.ids.decrement_control.disabled = False


class ActionButtons(MDBoxLayout):
    are_we_goofy = BooleanProperty(False)

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
        logger.debug('[UI] Retract Clicked, Retracting Tabs...')

        # disable the controls of the ACTIVE tab
        self.parent.deactivate()

        # shift the navigation bar over to the PROFILES tab
        navbar_in_boxlayout = self.parent.parent.parent
        nav_bar = [i for i in navbar_in_boxlayout.children if isinstance(i, NavigationBar)][0]
        nav_bar.set_current(0)

        # have the screenmanager switch to the ACTIVE sheet
        screen_manager = self.parent.parent
        print(f"screen_manager.children = {screen_manager.children}")
        screen_manager.current = "PROFILES"

        # Reset the text of the button on this surf_list_item which that this ACTIVE screen had been running on
        self.parent.list_item.deactivate()
