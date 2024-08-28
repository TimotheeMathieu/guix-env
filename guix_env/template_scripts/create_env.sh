#!/usr/bin/env -S guix time-machine --channels=${HOME}/.guix_env/{{ name }}/channels.scm -- shell {{ guix_args }} --preserve='(^DISPLAY$|^XAUTHORITY$|^TERM$)' --share=${HOME} --expose=/dev/dri --expose=/sys  -m ${HOME}/.guix_env/{{ name }}/manifest.scm -- bash


echo "Installing poetry"
curl -sSL https://install.python-poetry.org | python3 -
poetry install --no-root --directory={{ directory }}
