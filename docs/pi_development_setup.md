'# Install Miniconda

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
(surfy) ~/projects: $ git clone https://github.com/kivymd/KivyMD.git@0.104.2 --depth 1
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
(surfy) ~/projects/trim-tabs: $ python surf.py run
```

This does first-time set-up work if it finds that things needed to run are not present. 
* creates directory `~/.surf` if not present
* creates directory `~/.surf/logs` if not present
* creates directory `~/.surf/profiles` if not present
* creates directory `~/.surf/config` if not present
* copies `utils/config_templates/operating_modes.yml` to `~/.surf/config` if not present
* copies `utils/config_templates/control_surfaces.yml` to `~/.surf/config` if not present
* if `~/.surf/profiles/` is empty, it is populated with the files in `utils/profile_templates`

# Enabling Raspberry Pi touch screen

In `~/.kivy/config.ini` file, replace the lines under the `[input]` heading and replace with:

```
mouse = mouse
mtdev_%(name)s = probesysfs,provider=mtdev
hid_%(name)s = probesysfs,provider=hidinput
```

This allows the touchscreen input to be seen by the trim-tabs interface.
