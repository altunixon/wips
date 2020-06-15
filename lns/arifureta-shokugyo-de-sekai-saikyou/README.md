[Table of Contents](./toc.md) | [180-morning-at-the-nagumo-house-part-1.md](./arifureta-chapter-180-morning-at-the-nagumo-house-part-1.md) <br/>
#### Scrape
```bash
IFS=$'
'; for x in $(curl https://bakapervert.wordpress.com/arifureta-shokugyo-de-sekai-saikyou/ | tr '<' '
' | grep '^a' | grep 'Arifure' | grep -v bookwalker | awk -F '"' '{print $2"|"$3}'); do link=$(echo "$x" | awk -F '|' '{print $1}'); name=$(echo "$x" | awk -F '>' '{print tolower($NF)}' | sed 's/&#8211\;/ /g; s/&#8217\;/ /g; s/ &amp\; / /g; s/[①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳…\?\!,\(\)\~–]//g; s/arifureta after //g; s/’/-/g; s/ /-/g; s/ //g; s/---/-/g; s/--/-/g'); name=${name%%-}; name=${name##-}; htm=$(echo "$link" | awk -v title=$name -F '/' '{print $(NF-1)"-"title".htm"}'); curl $link | sed -n '/class="entry-content"/,/-- \.entry-content --/p' > $htm; done
```
#### Cleanup
```bash
rm arifureta-382-arifureta-382.htm
mv arifureta{,-chapter}-290-finished-iii-shia-arc-yes-with-pleasure.htm
for i in $(ls | grep '&amp;'); do o=$(echo "$i" | awk -F '&amp;' '{print $1"-"$2}'); mv "$i" "$o"; done
``` <br/>
[Table of Contents](./toc.md) | [180-morning-at-the-nagumo-house-part-1.md](./arifureta-chapter-180-morning-at-the-nagumo-house-part-1.md) <br/>
