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
