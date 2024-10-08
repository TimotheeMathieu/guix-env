# Guix & venv environments for reproducible python development

This package give a cli tool to construct and enter environments constructed through guix (for the system-level packages) and pip/venv (for python packages). 

Remark that due to the use of pip, the resulting environment is not perfectly reproducible as it would be better to use guix all the way but this way is much simpler when using dev python packages that are not yet packaged in guix.


## Usage
Guix must be installed on the system, see [the guix manual](https://guix.gnu.org/manual/en/html_node/Binary-Installation.html) to do this.

```
pip install git+https://github.com/TimotheeMathieu/guix-env 
guix-env create my_env_name
```

This should create a directory in `~/.guix-env` containing files needed for the environment to run. Note that every file generated by guix-env will be saved into `~/.guix-env`. Then to spawn a shell in the environment, do

```
guix-env shell my_env_name
```

The first run may be a bit slow because of guix downloading a bunch of packages but the second run should be faster as guix cache the packages it uses in `/gnu/store` (remark: don't forget to use `guix gc` to clear the store periodically).

Then, you are good to go and do anything you wish in your environment. You are in a python virtual environment and you can install new python packages with pip. To add new guix package, use `guix-env add my_env_name my_package_name` from outside the environment.

One of the qualities of guix-env is its *reproducibility*, you can use the three files `manifest.scm`, `channels.scm` and `requirements.txt` that are in `~/.guix-env/my_env_name` to reproduce the environment using the following command:
```
guix-env create my_env_name --channel-file channels.scm --manifest-file manifest.scm --requirements-file requirements.txt
```
Remark that it is not perfect reproductibility because the requirements.txt file is created using pip whether it would be better to use a lock file generated by `pip-tools` or `poetry`, or even better to use guix as python package manager. For now this is not implemented.

## TODO

- Better documentation
- better requirements.txt -- switch to poetry or pip-tools to handle locks?
- Tests
- Handle GPU ?
- Feature: rollback, similar to what can be done with guix-home.
