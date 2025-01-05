#!/usr/bin/env bash

guix time-machine --channels=${HOME}/.guix_env/{{ name }}/channels.scm -- shell {{ guix_args }} \
     --preserve='(^DISPLAY$|^XAUTHORITY$|^TERM$|^XDG_)' \
     --share=${HOME}/.guix_env \
     --share=${HOME}/.guix_env/{{ name }}/.local=${HOME}/.local \
     --share=/tmp \
     --expose=/dev/dri \
     --expose=/sys \
     --expose=$XAUTHORITY \
     -m ${HOME}/.guix_env/{{ name }}/manifest.scm -- "$@"
