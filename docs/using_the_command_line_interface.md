# Running the Application

Running it on the pi. This runs it like we're "on the boat".

```bash
$ python surf.py run
```

Running it on a desktop monitor

```bash
$ python surf.py run --windowed
```

Running it on a non-rasberry OS

```bash
$ python surf.py run --windowed --no_pins
```

# Create a New Wave Profile

```bash
$ python surf.py new-wave-profile --name Wacky --values 0 50 100
```

# Update an existing Wave Profile

```bash
$ python surf.py update-wave-profile --name Steep --values 0 15 30
```

# Delete Wave Profile

```bash
$ python surf.py delete-wave-profile --name Steep
```

# Updating an Operating Mode

Want to change the full extract duration of 2 pins?

```bash
$ python surf.py update-operating-mode --mode wet --concurrency 2 --context deploy --value 3.45
```

Want to change the full retract duration of 3 pins?

```bash
$ python surf.py update-operating-mode --mode wet --concurrency 3 --context withdraw --value 6.00
```

# Reset a Config File

Want to reset `operation_modes.yml` to the template values?

```bash
$ python surf.py --reset-config operating_modes
```

Want to reset `control_surfaces.yml` to the template values?

```bash
$ python surf.py --reset-config control_surfaces
```

# First Time Setup

```bash
$ python surf.py first-time-setup
```

* runs `utilities.first_time_setup_check()`
* this is also done when the application is run
* there is not need to manually call this unless you're testing the set-up process