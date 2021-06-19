import os

from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.config import Config
from kivy.core.window import Window

KV = """
#:import FadeTransition kivy.uix.screenmanager.FadeTransition
#:import SurfRootScreen interface.baseclass.root_screen.SurfRootScreen

SurfRootScreen:
    name: "SurfRootScreen"
    

"""
logger = None
UI_KV_DIR = None


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


def run(pins: bool, fullscreen: bool) -> None:
    global logger
    global UI_KV_DIR

    import utils
    from utils import UI_KV_DIR
    from utils import utilities as u
    from utils import logger
    from utils import controller

    utils.log_startup_details()

    logger.info('')
    logger.info('Running MDSurf.')
    logger.info('')

    u.first_time_setup_check()
    controller.start()
    if fullscreen:
        Config.set('graphics', 'window_state', 'maximized')
        Config.set('graphics', 'fullscreen', 'auto')
        Config.write()
    else:
        Config.set('graphics', 'resizable', '0')
        Config.set('graphics', 'width', '800')
        Config.set('graphics', 'height', '500')
        Config.set('graphics', 'fullscreen', 'false')
        Window.show_cursor = True
        Config.write()
    MDSurf().run()
