#!/usr/bin/env -S guix time-machine --channels=${HOME}/.guix_env/{{ name }}/channels.scm -- shell {{ guix_args }} --preserve='(^DISPLAY$|^XAUTHORITY$|^TERM$)' --share=${HOME} --expose=/dev/dri --expose=/sys  -m ${HOME}/.guix_env/{{ name }}/manifest.scm -- bash

# Link the lib file for FHS library handling


echo 'Entering guix environment'
[ -f ${HOME}/.guix_env/guix_env_venv/{{ name }}_venv/bin/python3 ] && rm  ${HOME}/.guix_env/guix_env_venv/{{ name }}_venv/bin/python3 && ln -s $(which python3) ${HOME}/.guix_env/guix_env_venv/{{ name }}_venv/bin/python3

${HOME}/.guix_env/{{ name }}/pre_env zsh
