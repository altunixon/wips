#### Scrape yAmi
```bash
for x in $(curl https://www.yamitranslations.com/p/ouroboros-record-circus-of-oubeniel_62.html | tr '<' '\n' | grep '^a ' | grep 'Chapter ' | grep -v 'oubeniel_62.html\|regarding-\|resume-' | sed "s/&lt\;/\[/g; s/&gt\;/\]/g; s/['\?]//g" | awk -F '"' '{print $2 tolower($3)}'); do l=$(echo "$x" | awk -F '>' '{print $1}' | sed 's/http:/https:/g'); n=$(echo "$x" | awk -F '>' '{print $2}'); o=$(echo "${n%% }.htm" | sed 's/ /-/g; s/://g; s/---/-/g'); echo $l; curl $l | sed -n '/entry-content/,/class="post-footer"/p' > $o; done
```
#### Scrape sychev
```bash
for x in $(curl https://knightsoflunadia.wordpress.com/ouroboros-records-circus-of-oubeniel/ | tr '"' '\n' | grep 'ouroboros' | grep -v 'ouroboros-records-circus-of-oubeniel\|comment-' | sort -u); do n=$(echo "${x%%/}" | awk -F '/' '{print $NF}' | sed 's/ouroboros-record-//g; s/ouroboros-records-//g'); echo $x; curl $x | sed -n '/class="entry-content"/,/-- \.entry-content --/p' > "${n}.htm"; done

```
#### Zfill
```bash
for x in $(ls -1 ./chapter-*); do w=$(echo "$x" | awk -F '-' '{print $2}'); z=$(echo "$x" | awk -F '-' '{printf("%03d", $2)}'); echo "s/-$w-/-$z-/"; y=$(echo "$x" | sed "s/-$w-/-$z-/"); [ "$y" != "$x" ] && mv --no-clobber -v "$x" "$y"; done
```