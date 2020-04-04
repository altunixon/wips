for x in $(seq 1 9); do
xx=($(curl "https://www.novelupdates.com/series/sevens-ln/?pg=$x" | tr '<' '\n' | grep 'class="chp-release"' | awk -F '"' '{print $2"|https:"$6}'))
for y in ${xx[@]}; do
echo $y
i=$(echo $y | awk -F '|' '{print $2}')
o=$(echo $y | awk -F '|' '{print $1}')
curl -L $i | sed -n '/class="entry-content"/,/id="comments"/p' > "${o}.htm"
done
done