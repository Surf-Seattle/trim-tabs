# Install Miniconda

* First check to see if you have miniconda installed.

```bash
~: $ conda
bash: conda: command not found
```

* If you get `bash: conda: command not found` you do not have conda installed.
* Continue through the rest of the `Install Miniconda` section.

```bash
~: $ wget http://repo.continuum.io/miniconda/Miniconda3-latest-Linux-armv7l.sh
~: $ sudo md5sum Miniconda3-latest-Linux-armv7l.sh
~: $ sudo /bin/bash Miniconda3-latest-Linux-armv7l.sh
~: $ echo 'export PATH="/home/pi/miniconda3/bin:$PATH"' >> ~/.bashrc
~: $ source ~/.bashrc
```
 * Now when you run `conda`, you should see the CLI help output
 
```bash
~: $ conda
usage: conda [-h] [-V] [--debug] command ...

conda is a tool for managing and deploying applications, environments and packages.

Options:
...
```

# Conda Configuration Details

* this step is required to enable `conda` on the rasberry pi

```bash
~: $ conda config --add channels rpi
```

# Git Configuration Details

* Skip this step if you have done this before.

```bash
~: $ git config --global user.email  "you@example.com"
~: $ git config --global user.name "Your Name"
```

# Create a Projects Directory

* this directory is where git repositories will be cloned.

```bash
~: $ cd
~: $ mkdir projects
~: $ cd projects
```

# Starting Over

> This section only applies to developers who have already set-up
> their development environment and would like to start from scratch
> for whatever reason.

```
~/projects: $ rm -rf ~/.surf
~/projects: $ rm -rf trim-tabs
~/projects: $ rm -rf KivyMD
~/projects: $ conda env remove -n surfy
```
* the first step will remove any files created by the app
* the next two steps will remove local git repositories
* the last step will remove the `surfy` conda environment
* following the remaining steps will allow you to restart fresh.

# Creating a Conda Environment

```bash
~/projects: $ conda create -n surfy python=3.6
~/projects: $ source activate surfy
(surfy) ~/projects: $
```

# Cloning Git Repositories

```bash
(surfy) ~/projects: $ git clone https://github.com/kivymd/KivyMD.git --depth 1
(surfy) ~/projects: $ cd KivyMD
(surfy) ~/projects/KivyMD: $ pip install .
(surfy) ~/projects/KivyMD: $ cd ..
(surfy) ~/projects: $ git clone https://github.com/Surf-Seattle/trim-tabs.git
(surfy) ~/projects: cd trim-tabs
(surfy) ~/projects/trim-tabs: pip install -r requirements.txt
```

# Running the App for the first time

Run the app for the first time:

```bash
(surfy) ~/projects/trim-tabs: $ python main.py
```

* You will be prompted to entery values related to configuration needed to run the app.
* Feel free to test your own values later.
* For now, follow the instructions below so we're all working from a common starting point.

### Configuring Control Surfaces

* The first set of prompts will populate `~/.surf/config/control_surfaces.yml` 
* For the following responses, provide the given answers:
  * `Enter the name for a control surface #1`: `PORT`
  * `Would you like to add another control surface? [y/N]`: `y`
  * `Enter the name for a control surface #2`: `CENTER`
  * `Would you like to add another control surface? [y/N]`: `y`
  * `Enter the name for a control surface #3`: `STARBOARD`
  * `Would you like to add another control surface? [y/N]`: `N`
  * `Are you happy with the names as shown?`: `y`
  * `Enter the goofy counterpart of: PORT`: `STARBOARD`
  * `Enter the goofy counterpart of: CENTER`: `CENTER`
  * `Enter the goofy counterpart of: STARBOARD`: `PORT`
  * `Are you happy with the mapping as shown?`: `y`

### Configuring the Initial Profiles

* The second set of prompts will populate files in `~/.surf/profiles/`:
* For the following responses, provide the given answers:
  * `enter a name for this profile:`: `Steep`
  * `enter PORT integer value between 0 and 100 (inclusive):`: `0`
  * `enter CENTER integer value between 0 and 100 (inclusive):`: `30`
  * `enter STARBOARD integer value between 0 and 100 (inclusive):`: `60`
  * `Create this profile?`: `y`
  * `Would you like to create another profile?`: `y`
  * `enter a name for this profile:`: `Mellow`
  * `enter PORT integer value between 0 and 100 (inclusive):`: `0`
  * `enter CENTER integer value between 0 and 100 (inclusive):`: `15`
  * `enter STARBOARD integer value between 0 and 100 (inclusive):`: `30`
  * `Create this profile?`: `y`
  * `Would you like to create another profile?`: `N`
* At this point the app should load and the profiles you've just configured
  should appear in the profiles tab.


# Triggering the "first time" prompts again

* These helpful prompts only appear if certain files are missing, 
  or if values in these files appear to be invalid.
* To trigger these prompts again, run the two following commands:

```bash
(surfy) ~/projects/trim-tabs: $ rm -rf ~/.surf/config/
(surfy) ~/projects/trim-tabs: $ rm -rf ~/.surf/profiles/
```

* Simply running `rm -rf ~/.surf/` is discouraged because it will
  delete existing log files which may be useful for debugging.
