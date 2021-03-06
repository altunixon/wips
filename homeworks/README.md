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
  added to dedicated script, use bin-sh/folder-watcher start|stop
- TP-LINK UE300 RTL8153
  https://www.raspberrypi.org/forums/viewtopic.php?t=285867
  https://www.tp-link.com/us/support/download/ue300/#Driver
  https://elinux.org/RPi_USB_Ethernet_adapters
- mysqldump (optional: sqlite) to json conversion
- skbnya external search url, preferable dm2 (very low priority)
- watcher list converter (inotifywait events to action)
- pixiv.py > classes > view / index 404, index 404 example / xpath
  ```html
  <div id="wrapper">
    <div class="_unit error-unit">
    <h2 class="error-title">An error has occurred.</h2>
        <p class="error-message">This user account has been suspended.</p>
        <p class="error-message"><a href="/">Back</a></p>
        <div class="bigbanner">
            <iframe src="https://pixon.ads-pixiv.net/show?zone_id=bigbanner&amp;format=html&amp;s=1&amp;up=0&amp;a=31&amp;ng=g&amp;l=en&amp;uri=%2Fen%2Fusers%2F_PARAM_&amp;K=5419686e6159a&amp;ab_test_digits_first=51&amp;yuid=E5mXGWU&amp;suid=Pgo5wym9pxidiak1h&amp;num=603e46f5194" marginwidth="0" marginheight="0" allowtransparency="true" scrolling="no" class="ad-bigbanner" width="500" height="520" frameborder="0"></iframe>
        </div>
    </div>
  </div>
  ```
  ```html
  <div id="wrapper">
    <div class="_unit error-unit">
    <h2 class="error-title">An error has occurred.</h2>
        <p class="error-message">Work has been deleted or the ID does not exist.</p>
        <p class="error-message"><a href="/">Back</a></p>
        <div class="bigbanner">
            <iframe src="https://pixon.ads-pixiv.net/show?zone_id=bigbanner&amp;format=html&amp;s=1&amp;up=0&amp;a=31&amp;ng=g&amp;l=en&amp;uri=%2Fen%2Fartworks%2F_PARAM_&amp;K=5419686e6159a&amp;ab_test_digits_first=31&amp;yuid=M3E0gxg&amp;suid=Pgo1yecskyiw00p54&amp;num=6039c2e575" marginwidth="0" marginheight="0" allowtransparency="true" scrolling="no" class="ad-bigbanner" width="500" height="520" frameborder="0"></iframe>
        </div>
    </div>
  </div>
  ```
  `xpath_pindex_purged = '//div[@id="wrapper"]/div[contains(@class, "error-unit")]/p[@class="error-message"]'`
- new ssh keypair
- use autossh instead of ssh to avaoid connection timeout
  ```bash
  # addition options 
  ssh -o IdentitiesOnly=yes -o BatchMode=yes -o ServerAliveInterval=300 -o ServerAliveCountMax=3
  # does autossh supports -o flags?
  autossh -nNT -i ~/keypair.pem -R 2000:localhost:22 username@myoutsidebox.com &
  echo $! > /tmp/rtunnel.pid
  ```

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
- booru.py > from helpers.text_file import keyed_list > list mark comment function keyed_list.comment(list_key, list_line, comment='#')
- helpers.misc > init_db() > needs updating to include jsondb type
- Patch booru.py, pixiv.py
- Patch helpers/{text_file.py,misc.py}
- Diskstation: alias passwd="synouser --setpw" # admin <yourpassword>
- rit empty
  ```bash
  find ./ -type d -empty -exec mv {} _empty/ \;
  ls -1 _empty/ > /tmp/rit_trueform.txt
  ls | grep -v '\]/$' > /tmp/rit_malformed.txt
  for x in $(grep '^(' rit_malformed.txt); do
  y=$(echo "$x" | sed -nE 's/^\(([^)]*)\) ?(.*)/\1/p'); 
  z=$(grep "$y" /tmp/rit_trueform.txt | tr '\n' '|'); 
  echo "${x}|${z}" | tee -a /tmp/rit_merged.txt; 
  done
  sed -i.bak 's/\/|/|/g; s/|$//' /tmp/rit_merged.txt
  ```
```python
with open('/tmp/rit_merged.txt', 'r') as rf:
    rlines=[x.strip('\n') for x in rf.readlines() if '|' in x and not x.startswith('#')]

nlines = []
for z in rlines:
    w=z.split('|')
    old = w[0]
    print ('OLD Dir: "%s"' % old)
    news = w[1:]
    if len(news) == 1:
        mvline = ("mv -v --noclobber '{old}' '{new}' && ls -A '_empty/{new}' && echo 'Not Empty _empty/{new}' || rm -v -rf '_empty/{new}'".format(old=old, new=news[0]))
    else:
  	    for n, i in enumerate(news):
  	  	    print ('[%s]: "%s"' % (n, i))
        selection=int(input("Select One: ") or 0)
        mvline = ("mv -v --noclobber '{old}' '{new}' && ls -A '_empty/{new}' && echo 'Not Empty _empty/{new}' || rm -v -rf '_empty/{new}'".format(old=old, new=news[selection]))
    nlines.append(mvline)

with open('/tmp/rit_mv.txt', 'w+') as wf:
    wf.write('\n'.join(nlines))
```
