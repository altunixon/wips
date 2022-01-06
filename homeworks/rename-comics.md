### Rename the kets
#### Test (FOR GODS SAKE! PLEASE DO THIS FIRST)
- COMIKET: </br>
```bash
ls -1 | grep -E '^\(C[0-9]{1,2}\)'
ls -1 | grep -E '^\(C[0-9]{1,2}\)' | sed -nE 's/.*\((C[0-9]{1,2})\).*/\1/p'
ls -1 | grep -E '^\(C[0-9]{1,2}\)' | sed -nE 's/.*\(C[0-9]{1,2}\)(.*)/\1/p'
Z=$(ls -1 | grep -E '^\(C[0-9]{1,2}\)' | head -n 1 | sed -nE 's/.*\(C[0-9]{1,2}\)(.*)/\1/p')
echo "$Z" | sed -e 's/^[[:space:]]*//; s/[[:space:]]*$//'
Z=${Z%% }; Z=${Z## }; echo "$Z"
```
- General DJ (COMIC1 & Tanks): `'s/^\([^)]*\) ?(.*)/\1/p' = 's/(^\([^)]*\)) ?(.*)/\2/p'`
```bash
ls -1 | grep -E '^\('
ls -1 | grep -E '^\(' | sed -nE 's/^\(([^)]*)\) ?.*/\1/p; s/[\d128-\d255]/-/g'
ls -1 | grep -E '^\(' | sed -nE 's/^\([^)]*\) ?(.*)/\1/p'
Z=$(ls -1 | grep -E '^\(' | head -n 1 | sed -nE 's/(^\([^)]*\)) ?(.*)/\2/p')
echo "$Z" | sed -e 's/^[[:space:]]*//; s/[[:space:]]*$//'
Z=${Z%% }; Z=${Z## }; echo "$Z"
```
#### Cooking with uranium
- COMIKET:
```bash
IFS=$'\r\n'
for X in $(ls -1 | grep -E '^\(C[0-9]{1,2}\)'); do
K=$(echo "$X" | sed -nE 's/.*\((C[0-9]{1,2})\).*/\1/p')
/home/alt/bin-py/utils/rnpa.py -p "${K## }" -d "_" "$X"/*
Y=$(echo "$X" | sed -nE 's/.*\(C[0-9]{1,2}\)(.*)/\1/p')
Y=$(echo "$Y" | sed -e 's/^[[:space:]]*//; s/[[:space:]]*$//')
mv --no-clobber -v "$X" "$Y"
echo "mv -v --no-clobber \"$Y\" \"$X\"" >> /tmp/CXX_undo.txt
done
```
- General DJ \(remove first round brackets, no rnpa\):
```bash
IFS=$'\r\n'
CUR=$(pwd)
for X in $(ls -1 | grep -E '^\([^)]*\) ?'); do
K=$(echo "$X" | sed -nE 's/^\(([^)]*)\) ?(.*)/\1/p; s/[\d128-\d255]/-/g')
Y=$(echo "$X" | sed -nE 's/(^\([^)]*\)) ?(.*)/\2/p')
Y=$(echo "$Y" | sed -e 's/^[[:space:]]*//; s/[[:space:]]*$//')
mv --no-clobber -v "$X" "$Y"
echo "mv '$Y' '$X'" >> /tmp/CXX_undo.txt
done
```
### Find duplicate image by ID (the dumb way)
```bash
for Y in ${@}; do
    N=${Y##*/}
    case $N in
        [A-Za-z]*-[0-9]*[0-9]-*) # HF
        D=$(echo "$N" | awk -F '-' '{print $2}')
        ;;
        [0-9]*) # Pixiv?
        D=$(echo "$N" | awk -F '_' '{print $1}')
        ;;
        [a-z]*" "[0-9]*_*) # Twitter?
        D=$(echo "$N" | awk '{print $NF}' | awk -F '_' '{print $1}')
        ;;
        *) # Everything Else
        D="$N"
        ;;
    esac
    
    echo "Id=[$D]: $N"
    ls -1 *"$D"*
    if [ $(ls -1 *"$D"* | wc -l) -lt 0 ]; then
        echo "DUPLICATE"
    else
        echo "UNIQ"
    fi
done
```
### Trailing spaces trimming
```bash
var='   space test   '
echo $var | sed -n -e 'l'
echo "$var" | sed -n -e 'l'

printf "%s" "${var#"${var%%[![:space:]]*}"}" | sed -n -e 'l'
printf "%s" "${var%"${var##*[![:space:]]}"}" | sed -n -e 'l'


# Space characters include: tab, newline, vertical tab, form feed, carriage return, and space.
# cf. "POSIX character classes" at http://en.wikipedia.org/wiki/Regular_expression

var="${var#"${var%%[![:space:]]*}"}"   # remove leading whitespace characters
var="${var%"${var##*[![:space:]]}"}"   # remove trailing whitespace characters

echo "$var" | sed -n -e 'l'
```
### Rename pixivs
```bash
find ./ -type f
head pixi-mutou.txt | awk -F '/' '{n=split($NF, x, "_"); a=x[1]; b=x[2]; split(x[3], y, "-"); c=y[1]; l=split(x[(n)], z, "."); d=z[l]; $NF=""; print $0 a"_"b"_"c"."d}' | sed 's/ /\//g'
for x in $(cat pixi-mutou.txt); do
y=$(echo "$x" | awk -F '/' '{n=split($NF, x, "_"); a=x[1]; b=x[2]; split(x[3], y, "-"); c=y[1]; l=split(x[(n)], z, "."); d=z[l]; $NF=""; print $0 a"_"b"_"c"."d}' | sed 's/ /\//g');
mv -v --no-clobber "$x" "$y";
done
```
### Migrate xtracts
- On Source: `find ./ -mindepth 2 -type d | tee -a /tmp/src.txt; scp /tmp/src.txt dest:/tmp/`
- On Dest:
```bash
IFS=$'\r\n'
for x in $(cat /tmp/src.txt); do
y=$(echo "$x" | awk -F '/' '{print $2}')
z=$(echo "$x" | awk -F '/' '{print $NF}')
[ ! -d "$y" ] && mkdir "$y"
[ -d "$z" ] && mv -v --no-clobber "$z" "./${y}/"
done
```
- Extra check renamed stuffs:
```
for x in $(cat /tmp/src.txt); do
y=$(echo "$x" | awk -F '/' '{print $2}')
z=$(echo "$x" | awk -F '/' '{print $NF}' | sed -nE 's/^\([^[].*(\[.*)/\1/p')
if [ ! -z "$z" ] && [ -d "$z" ]; then
    mv -v --no-clobber "$z" "./${y}/"
fi
done
```
### Sync clips
```bash
for x in $(ls -1 *.mp4); do y=$(echo "$x" | awk '{print $NF}'); echo "$y:$x" | tee -a /tmp/clips.txt; done
for x in $(cat /tmp/clips.txt); do y=$(echo "$x" | awk -F ':' '{print $1}'); z=$(echo "$x" | awk -F ':' '{print $NF}'); if [ ! -z "$z" ]; then o=$(compgen -G '*'"$y"); if [ ! -z "$o" ] && [ "$o" != "$z" ]; then mv -v --no-clobber "$o" "$z"; else echo "EXISTS:$o"; fi; fi; done
```

