#!/usr/bin/env -S guix time-machine --channels=${HOME}/.guix_env/{{ name }}/channels.scm -- shell {{ guix_args }} --preserve='(^DISPLAY$|^XAUTHORITY$|^TERM$)' --share=${HOME} --share=/tmp --expose=/dev/dri --expose=/sys  -m ${HOME}/.guix_env/{{ name }}/manifest.scm -- sh

export POETRY_CACHE_DIR=${HOME}/.guix_env/poetry_cache
export POETRY_VIRTUALENVS_IN_PROJECT=true
export GUIX_ENV_NAME={{ name }}
export SHELL=$(realpath $(which zsh))
export LD_LIBRARY_PATH=/lib
export ZDOTDIR=${HOME}/.guix_env/{{ name }}/bin
export TERM=ansi

exec "$@"
