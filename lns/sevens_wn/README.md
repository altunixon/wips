### Scrape
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

function name_proc() {
    md_title=$(grep -i '^[a-z0-9]' "$1" | head -n 1 | sed 's/\<br\/\>//g')
    md_lower=$(echo "$md_title" | awk '{print tolower($0)}' | sed 's/ /-/g')
    md_name=$(echo "$1" | awk -F '.md' '{print $1}')
    md_out="${md_name%%-}-${md_lower##-}.md"
    md_lnk="[${md_name}: ${md_title}](./${md_out})"
    case $2 in
    name) echo -n "${md_out}";;
    link) echo -n "${md_lnk}";;
    *) echo -n "${md_out}|${md_lnk}";; 
    esac
}

nav_pre="[Table of Contents](./toc.md)"
chp_lst=$(ls -1 *.md)
n_f=$((${#chp_lst[@]} - 1))
for n_i in $(seq 0 $n_f); do
    chp_cur=$(name_proc "${chp_lst[$n_i]}" both)
    if [ $n_i -lt $n_f ]; then
        nav_nex=$(name_proc "${chp_lst[$((n_i + 1))]}" link)
    else
        nav_nex="[Table of Contents](./toc.md)"
    fi
    echo "${nav_pre} | ${nav_nex} <br/>" >> "${chp_lst[$n_i]}"
    chp_new=$(echo "$chp_cur" | awk -F '|' '{print $1}')
    mv --no-clobber -v "${chp_lst[$n_i]}" "${chp_new%% }"
    nav_pre=$(echo "$chp_cur" | awk -F '|' '{print $2}')
done
```
