## TODOs
- comment downloaded links in yande listfile booru-yande.txt
  ```bash
  IFS=$'\r\n'
  cp booru-yande.txt /tmp/yande.txt
  for x in $(ls -1 yande.re* | awk '{print $2}'); do
  sed -e "/ $x / s/^#*/#/" -i /tmp/yande.txt
  done
  cat /tmp/yande.txt > booru-yande.txt
  ```
- Xtract watcher (WORKING) https://linux.die.net/man/1/inotifywait
  ```bash
  inotifywait -m -r -o /tmp/xtract_watch.txt -e modify -e move -e create -e delete --format '%:e %w%f' ~/Xtracts
  inotifywait --monitor --recursive --outfile /tmp/xtract_watch.txt --event modify --event move --event create --event delete --format '%:e %w%f' ~/Xtracts
  function watcher_start() {
    IFS=$'\r\n'
    inotifywait -m -r -o /tmp/xtract_watch.txt -e modify -e move -e create -e delete --format '%:e %w%f' --daemon "$1"
    echo $! | tee /tmp/watcher.pid
    watcher_pid=$(cat /tmp/watcher.pid)
    echo "Watcher Process [$watcher_pid]: $(ps -p $watcher_pid -o command) [STARTED]\nUse: 'kill -9 $watcher_pid' or 'watcher_stop' to kill it."
  }
  function watcher_stop() {
    if [ -s /tmp/watcher.pid ]; then
      watcher_pid=$(cat /tmp/watcher.pid)
      echo -n "[$watcher_pid] Killing: $(ps -p $watcher_pid -o command) "
      kill -9 "$watcher_pid" && echo '[_OK_]' || echo '[FAIL]'
    else
      echo "No watcher process available"
    fi
  }
  ```
- booru.py > from helpers.text_file import keyed_list > list mark comment function keyed_list.comment(list_key, list_line, comment='#')
- helpers.misc > init_db() > needs updating to include jsondb type
- mysqldump (optional: sqlite) to json conversion
- skbnya external search url, preferable dm2 (very low priority)
- watcher list converter (inotifywait events to action)

## DONE
- rename dj match first brackets: </br>
  https://unix.stackexchange.com/questions/617505/sed-replace-string-in-square-brackets-with-key </br>
  `
  Since you need to match from an opening until the corresponding closing bracket.
  That would be \[.*\] but sed is greedy:
    In case your line contains [text1] text2 [text3], sed will match all of this.
    So you need to define, instead of .*, any character which is not a closing bracket, zero or more times: [^]]*.
  Note that in the above, we don't need to escape (\]) the bracket in the middle, 
    because sed awaits for at least one character to exclude after the caret (^), 
    so it will not misread this as the closing bracket of the list of the excluded characters, but as a literal bracket.
  `
  ```bash
  ls -1 | grep -E '^\('
  ls -1 | grep -E '^\(' | sed -nE 's/^\(([^)]*)\) ?.*/\1/p; s/[\d128-\d255]/-/g'
  ls -1 | grep -E '^\(' | sed -nE 's/^\([^)]*\) ?(.*)/\1/p'
  Z=$(ls -1 | grep -E '^\(' | head -n 1 | sed -nE 's/(^\([^)]*\)) ?(.*)/\2/p')
  echo "$Z" | sed -e 's/^[[:space:]]*//; s/[[:space:]]*$//'
  Z=${Z%% }; Z=${Z## }; echo "$Z"
  
  IFS=$'\r\n'
  CUR=$(pwd)
  for X in $(ls -1 | grep -E '^\([^)]*\) ?'); do
  Y=$(echo "$X" | sed -nE 's/(^\([^)]*\)) ?(.*)/\2/p')
  Y=$(echo "$Y" | sed -e 's/^[[:space:]]*//; s/[[:space:]]*$//')
  mv --no-clobber -v "$X" "$Y"
  echo "mv '$Y' '$X'" >> /tmp/CXX_undo.txt
  done
  ```
  `Tl;dr: [^)] = Negative set, match everything that is not ")" close bracket`
