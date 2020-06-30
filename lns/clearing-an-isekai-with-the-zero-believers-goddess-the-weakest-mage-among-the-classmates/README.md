### scrape
```bash
for x in $(curl https://isekailunatic.com/clearing-an-isekai-with-the-zero-believers-goddess-the-weakest-mage-among-the-classmates/ | sed -n '/class="entry-content"/,/\.entry-content/p' | tr '"' '\n' | grep isekailunatic | grep '^https' | grep -v '.file\|not-a-chapter-a-new-story-on-the-side\|share'); do y=$(echo ${x%/} | awk -F '/' '{print $NF".htm"}'); echo "$x -> $y"; curl -L "$x" | sed -n '/class="entry-content"/,/ \.entry-content /p' > ./$y; done
```
### rename zfill
```bash
for i in $(ls *.htm); do n=$(echo $i | awk -F '-' '{printf("%03d", $3)}'); o=$(echo $i | awk -F '-' -v xx=$n '{$3=xx; print}' OFS=-); mv --no-clobber -v $i $o; done
```
### cleanup
```bash
sed -i '/__ATA.cmd.push/,/TwitterFacebook/d' *.md
```
### add navigate
```bash
nav_pre="[Table of Contents](./toc.md)"
chp_lst=($(ls -1 *chapter-*.md))
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
