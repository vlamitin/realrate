#!/bin/zsh
# runs realrate commands

./ifinstalled xsel
./ifinstalled dmenu
./ifinstalled notify-send
./ifinstalled xargs
./ifinstalled awk
./ifinstalled python

fromSel=$(xsel -o)

source ./venv/bin/activate

verboseExit() {
  echo "$2" && notify-send -t 35000 -u critical "$1" "$2" && exit 1
}

setFrom() {
  result=$(python realrate.py set_from  --code "$1")
  lastCode=$?

  if [ $lastCode -eq 0 ]; then
    notify-send -t 10000 "Success!" "\n$result"
  else
    verboseExit "Fail" "\n$result"
  fi
}

calculateComissions() {
  result=$(python realrate.py calculate_comissions  --selected_price "$1")
  lastCode=$?

  if [ $lastCode -eq 0 ]; then
    notify-send -t 35000 "Comissions calculated below:" "\n$result"
  else
    verboseExit "Fail" "\n$result"
  fi
}

setTo() {
  result=$(python realrate.py set_to  --code "$1")
  lastCode=$?

  if [ $lastCode -eq 0 ]; then
    notify-send -t 10000 "Success!" "\n$result"
  else
    notify-send -t 35000 -u critical "Fail" "\n$result"
  fi
}

addFavorite() {
  result=$(python realrate.py add_favorite  --code "$1")
  lastCode=$?

  if [ $lastCode -eq 0 ]; then
    notify-send -t 10000 "Success!" "\n$result"
  else
    notify-send -t 35000 -u critical "Fail" "\n$result"
  fi
}

cleanFavorite() {
  result=$(python realrate.py clean_favorite  --code "$1")
  lastCode=$?

  if [ $lastCode -eq 0 ]; then
    notify-send -t 10000 "Success!" "\n$result"
  else
    notify-send -t 35000 -u critical "Fail" "\n$result"
  fi
}

askWhatToDoSel() {
  [ -z $fromSel ] && verboseExit "Fail!" "Nothing selected!"
  cleanedSelResult=$(python realrate.py clean_input  --dirty "$fromSel")
  lastCode=$?

  if [ $lastCode -eq 0 ]; then
    answersel=$(printf "Calculate comissions\\nSet as 'from'\\nSet as 'to'\\nAdd to favorites\\nClean from favorites" | dmenu -i -p "What to do with '$cleanedSelResult'?") &&
    case "$answersel" in
      "Calculate comissions") calculateComissions "$cleanedSelResult";;
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
