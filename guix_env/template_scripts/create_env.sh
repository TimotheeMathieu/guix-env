#!/usr/bin/env -S bash
# Must be run through launch_in_guix

set -e

export POETRY_CACHE_DIR=${HOME}/.guix_env/poetry_cache
export POETRY_VIRTUALENVS_IN_PROJECT=true
export GUIX_ENV_NAME={{ name }}
export SHELL=$(realpath $(which zsh))
export LD_LIBRARY_PATH=/lib
export ZDOTDIR=${HOME}/.guix_env/{{ name }}/bin
export TERM=ansi

echo "Creating the environment"

export REQUIREMENTS_FILE={{ requirements }}


pip3 install -U requests==2.28.2 urllib3==1.26.15 # fix depencies, needed for now for poetry while I am not sure why.

poetry config virtualenvs.prompt ' ' --local --directory={{ directory }}
poetry install --no-root --directory={{ directory }}

if [[ ! -z $REQUIREMENTS_FILE ]]; then
     cat $REQUIREMENTS_FILE | xargs poetry add --directory={{ directory }}
fi

poetry completions zsh > {{ directory }}/_poetry
