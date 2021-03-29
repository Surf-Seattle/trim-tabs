following: https://stackoverflow.com/questions/43028666/how-to-package-a-kivy-app-with-pyinstaller

* create a new directory where the package will be built:
  * `/Users/alutz/IdeaProjects/trim-tabs-packaged`
* move the command line into that directory
* run
  * `python -m PyInstaller --name surf "/Users/alutz/IdeaProjects/trim-tabs/surf/main.py"`
  * `error 1` seen in the output of this command
  * despite this error the command seems to complete
* this created 2 directories in a file in `trim-tabs-packaged`
  * `build`, `dist`, and `surf.spec`
* then, run: 
  * `python -m PyInstaller surf.spec`
  * it will ask if you want to replace the contents of `dist`, yes.
  
  
  pip uninstall pyinstaller
  conda install -c conda-forge pyinstaller
  
# Errors

1

```text
[CRITICAL] [Spelling    ] Unable to find any valuable Spelling provider. Please enable debug logging (e.g. add -d if running from the command line, or change the log level in the config) and re-run your app to identify potential causes
enchant - ModuleNotFoundError: No module named 'enchant'
  File "/usr/local/anaconda3/envs/kivy_md_env/lib/python3.6/site-packages/kivy/core/__init__.py", line 62, in core_select_lib
    fromlist=[modulename], level=0)
  File "/usr/local/anaconda3/envs/kivy_md_env/lib/python3.6/site-packages/kivy/core/spelling/spelling_enchant.py", line 12, in <module>
    import enchant

osxappkit - ModuleNotFoundError: No module named 'AppKit'
  File "/usr/local/anaconda3/envs/kivy_md_env/lib/python3.6/site-packages/kivy/core/__init__.py", line 62, in core_select_lib
    fromlist=[modulename], level=0)
  File "/usr/local/anaconda3/envs/kivy_md_env/lib/python3.6/site-packages/kivy/core/spelling/spelling_osxappkit.py", line 16, in <module>
    from AppKit import NSSpellChecker, NSMakeRange
```


# changes made to support the packaging effort
* profiles moved from `surf/config/profiles` to `~/.surf/profiles`
* configs moved from `surf/config` to `~/.surf/config`
* logs moved from `surf/logs` to `~/.surf/logs`




# https://www.youtube.com/watch?v=NEko7jWYKiE&list=PLCC34OHNcOtpz7PJQ7Tv7hqFBP_xDDjqg&index=20

pip install pyinstaller
pyinstaller main.py -w

in main.spec, add
```
from kivy_deps import sdl2, glew
...
a.datas += [
    ('Code\\active_controls.kv', 'C:\\Users\\aaron\\Documents\\git_project\\trim-trabs\\intraface\\active_controls.kv', 'DATA'),
    ('Code\\active_screen.kv', 'C:\\Users\\aaron\\Documents\\git_project\\intraface\\active_screen.kv', 'DATA'),
    ('Code\\profiles_screen.kv', 'C:\\Users\\aaron\\Documents\\git_project\\intraface\\profiles_screen.kv', 'DATA'),
    ('Code\\profiles_screen_dialogues.kv', 'C:\\Users\\aaron\\Documents\\git_project\\trim-trabs\\intraface\\profiles_screen_dialogues.kv', 'DATA'),
    ('Code\\profiles_screen_list_item.kv', 'C:\\Users\\aaron\\Documents\\git_project\\trim-trabs\\intraface\\profiles_screen_list_item.kv', 'DATA'),
    ('Code\\root_screen.kv', 'C:\\Users\\aaron\\Documents\\git_project\\trim-trabs\\intraface\\root_screen.kv', 'DATA'),
    ('Code\\settings_screen.kv', 'C:\\Users\\aaron\\Documents\\git_project\\trim-trabs\\intraface\\settings_screen.kv', 'DATA'),
    ('Code\\tab_navigation.kv', 'C:\\Users\\aaron\\Documents\\git_project\\trim-trabs\\intraface\\tab_navigation.kv', 'DATA'),
]
...
 *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
```
pyinstaller calc.spec -y


I removed this from root_screen.kv: #: import StiffScrollEffect kivymd.stiffscroll.StiffScrollEffect

$ pyintaller main.py -w --onefile
$ python -m PyInstaller main.py -w --onefile
< make changes to the .spec file >
$ python -m PyInstaller main.spec -y