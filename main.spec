from kivy_deps import sdl2, glew
from kivymd import hooks_path as kviymd_hooks_path
# import yaml

# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['main.py'],
             pathex=['C:\\Users\\aaron\\Documents\\git_project\\trim-tabs'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[kviymd_hooks_path],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

a.datas += [
    ('Code\\intraface\\active_controls.kv', 'C:\\Users\\aaron\\Documents\\git_project\\trim-tabs\\intraface\\active_controls.kv', 'DATA'),
    ('Code\\intraface\\active_screen.kv', 'C:\\Users\\aaron\\Documents\\git_project\\intraface\\active_screen.kv', 'DATA'),
    ('Code\\intraface\\profiles_screen.kv', 'C:\\Users\\aaron\\Documents\\git_project\\intraface\\profiles_screen.kv', 'DATA'),
    ('Code\\intraface\\profiles_screen_dialogues.kv', 'C:\\Users\\aaron\\Documents\\git_project\\trim-tabs\\intraface\\profiles_screen_dialogues.kv', 'DATA'),
    ('Code\\intraface\\profiles_screen_list_item.kv', 'C:\\Users\\aaron\\Documents\\git_project\\trim-tabs\\intraface\\profiles_screen_list_item.kv', 'DATA'),
    ('Code\\intraface\\root_screen.kv', 'C:\\Users\\aaron\\Documents\\git_project\\trim-tabs\\intraface\\root_screen.kv', 'DATA'),
    ('Code\\intraface\\settings_screen.kv', 'C:\\Users\\aaron\\Documents\\git_project\\trim-tabs\\intraface\\settings_screen.kv', 'DATA'),
    ('Code\\intraface\\tab_navigation.kv', 'C:\\Users\\aaron\\Documents\\git_project\\trim-tabs\\intraface\\tab_navigation.kv', 'DATA'),
]

exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='main',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False )

coll = COLLECT(exe,
               Tree('C:\\Users\\aaron\\Documents\\git_project\\trim-tabs\\'),
               a.binaries,
               a.zipfiles,
               a.datas,
               *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
               strip=False,
               upx=True,
               upx_exclude=[],
               name='main')
