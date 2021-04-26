# Using the Controller

The controller is `utils/controller.py` and contains the functionality that will be
used by the UI to drive the pins. A traditional python CLI using `argparse` or `click`
wouldn't work if you want the controller to remember the positions of the pins, which 
is an important part of its functionality. So for now the recommended method will be 
opening a python console.


#### The right place with the right tools

* remember to activate the `surfy` conda environment.
* remember to navigate to the local repository.

```bash
~: $ cd projects/trim-tabs
~/projects/trim-tabs: $ source activate surfy
(surfy) ~/projects/trim-tabs: $
```

### Using the controller

* First we'll open a python console
* Do that by typing `python` then pressing `enter`
* When you're cursor is idling after the `>>>`, you're in a python console!

```bash
(surfy) ~/projects/trim-tabs: $ python
Python 3.6.6 | packaged by rpi | (default Sep 6 2018, 10:56:14)
[GCC 6.3.0 20170516] on linux
Type "help", "copyright", "credits" or "license" for more information
>>> 
```

* import the controller.
* you'll see some logging lines, you can ignore those.

```python
>>> from utils import controller
2021-04-25 15:17:28,782 Surf                    __init__.py                  log_startup_details  57     INFO: -------------------------------------------------------
2021-04-25 15:17:28,782 Surf                    __init__.py                  log_startup_details  58     INFO: logger ready.
2021-04-25 15:17:28,782 Surf                    __init__.py                  log_startup_details  59     INFO: logging to: /Users/alutz/.surf/logs/20210425_151728.log
2021-04-25 15:17:28,782 Surf                    __init__.py                  log_startup_details  60     INFO: -------------------------------------------------------
2021-04-25 15:17:28,782 Surf                    __init__.py                  log_startup_details  61    DEBUG: START_TIME:      2021-04-25 15:17:28.781042
2021-04-25 15:17:28,782 Surf                    __init__.py                  log_startup_details  62    DEBUG: ROOT_DIR:        /Users/alutz/IdeaProjects/trim-tabs
2021-04-25 15:17:28,782 Surf                    __init__.py                  log_startup_details  63    DEBUG: CONFIG_DIR:      /Users/alutz/.surf/config
2021-04-25 15:17:28,783 Surf                    __init__.py                  log_startup_details  64    DEBUG: LOGS_DIR:        /Users/alutz/.surf/logs
2021-04-25 15:17:28,798 Surf                    __init__.py                  log_startup_details  65    DEBUG: PROFILES_DIR:    /Users/alutz/.surf/profiles
2021-04-25 15:17:28,798 Surf                    __init__.py                  log_startup_details  66    DEBUG: UI_DIR:          /Users/alutz/IdeaProjects/trim-tabs/interface
2021-04-25 15:17:28,799 Surf                    __init__.py                  log_startup_details  67    DEBUG: UI_KV_DIR:       /Users/alutz/IdeaProjects/trim-tabs/interface/kv
2021-04-25 15:17:28,799 Surf                    __init__.py                  log_startup_details  68    DEBUG: UI_PY_DIR:       /Users/alutz/IdeaProjects/trim-tabs/interface/baseclass
2021-04-25 15:17:28,799 Surf                    __init__.py                  log_startup_details  69     INFO: -------------------------------------------------------
```

* next create an instance of the `ControlSurfaces` class

```python
>>> surfaces = contoller.ControlSurfaces()
```

Now, there are commands that will track the position of the individual surfaces that will be 
used by the UI. These are great! There are also a few which cause the pins to act without
the change in position being tracked. These are intended for debugging purposes outside of the
UI. The first example will show the commands where the position is tracked, after which 
a second example will show the untracked commands. 

