#!/usr/bin/env -S guix time-machine --channels=${HOME}/.guix_env/{{ name }}/channels.scm -- shell git bash  -- bash

cd $HOME/.guix_env/{{ name }}

git add manifest.scm channels.scm .zshrc
git add bin/*

[[ -f poetry.lock ]] && git add poetry.lock
[[ -f pyproject.toml ]] && git add pyproject.toml
git commit -m "Update of guix env {{ name }}"
