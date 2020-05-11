### Scrape script
```bash
for i in $(curl https://yoraikun.wordpress.com/7s-chapters/ | tr '"' '\n' | grep 'sevens-' | sort | grep '^http.*/$'); do
      o=$(echo $i | awk -F '/' '{print $(NF-1)".htm"}'); 
      curl $i | sed -n '/class="entry-content"/,/\.entry-content/p' > $o;
done
```

### Convert to MarkDown
```bash
ls ./*.htm | html2md.py
```

### Add chapter title and relative links to MarkDown documents
```bash
IFS=$'\r\n'
nav_pre="toc.md"
nav_nxt=""
for m in $(ls -1 *.md); do
    h=$(grep -i '^[a-z0-9]' "$m" | head -n 1)
    t=$(echo "$h" | awk '{print tolower($0)}' | sed 's/ /-/g')
    o=$(echo "$m" | awk -F '.md' '{print $1}')
    f="${m}-${t}.md"
    sed -i "s/$h/### $h/" "$m"
    n="[< Previous <]($n)"
done
```
