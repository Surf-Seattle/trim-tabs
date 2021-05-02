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
from .tab_navigation import NavigationBar

from utils import (
    controller,
    logger,
    utilities as u
)


class SurfActiveScreen(MDScreen):
    username = StringProperty()

    def __init__(self, *args, **kwargs):
        logger.debug('[UI] Initializing: ActiveScreen')
        MDScreen.__init__(self, *args, **kwargs)
        Clock.schedule_once(self.post_init)

    def post_init(self, *args, **kwargs):
        self.deactivate()

    def activate(self, username: str, profile_list_item) -> None:
        """Enable Controls, Set values to those of a given profile."""
        # username
        self.username = username
        self.list_item = profile_list_item

        # update the Control Panel
        self.ids.control_panel.enable_controls(username)
        u.get_root_screen(self).active_bar.show()

    def deactivate(self) -> None:
        """Disable Controls, Set values to 'Off'."""
        self.username = ''
        # update the Control Panel
        self.ids.control_panel.disable_controls()


class ControlPanel(BoxLayout):
    tabs_rendered = BooleanProperty(False)
    column_count = NumericProperty()
    tab_control_ids = DictProperty({})
    initial_values = DictProperty({})
    profile_name = StringProperty()

    def __init__(self, *args, **kwargs):
        logger.debug('[UI] Initializing: ActiveScreen.TabControls')
        BoxLayout.__init__(self, *args, **kwargs)
        Clock.schedule_once(self.create_controls)

    def create_controls(self, *args) -> None:
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

        self.controller = controller.Controller()

    def disable_controls(self) -> None:
        """Disable the ActiveScreen controls."""
        self.profile_name = ''
        for tab_control_widget in self.tab_control_ids.values():
            tab_control_widget.disable()

        if hasattr(self, 'controller'):
            self.controller.retract_pins(blindly=True)

    def enable_controls(self, username: str) -> None:
        """Enable the ActiveScreen controls with values from a WaveProfile yaml file."""
        config = u.Profile.read_config(username=username)

        if not self.initial_values:
            self.initial_values = config['control_surfaces']

        self.profile_name = config['name']
        for tab_control_name, tab_control_widget in self.tab_control_ids.items():
            tab_control_widget.set_value(config['control_surfaces'][tab_control_name])

        self.controller.move_to(
            {
                tab_control_name: config['control_surfaces'][tab_control_name]
                for tab_control_name, tab_control_widget in self.tab_control_ids.items()
            }
        )

    def invert(self) -> None:
        """Mirror the Controls, either `Goofy` or `Regular` was pressed."""
        current_values = self.current_values.copy()
        for current_name, goofy_name in u.Configuration().goofy_map.items():
            self.tab_control_ids[goofy_name].set_value(current_values[current_name])
        self.controller.invert()

    @property
    def current_values(self) -> dict:
        """The current values of the ActiveScreen controls."""
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
            u.get_root_screen(self).active_bar.refresh()
            self.disable_increment()
            self.screen.controller.surfaces[self.id].increment()
            self.enable_increment()

    def decrement(self, *args) -> None:
        if self.prevent_decrement:
            logger.debug('')
            logger.info(f'[UI] Prevented Decrementing "{self.id}", {self.get_value()} is too low.')
        else:
            logger.debug('')
            logger.debug(f"[UI] Decrementing '{self.id}' value.")
            self.set_value(self.get_value() - 5)
            u.get_root_screen(self).active_bar.refresh()
            self.disable_decrement()
            self.screen.controller.surfaces[self.id].decrement()
            self.enable_decrement()

    def disable(self) -> None:
        """Disable This """
        self.set_value("0")
        self.disable_increment()

    def set_value(self, new_value) -> None:
        logger.info(f"[UI] Updating '{self.id}' value from '{self.get_value()}' to '{new_value}'")
        self.ids.control_surface_value.text = str(int(new_value))
        self.refresh_controls()
        self.screen.controller.surfaces[self.id].move_to(new_value/100)

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



