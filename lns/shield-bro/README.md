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
- Add Navigation
    ```bash
    nav_pre="[Table of Contents](./toc.md)"
    chp_lst=($(ls -1 *.md))
    n_f=$((${#chp_lst[@]} - 1))
    for n_i in $(seq 0 $n_f); do
        chp_now="${chp_lst[$n_i]}"
        if [ $n_i -lt $n_f ]; then
            nav_nex=$"${chp_lst[$((n_i + 1))]}"
        else
            nav_nex="[Table of Contents](./toc.md)"
        fi
        echo -e "${nav_pre} | ${nav_nex} <br/>\n$(cat ${chp_lst[$n_i]})\n${nav_pre} | ${nav_nex} <br/>\n" > "${chp_lst[$n_i]}"
        chp_new=$(echo "$chp_now" | awk -F '|' '{print $1}')
        mv --no-clobber -v "${chp_lst[$n_i]}" "${chp_new%% }"
        nav_pre="$chp_now"
    done
    ```
