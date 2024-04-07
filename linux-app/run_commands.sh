#!/bin/zsh
# runs realrate commands

fromSel=$(xsel -o)
full_path=$(realpath "$0")
dir_path=$(dirname "$full_path")

"$dir_path/ifinstalled" xsel
"$dir_path/ifinstalled" dmenu
"$dir_path/ifinstalled" notify-send
"$dir_path/ifinstalled" xargs
"$dir_path/ifinstalled" awk
"$dir_path/ifinstalled" python

source "$dir_path/venv/bin/activate"

verboseExit() {
  echo "$2" && notify-send -t 35000 -u critical "$1" "$2" && exit 1
}

setFrom() {
  result=$(python "$dir_path/realrate.py" set_from  --code "$1")
  lastCode=$?

  if [ $lastCode -eq 0 ]; then
    notify-send -t 10000 "Success!" "\n$result"
  else
    verboseExit "Fail" "\n$result"
  fi
}

calculateComissions() {
  result=$(python "$dir_path/realrate.py" calculate_comissions  --selected_rate "$1")
  lastCode=$?

  if [ $lastCode -eq 0 ]; then
    notify-send -t 35000 "Comissions calculated below:" "\n$result"
  else
    verboseExit "Fail" "\n$result"
  fi
}

setTo() {
  result=$(python "$dir_path/realrate.py" set_to  --code "$1")
  lastCode=$?

  if [ $lastCode -eq 0 ]; then
    notify-send -t 10000 "Success!" "\n$result"
  else
    notify-send -t 35000 -u critical "Fail" "\n$result"
  fi
}

addFavorite() {
  result=$(python "$dir_path/realrate.py" add_favorite  --code "$1")
  lastCode=$?

  if [ $lastCode -eq 0 ]; then
    notify-send -t 10000 "Success!" "\n$result"
  else
    notify-send -t 35000 -u critical "Fail" "\n$result"
  fi
}

cleanFavorite() {
  result=$(python "$dir_path/realrate.py" clean_favorite  --code "$1")
  lastCode=$?

  if [ $lastCode -eq 0 ]; then
    notify-send -t 10000 "Success!" "\n$result"
  else
    notify-send -t 35000 -u critical "Fail" "\n$result"
  fi
}

updateRates() {
  result=$(python "$dir_path/realrate.py" update_rates)
  lastCode=$?

  if [ $lastCode -eq 0 ]; then
    notify-send -t 10000 "Success!" "\n$result"
  else
    notify-send -t 35000 -u critical "Fail" "\n$result"
  fi
}

askWhatToDoSel() {
  [ -z $fromSel ] && verboseExit "Fail!" "Nothing selected!"
  cleanedSelResult=$(python "$dir_path/realrate.py" clean_input  --dirty "$fromSel")
  lastCode=$?

  if [ $lastCode -eq 0 ]; then
    answersel=$(printf "Calculate comissions\\nUpdate rates\\nSet as 'from'\\nSet as 'to'\\nAdd to favorites\\nClean from favorites" | dmenu -i -p "What to do with '$cleanedSelResult'?") &&
    case "$answersel" in
      "Calculate comissions") calculateComissions "$cleanedSelResult";;
      "Update rates") updateRates;;
      "Set as 'from'") setFrom "$cleanedSelResult";;
      "Set as 'to'") setTo "$cleanedSelResult";;
      "Add to favorites") addFavorite "$cleanedSelResult";;
      "Clean from favorites") cleanFavorite "$cleanedSelResult";;
      *) verboseExit "error!" "nothing selected!" ;;
    esac
  else
    verboseExit "Fail" "\nUnsupported format of selected text"
  fi
}

askWhatToDoSel
