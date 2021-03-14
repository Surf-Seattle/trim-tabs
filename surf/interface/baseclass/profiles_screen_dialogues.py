from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import (
    NumericProperty,
    StringProperty,
    BooleanProperty,
    DictProperty
)

from utils import (
    logger,
    utilities as u
)


class EditProfileDialogue(BoxLayout):
    row_count = NumericProperty()
    username = StringProperty()
    initial_attributes = DictProperty()
    profile_config = DictProperty()
    slider_ids = DictProperty({})

    def __init__(self, *args, **kwargs) -> None:
        super().__init__()
        self.username = kwargs['username']
        self.profile_config = u.Profile.read_config(username=self.username)
        self.initial_attributes = self.profile_config['control_surfaces']
        self.row_count = len(self.initial_attributes)
        Clock.schedule_once(self.create_controls)

    def create_controls(self, *args) -> None:
        for control_surface_name, control_surface_value in self.initial_attributes.items():
            logger.info(f'[UI] Creating Slider for "{control_surface_name}" with value: "{control_surface_value}"')
            slider = TabValueSlider(
                id=control_surface_name,
                value=control_surface_value,
            )
            self.slider_ids[control_surface_name] = slider
            self.ids.interactive_controls.add_widget(slider)

    @property
    def slider_values(self) -> dict:
        return {
            control_surface_name: int(slider_widget.ids.slider.value)
            for control_surface_name, slider_widget in self.slider_ids.items()
        }


class AddProfileDialogue(BoxLayout):
    row_count = NumericProperty()
    initial_attributes = DictProperty({})
    slider_ids = DictProperty({})

    def __init__(self, *args) -> None:
        super().__init__()
        Clock.schedule_once(self.create_controls)
        self.row_count = len(u.Configuration().control_surfaces) + 100
        self.initial_attributes = {control['name']: 0 for control in u.Configuration().control_surfaces}

    def create_controls(self, *args) -> None:
        self.row_count = len(u.Configuration().control_surfaces)
        for control_surface_name, control_surface_value in self.initial_attributes.items():
            logger.info(f'[UI] Creating Slider for "{control_surface_name}" with value: "{control_surface_value}"')
            slider = TabValueSlider(
                id=control_surface_name,
                value=control_surface_value,
            )
            self.slider_ids[control_surface_name] = slider
            self.ids.interactive_controls.add_widget(slider)

    @property
    def slider_values(self) -> dict:
        return {
            control_surface_name: int(slider_widget.ids.slider.value)
            for control_surface_name, slider_widget in self.slider_ids.items()
        }

class TabValueSlider(BoxLayout):
    id = StringProperty()
    display_name = StringProperty()
    value = NumericProperty()
    max = NumericProperty()
    min = NumericProperty()

    def __init__(self, **kwargs):
        super().__init__()
        self.id = kwargs['id']
        self.display_name = f"  {self.id}"
        self.value = int(kwargs['value'])
        self.min = 0
        self.max = 100
