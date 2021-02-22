### 2021/02/22
- comment downloaded links in yande listfile booru-yande.txt
  ```bash
  IFS=$'\r\n'
  cp booru-yande.txt /tmp/yande.txt
  for x in $(ls -1 yande.re* | awk '{print $2}'); do
  sed -e "/ $x / s/^#*/#/" -i /tmp/yande.txt
  done
  cat /tmp/yande.txt > booru-yande.txt
  ```
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
  ls -1 | grep -E '^\(' | sed -nE 's/(^\([^)]*\)) ?(.*)/\2/p'
  Z=$(ls -1 | grep -E '^\(' | head -n 1 | sed -nE 's/(^\([^)]*\)) ?(.*)/\2/p')
  echo "$Z" | sed -e 's/^[[:space:]]*//; s/[[:space:]]*$//'
  Z=${Z%% }; Z=${Z## }; echo "$Z"
  
  IFS=$'\r\n'
  CUR=$(pwd)
  for X in $(ls -1 | grep -E '^\([^)]*\)'); do
  Y=$(echo "$X" | sed -nE 's/(^\([^)]*\)) ?(.*)/\2/p')
  Y=$(echo "$Y" | sed -e 's/^[[:space:]]*//; s/[[:space:]]*$//')
  mv --no-clobber -v "$X" "$Y"
  echo "mv '$Y' '$X'" >> /tmp/CXX_undo.txt
  done
  ```
  `Tl;dr: [^)] = Negative set, match everything that is not ")" close bracket`
  
  
  
