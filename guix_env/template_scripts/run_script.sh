#!/usr/bin/env -S bash
# Must be run through launch_in_guix


export GUIX_ENV_NAME={{ name }}
export SHELL=$(realpath $(which zsh))
export LD_LIBRARY_PATH=/lib # Link the lib file for FHS library handling
export ZDOTDIR=${HOME}/.guix_env/{{ name }}/bin
export TERM=ansi

{% if with_python  %}
export POETRY_CACHE_DIR=${HOME}/.guix_env/poetry_cache
export POETRY_VIRTUALENVS_IN_PROJECT=true
. $HOME/.guix_env/{{ name }}/.venv/bin/activate

$@
    
{% else %}
$@

{% endif %}
