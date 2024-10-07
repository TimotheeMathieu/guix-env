#!/usr/bin/env guix shell --pure --preserve='(^DISPLAY$|^XAUTHORITY$|^TERM$)' bash  coreutils -- bash
# From https://stackoverflow.com/questions/10813538/shebang-line-limit-in-bash-and-linux-kernel

script="$1" 
shebang=$(head -1 "$script")

# use an array in case a argument is there too
interp=( ${shebang#\#!} )        

# now run it, passing in the remaining command line arguments
shift 1
exec "${interp[@]}" "$script" "${@}"
