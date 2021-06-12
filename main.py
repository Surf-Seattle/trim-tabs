import os

from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.config import Config

from utils import (
    logger,
    UI_KV_DIR,
    utilities as u,
    controller
)


KV = """
#:import FadeTransition kivy.uix.screenmanager.FadeTransition
#:import SurfRootScreen interface.baseclass.root_screen.SurfRootScreen

SurfRootScreen:
    name: "SurfRootScreen"
    

"""


class MDSurf(MDApp):
    def __init__(self, **kwargs):
        self.load_kv_modules()
        super().__init__(**kwargs)
        self.title = "Surfpy"

    @classmethod
    def load_kv_modules(cls) -> None:
        logger.info('Loading kivy modules...')
        for kv_file in os.listdir(UI_KV_DIR):
            logger.debug(f"\t- loading: {os.path.join(UI_KV_DIR, kv_file)}")
            with open(os.path.join(UI_KV_DIR, kv_file), encoding="utf-8") as kv:
                Builder.load_string(kv.read())

    def build(self):
        self.theme_cls.primary_palette = "Green"
        self.theme_cls.theme_style = "Dark"
        return Builder.load_string(KV)


if __name__ == '__main__':

    logger.info('')
    logger.info('Running MDSurf.')
    logger.info('')
    u.first_time_setup_check()
    controller.start()
    if os.environ.get('FULLSCREEN', "true") == "true":
        print('using fullscreen')
        Config.set('graphics', 'window_state', 'maximized')
        Config.set('graphics', 'fullscreen', 'auto')
    else:
        print('using windowed screen')
        Config.set('graphics', 'resizable', '0') #0 being off 1 being on as in true/false
        Config.set('graphics', 'width', '500')
        Config.set('graphics', 'height', '500')
    # Config.write()
    MDSurf().run()
