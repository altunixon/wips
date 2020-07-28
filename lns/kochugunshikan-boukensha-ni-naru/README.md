### Scrape
```bash
for x in $(curl https://lightnovelstranslations.com/the-galactic-navy-officer-becomes-an-adventurer/ | sed -n '/class="entry-content"/,/\.entry-content/p' | tr '"' '\n' | grep 'the-galactic-navy-officer-becomes-an-adventurer'); do y=$(echo "${x%/}" | awk -F '/' '{print $NF".htm"}'); curl "$x" | sed -n '/class="entry-content"/,/\.entry-content/p' > "$y"; done
```
### Zfill
```bash
for x in $(ls chapter-*.md); do n=$(echo "$x" | awk -F '-' '{printf("-%03d-", $2)}'); z=$(echo "$x" | awk -F '-' '{print "-"$2"-"}'); y=$(echo "$x" | sed "s/$z/$n/"); mv --no-clobber -v "$x" "$y"; done
```
### Link
```bash
nav_pre="[Table of Contents](./toc.md)"
chp_lst=($(ls -1 chapter-*.md))
n_f=$((${#chp_lst[@]} - 1))
for n_i in $(seq 0 $n_f); do
    chp_now=${chp_lst[$n_i]}
    chp_nex=${chp_lst[$((n_i + 1))]}
    if [ $n_i -lt $n_f ]; then
        nav_nex="[$chp_nex](./$chp_nex)"
    else
        nav_nex="[Table of Contents](./toc.md)"
    fi
    echo -e "${nav_pre} | ${nav_nex} <br/>\n$(cat $chp_now) <br/>\n${nav_pre} | ${nav_nex} <br/>" > "$chp_now"
    nav_pre="[$chp_now](./$chp_now)"
done
```