```python
>>> # this first step is not necessary, but shows how `surfaces.position` will 
>>> # print out the current position of each of the 3 surfaces
>>> surfaces.positions
{'PORT': 0, 'CENTER': 0, 'STARBOARD': 0}
>>>  
>>> # the following will move PORT to 50%
>>>  surfaces.move_to({'PORT': 0.5})
>>>
>>> # if you check the position again, you'll see the PORT position has changed
{'PORT': 0.5, 'CENTER': 0, 'STARBOARD': 0}
>>>
>>> # using this approach you can move more than 1 control surface at a time
>>>
>>> # `surfaces.move_to()` will move all of the surfaces at the same time
>>> # the following command will set all 3 `extend` pins high, then after
>>> # a period set `PORT.extend` low, then after another period set `CENTER.extend`
>>> # low, then finally after another period set `STARBOARD.extend` low.
>>> 
>>> surfaces.move_to({'PORT': 0.2, 'CENTER': 0.4, 'STARBOARD': 0.6})
>>> surfaces.positions
{'PORT': 0.2, 'CENTER': 0.4, 'STARBOARD': 0.6}
>>>
>>> # to move one surface at a time, you can use `surfaces.move_to()` and 
>>> # provide only one 1 surface in the dictionary argument, or you could
>>> # call the surface directly, like this:
>>>
>>> surfaces.STARBOARD.move_to(0.5)
>>> surfaces.positions
{'PORT': 0.2, 'CENTER': 0.4, 'STARBOARD': 0.5}
>>>
>>> # if you want to mimic how the UI will work, you can use the `increment()`
>>> # or `decrement()` on one of the surfaces, like:
>>>
>>> surfaces.PORT.increment()
>>> surfaces.position
{'PORT': 0.25, 'CENTER': 0.4, 'STARBOARD': 0.5}
>>> surfaces.STARBOARD.decrement()
>>> surfaces.position
{'PORT': 0.25, 'CENTER': 0.4, 'STARBOARD': 0.45}
>>>
>>> # the UI will also be able to "go goofy" or "go regular". For now I have encoded
>>> # this as simply 'inverting', and we'll let the UI handle whatever we want it 
>>> # to be called.
>>>
>>> surfaces.invert()
>>> surfaces.position
{'PORT': 0.45, 'CENTER': 0.4, 'STARBOARD': 0.25}
>>>
>>> # after we have had our fun, we'll want to retract the control surfaces.
>>> 
>>> surfaces.retract()
>>> surfaces.positions
{'PORT': 0, 'CENTER': 0, 'STARBOARD': 0}
>>>
>>> # you'll notice that this didnt set all 3 retract pins high for the full 4 seconds
>>> # this is a wrapper to calling `surfaces.move_to()` with a dictionary that has all 
>>> # of the control surfaces and 0 as the position. `move_to()` will calculate the difference
>>> # between the current position and the target position and make the necessary move. 
>>> # if a control surface is already at 0, the target and current positions are both 0. 
>>> # in cases when `move_to` is told to move to a position that is already satisfied, it 
>>> # will skip that change. to demonstrate this, lets run the preceeding command again. 
>>> surfaces.retract()
PORT already at 0
CENTER already at 0
STARBOARD already at 0
no change required, all positions already satisfied
>>> 
>>> # because the class thinks they are all already 0, it will skip any calls to move to 0.
>>> # if the control surface is not fully retracted, the logic of `move_to()` can be 
>>> # circumvented like this:
>>> 
>>> surfaces.retract(blindly=True)
>>>
>>> # this will set the retract pin of all of the control surfaces to HIGH for the full 
>>> # `full_retract_duration` which is defined in `~/.surf/config/constants.yml` which 
>>> # should be 4 seconds if you followed `pi_development_setup.py`
```

* The position of the control surfaces was tracked all throughout the preceeding example. 
* What follows are commands that are intended for debugging.
* The position of the surfaces is not tracked when these commands are used.
* After using these commands, a `surfaces.retract(blindly=True)` should be executed to 
  ensure that the pins and the position-tracking are re-synced.
  
```python
>>> # the pins can also be commanded directly. 
>>>
>>> # to set the PORT extend pin HIGH for 1 second
>>> surfaces.PORT.extend_pin.high(duration=1)
>>>
>>> # the `duration=` is optional, this will do the exact same thing
>>> surfaces.PORT.extend_pin.high(1)
>>>
>>> # if you do not specify a duration, it will set the pin high indefinitely
>>> surfaces.PORT.extend_pin.high()
>>>
>>> # if you do not specify a duration you will need to manually set that pin low again
>>> surfaces.PORT.extend_pin.low()
>>>
>>> # here are some examples using CENTER and STARBOARD
>>> # only `high()` takes a duration argument, an error will occur if you try to pass that argument to `low()`
>>>
>>> # CENTER using an explit duration
>>> surfaces.CENTER.retract_pin.high(duration=2)
>>> surfaces.CENTER.retract_pin.high(2)
>>>
>>> # CENTER with the duration controlled manually
>>> surfaces.CENTER.retract_pin.high()
>>> surfaces.CENTER.retract_pin.low()
>>>
>>> # STARBOARD using an explit duration
>>> surfaces.STARBOARD.retract_pin.high(duration=2)
>>> surfaces.STARBOARD.retract_pin.high(2)
>>>
>>> # STARBOARD with the duration controlled manually
>>> surfaces.STARBOARD.extend_pin.high()
>>> surfaces.STARBOARD.extend_pin.low()
>>>
```
