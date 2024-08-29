#!/usr/bin/env  bash
# We use this script instead of having it in the shebang because the guix line is too long for a shebang.
# Found on stackoverflow https://stackoverflow.com/questions/10813538/shebang-line-limit-in-bash-and-linux-kernel
script="$1" 
guix_cmd="guix time-machine --channels=${HOME}/.guix_env/{{ name }}/channels.scm -- shell {{ guix_args }} --preserve='(^DISPLAY$|^XAUTHORITY$|^TERM$)' --share=${HOME} --share=/tmp --expose=/dev/dri --expose=/sys  -m ${HOME}/.guix_env/{{ name }}/manifest.scm -- "

# now run it, passing in the remaining command line arguments
shift 1
$guix_cmd ${HOME}/.guix_env/{{ name }}/pre_env "$script" "${@}"
