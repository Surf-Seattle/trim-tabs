from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import (
    NumericProperty,
    StringProperty,
    BooleanProperty,
    DictProperty
)

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.screen import MDScreen

from utils import (
    logger,
    utilities as u
)

from utils.controller import controller, Surface


class SurfActiveScreen(MDScreen):
    username = StringProperty()

    def __init__(self, *args, **kwargs):
        logger.debug('[UI] Initializing: ActiveScreen')
        MDScreen.__init__(self, *args, **kwargs)
        Clock.schedule_once(self.post_init)

    def post_init(self, *args, **kwargs):
        self.ids.control_panel.disable_controls()

    def activate(self, username: str, profile_list_item) -> None:
        """Enable Controls, Set values to those of a given profile."""
        # username
        self.list_item = profile_list_item

        # update the Control Panel
        self.ids.control_panel.enable_controls(username)
        u.get_root_screen(self).active_bar.show()

    def on_pre_leave(self):
        """Disable Controls, Set values to 'Off'."""
        logger.info('SurfActiveScreen.on_pre_leave.begin')
        if not controller.active_profile:
            self.ids.control_panel.disable_controls()
        logger.info('SurfActiveScreen.on_pre_leave.end')

    @property
    def username(self) -> None:
        return controller.active_profile


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
        self.column_count = len(controller.surface_display_order)
        for control_surface_name in controller.surface_display_order:
            logger.info(f'[UI] Adding "{control_surface_name}" TabControl to ControlPanel.')
            tab_control = TabControl(id=control_surface_name)
            self.tab_control_ids[control_surface_name] = tab_control
            self.ids.interactive_controls.add_widget(tab_control)

    def disable_controls(self) -> None:
        """Disable the ActiveScreen controls."""
        logger.info('ControlPanel.disable_controls.begin')
        if self.tab_control_ids:
            for surface_name in controller.surface_names:
                self.tab_control_ids[surface_name].disable_both()
                self.tab_control_ids[surface_name].display_value("·")

        logger.info('ControlPanel.disable_controls.end')

    def enable_controls(self, username: str) -> None:
        """Enable the ActiveScreen controls with values from a WaveProfile yaml file."""
        for surface_name, surface_value in controller.activate_profile(username).items():
            self.tab_control_ids[surface_name].value = surface_value

    def invert(self) -> None:
        """Mirror the Controls, either `Goofy` or `Regular` was pressed."""
        logger.info("----- Invert Pressed -----")
        for surface_name, surface_value in controller.invert().items():
            self.tab_control_ids[surface_name].value = surface_value


class TabControl(MDBoxLayout):
    id = StringProperty()
    _value = NumericProperty()
    value = NumericProperty()
    display = StringProperty()
    max = NumericProperty()
    min = NumericProperty()

    def __init__(self, **kwargs):
        super().__init__()
        self.id = kwargs['id']
        self.value = -2
        self.max = 100
        self.min = 0
        self._value = -1

    def increment(self, *args) -> None:
        logger.info("----- Increment Pressed -----")
        self.value = controller.surfaces[self.id].increment()
        print(controller.values.get(self.id, -1))

    def decrement(self, *args) -> None:
        logger.info("----- Decrement Pressed -----")
        self.value = controller.surfaces[self.id].decrement()
        print(controller.values.get(self.id, -1))

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        if new_value < self.min:
            self.disable_decrement()
        elif new_value == self.min:
            self._value = new_value
            self.disable_decrement()
        elif new_value > self.max:
            self.disable_increment()
        elif new_value == self.max:
            self._value = new_value
            self.disable_increment()
        else:
            self._value = new_value
            self.enable_both()

        self.ids.control_surface_value.text = str(int(self._value))

    def display_value(self, display_value) -> None:
        self.ids.control_surface_value.text = display_value

    def disable_increment(self) -> None:
        logger.debug(f'[UI]\t"{self.id}" Controls: Disabling Increment, Enabling Decrement')
        self.ids.increment_control.disabled = True
        self.ids.decrement_control.disabled = False

    def disable_decrement(self) -> None:
        logger.debug(f'[UI]\t"{self.id}" Controls: Disabling Decrement, Enabling Increment')
        self.ids.decrement_control.disabled = True
        self.ids.increment_control.disabled = False

    def disable_both(self) -> None:
        logger.debug(f'[UI]\t"{self.id}" Controls: Disabling Decrement, Disabling Increment')
        self.ids.increment_control.disabled = True
        self.ids.decrement_control.disabled = True

    def enable_both(self) -> None:
        logger.debug(f'[UI]\t"{self.id}" Controls: Enabling Decrement, Enabling Increment')
        self.ids.increment_control.disabled = False
        self.ids.decrement_control.disabled = False


