import os
from pathlib import Path

from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.config import Config
from kivy.core.window import Window

from log import logger

Config.set('graphics', 'resizable', '0') #0 being off 1 being on as in true/false
Config.set('graphics', 'width', '500')
Config.set('graphics', 'height', '500')


KV = """
#:import FadeTransition kivy.uix.screenmanager.FadeTransition
#:import SurfRootScreen interface.baseclass.root_screen.SurfRootScreen

ScreenManager:
    transition: FadeTransition()
    
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
        kv_dir = os.path.join(os.environ['SURF_ROOT'], 'interface', 'kv')
        for kv_file in os.listdir(kv_dir):
            logger.debug(f"\t- loading: {os.path.join(kv_dir, kv_file)}")
            with open(os.path.join(kv_dir, kv_file), encoding="utf-8") as kv:
                Builder.load_string(kv.read())

    def build(self):
        self.theme_cls.primary_palette = "Green"
        self.theme_cls.theme_style = "Dark"
        Window.size = (800, 480)
        Config.set('graphics', 'resizable', '0') #0 being off 1 being on as in true/false
        return Builder.load_string(KV)


if __name__ == '__main__':

    surf_root = str(Path(__file__).parent)
    os.environ.update({
        'SURF_ROOT': surf_root,
        'PROFILES_DIR': os.path.join(surf_root, 'config', 'profiles'),
        'CONFIG_DIR': os.path.join(surf_root, 'config'),
    })

    logger.debug(f"env.SURF_ROOT = {os.environ['SURF_ROOT']}")
    logger.debug(f"env.PROFILES_DIR = {os.environ['PROFILES_DIR']}")
    logger.debug(f"env.CONFIG_DIR = {os.environ['CONFIG_DIR']}")
    logger.debug(f"env.CONFIG_DIR = {os.environ['CONFIG_DIR']}")
    logger.info('')
    logger.info('Running MDSurf.')
    logger.info('')
    MDSurf().run()
