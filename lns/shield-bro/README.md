#### Scrape
- Test
    ```bash
    curl https://yoraikun.wordpress.com/tny-chapters/ | \
        sed -n '/div class="entry-content"/,/id="jp-post-flair"/p' | \
        tr '<' '\n' | grep '^a ' | awk -F 'href=' '{print $2}' | awk -F '"' '{print $2}'
    curl https://yoraikun.wordpress.com/tny-chapters/ | \
        sed -n '/div class="entry-content"/,/id="jp-post-flair"/p' | \
        tr '<' '\n' | grep '^a ' | sed -n 's/href="(http.*)"/\1/p
    curl https://yoraikun.wordpress.com/tny-chapters/ | \
        sed -n '/div class="entry-content"/,/id="jp-post-flair"/p' | \
        tr '<' '\n' | grep '^a ' | awk -F '>' '{print tolower($NF)}' | \
        sed 's/\:/ /g, s/&#8211; //g, s/  / /g, s/ /-/g'
    curl "http://pastebin.com/raw/kB1n5bWG" | sed 's/\n/<\/br>\n/g'
    curl "http://www.baka-tsuki.org/project/index.php?title=Tate_no_Yuusha:Web_Chapter_22"
    curl "https://yoraikun.wordpress.com/2014/11/15/the-rise-of-the-shield-hero-chapter-155/" | \
        sed -n '/class="entry-content"/,/\.entry-content/p'
    curl "http://bakahou.wordpress.com/2014/10/15/chapter-102-hero-conference-during/" | \
        sed -n '/class="entry-content"/,/\.entry-content/p'
    curl "http://ohanashimi.wordpress.com/2014/11/10/hero-of-shield-ch-148-failed-creation/" | \
        sed -n '/class="entry-content"/,/\.entry-content/p'
    ```
- Main
    ```bash
    IFS=$'\r\n'
    for i in $(curl https://yoraikun.wordpress.com/tny-chapters/ | sed -n '/div class="entry-content"/,/id="jp-post-flair"/p' | tr '<' '\n' | grep '^a ' | grep -v 'youtube\|facebook\|twitter'); do
        c_link=$(echo "$i" | awk -F 'href=' '{print $2}' | awk -F '"' '{print $2}')
        c_name=$(echo "$i" | awk -F '>' '{print tolower($NF)}' | sed 's/\:/ /g; s/&\#8211\; //g; s/&#8217\;/ /g; s/  / /g; s/ /-/g; s/--/-/g')
        case $c_link in
        *pastebin*)
            c_id=$(echo "${c_link%/}" | awk -F '/' '{print $NF}')
            curl -L "http://pastebin.com/raw/$c_id" > "./${c_name}_${c_id}.txt"
        ;;
        *tsuki*)
            curl -L "$c_link" > "./${c_name}-baka-tsuki.html"
        ;;
        *wordpress*)
            curl -L "$c_link" | sed -n '/class="entry-content"/,/\.entry-content/p' > "./${c_name}.htm"
        ;;
        esac
    done
    ```
- Z-fill
    ```bash
    for x in $(ls -1 *.md); do
        w=$(echo "$x" | awk -F '-' '{print $2}')
        z=$(echo "$x" | awk -F '-' '{printf("%03d", $2)}')
        y=$(echo "$x" | sed "s/-$w-/-$z-/; s/-&amp\;-/-&-/")
        [ "$y" != "$x" ] && mv --no-clobber -v "$x" "$y"
    done
    ```
- Add Navigation
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
- Redo Navigation
  Remove current links
    ```bash
    ls -1 chapter-*.md | xargs -I {} sed -i '/[chapter-/d' "{}"
    ```
  Re-run add navigation process descrived above

