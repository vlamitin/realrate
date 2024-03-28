#!/bin/zsh
# runs realrate commands

./ifinstalled xsel
./ifinstalled dmenu
./ifinstalled notify-send
./ifinstalled xargs
./ifinstalled awk
./ifinstalled python

fromsel=$(xsel -o | awk '{print $1}')
truncatedFS=$(printf "%s" "${fromsel:0:10}")

verboseExit() {
  echo $2 && notify-send -t 35000 -u critical $1 $2 && exit 1
}

setFrom() {
  source ./venv/bin/activate
  result=$(python realrate.py set_from  --code $truncatedFS)
  lastCode=$?

  if [ $lastCode -eq 0 ]; then
    notify-send -t 10000 "Success!" "\n$result"
  else
    verboseExit "Fail" "\n$result"
  fi
}

setTo() {
  source ./venv/bin/activate
  result=$(python realrate.py set_to  --code $truncatedFS)
  lastCode=$?

  if [ $lastCode -eq 0 ]; then
    notify-send -t 10000 "Success!" "\n$result"
  else
    notify-send -t 35000 -u critical "Fail" "\n$result"
  fi
}

addFavorite() {
  source ./venv/bin/activate
  result=$(python realrate.py add_favorite  --code $truncatedFS)
  lastCode=$?

  if [ $lastCode -eq 0 ]; then
    notify-send -t 10000 "Success!" "\n$result"
  else
    notify-send -t 35000 -u critical "Fail" "\n$result"
  fi
}

cleanFavorite() {
  source ./venv/bin/activate
  result=$(python realrate.py clean_favorite  --code $truncatedFS)
  lastCode=$?

  if [ $lastCode -eq 0 ]; then
    notify-send -t 10000 "Success!" "\n$result"
  else
    notify-send -t 35000 -u critical "Fail" "\n$result"
  fi
}

askWhatToDoSel() {
  [ -z truncatedFS ] && verboseExit "error!" "Nothing selected!"
  answersel=$(printf "Set as 'from'\\nSet as 'to'\\nAdd to favorites\\nClean from favorites" | dmenu -i -p "What to do with '$truncatedFS'?") &&
  case "$answersel" in
    "Set as 'from'") setFrom;;
    "Set as 'to'") setTo ;;
    "Add to favorites") addFavorite ;;
    "Clean from favorites") cleanFavorite ;;
    *) verboseExit "error!" "nothing selected!" ;;
  esac
}

askWhatToDoSel
