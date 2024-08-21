#!/usr/bin/env -S guix time-machine --channels=${HOME}/.guix_env/{{ name }}/channels.scm -- shell {{ guix_args }} --preserve='(^DISPLAY$|^XAUTHORITY$|^TERM$)' --share=${HOME} --expose=/dev/dri --expose=/sys  -m ${HOME}/.guix_env/{{ name }}/manifest.scm -- bash

# Link the lib file for FHS library handling
export LD_LIBRARY_PATH=/lib

echo 'Entering guix environment'
rm  ${HOME}/.guix_env/guix_env_venv/{{ name }}_venv/bin/python3
ln -s $(which python3) ${HOME}/.guix_env/guix_env_venv/{{ name }}_venv/bin/python3
source ${HOME}/.guix_env/guix_env_venv/{{ name }}_venv/bin/activate

pip freeze > /tmp/guix_env_{{ name }}_requirements.txt
if cmp --silent -- "/tmp/guix_env_{{ name }}_requirements.txt" "${HOME}/.guix_env/{{ name }}/requirements.txt"
then
   echo
else
   read -p "Requirement and installed packages are different. Reinstall from requirements.txt ? (y/n)" -n 1 -r
   echo    # (optional) move to a new line
   if [[ $REPLY =~ ^[Yy]$ ]]
   then
       pip install -r ${HOME}/.guix_env/{{ name }}/requirements.txt
   fi
fi


ZDOTDIR=${HOME}/.guix_env/{{ name }}/bin zsh
