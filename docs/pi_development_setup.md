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

# Creating a Conda Environment

```bash
~: $ conda config --add channels rpi
~: $ conda create -n surfy python=3.6
~: $ source activate surfy
(surfy) ~: $
```

# Git Configuration Details

* Skip this step if you have done this before.

```bash
(surfy) ~: $ git config --global user.email  "you@example.com"
(surfy) ~: $ git config --global user.name "Your Name"
```

# Cloning this Repository

```bash
(surfy) ~: $ cd
(surfy) ~: $ mkdir projects
(surfy) ~: $ cd projects
(surfy) ~/projects: $ git clone https://github.com/Surf-Seattle/trim-tabs.git
(surfy) ~/projects: $ cd trim-tabs
(surfy) ~/projects/trim-tabs: $ git status
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
```

# Installing Dependencies

```bash
(surfy) ~/projects/trim-tabs: $ pip install -r requirements.txt
```

# Running the App for the first time

When running the project for the first time you will be prompted to enter configuration values for
the control surfaces as well as the profiles. Feel free to test your own values, but the following 
will be considered the standard as we all work on this together. Enter these values as prompted
after running `python main.py`:

> To trigger these steps after the "first time", just run `rm -rf ~/.surf` before running `python main.py`

Enter these values for the prompts which will populate `~/.surf/config/control_surfaces.yml`:

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

Enter these values for the prompts which will populate files in `~/.surf/profiles/`:

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

> The app should then load with the profiles as configured in the preceding steps appearing in the profiles tab.