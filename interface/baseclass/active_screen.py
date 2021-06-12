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
        self.column_count = len(controller.surface_display_order)
        for control_surface_name in controller.surface_display_order:
            logger.info(f'[UI] Adding "{control_surface_name}" TabControl to ControlPanel.')
            tab_control = TabControl(id=control_surface_name)
            self.tab_control_ids[control_surface_name] = tab_control
            self.ids.interactive_controls.add_widget(tab_control)

    def disable_controls(self) -> None:
        """Disable the ActiveScreen controls."""
        for surface_name, surface_value in controller.deactivate_profile().items():
            self.tab_control_ids[surface_name].set_value(surface_value)
            self.tab_control_ids[surface_name].disable()

    def enable_controls(self, username: str) -> None:
        """Enable the ActiveScreen controls with values from a WaveProfile yaml file."""
        for surface_name, surface_value in controller.activate_profile(username).items():
            self.tab_control_ids[surface_name].set_value(surface_value)

    def invert(self) -> None:
        """Mirror the Controls, either `Goofy` or `Regular` was pressed."""
        for surface_name, surface_value in controller.invert().items():
            self.tab_control_ids[surface_name].set_value(surface_value)


class TabControl(MDBoxLayout):
    id = StringProperty()
    value = NumericProperty()
    display = StringProperty()
    max = NumericProperty()
    min = NumericProperty()

    def __init__(self, **kwargs):
        super().__init__()
        self.id = kwargs['id']

    def increment(self) -> None:
        try:
            controller.surfaces[self.id].increment()
            self.enable_increment()
        except Surface.CannotDecrement:
            self.disable_increment()

    def decrement(self) -> None:
        try:
            controller.surfaces[self.id].decrement()
            self.enable_decrement()
        except Surface.CannotDecrement:
            self.disable_decrement()

    @property
    def value(self) -> None:
        return controller.values[self.id]




