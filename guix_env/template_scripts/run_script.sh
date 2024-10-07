#!/usr/bin/env -S bash
# Must be run through launch_in_guix

export POETRY_CACHE_DIR=${HOME}/.guix_env/poetry_cache
export POETRY_VIRTUALENVS_IN_PROJECT=true
export GUIX_ENV_NAME={{ name }}
export SHELL=$(realpath $(which zsh))
export LD_LIBRARY_PATH=/lib
export ZDOTDIR=${HOME}/.guix_env/{{ name }}/bin
export TERM=ansi

# Link the lib file for FHS library handling
poetry run --directory=${HOME}/.guix_env/{{ name }} $@
