#!/bin/zsh
# runs realrate commands

full_path=$(realpath "$0")
dir_path=$(dirname "$full_path")

"$dir_path/ifinstalled" xsel
"$dir_path/ifinstalled" notify-send
"$dir_path/ifinstalled" python

source "$dir_path/venv/bin/activate"

verboseExit() {
  echo "$2" && notify-send -t 35000 -u critical "$1" "$2" && exit 1
}

result=$(python "$dir_path/realrate.py" get_rate  --from "$1" --to "$2")
lastCode=$?

if [ $lastCode -eq 0 ]; then
  echo "$result"
else
  verboseExit "Fail" "\n$result"
fi
