### Rename the kets
#### Test
```bash
ls -1 | grep '^(C[0-9]{1,2})'
ls -1 | grep '^(C[0-9]{1,2})' | sed -nE 's/.*\((C[0-9]{1,2})\).*/\1/p'
ls -1 | grep '^(C[0-9]{1,2})' | sed -nE 's/.*\(C[0-9]{1,2}\)(.*)/\1/p'
Z=$(ls -1 | grep '^(C[0-9]{1,2})' | head -n 1 | sed -nE 's/.*\(C[0-9]{1,2}\)(.*)/\1/p')
echo "$Z" | sed -e 's/^[[:space:]]*//; s/[[:space:]]*$//'
Z=${Z%% }; Z=${Z## }; echo "$Z"
```
#### Cooking with uranium
```bash
IFS=$'\r\n'
CUR=$(pwd)
for X in $(ls -1 | grep '^(C[0-9]{1,2})'); do
K=$(echo "$X" | sed -nE 's/.*\((C[0-9]{1,2})\).*/\1/p')
cd "$X" && /home/alt/bin-sh/rnpa -p "${K## }" -s "_" ./*
cd "$CUR"
Y=$(echo "$X" | sed -nE 's/.*\(C[0-9]{1,2}\)(.*)/\1/p')
Y="${Y# }"
Y="${Y% }"
mv --no-clobber -v "$X" "$Y"
done
```
### img no-clobber
```bash
for Y in ${@}; do
    N=${Y##*/}
    case $N in
        [A-Za-z]*-[0-9]*[0-9]-*)
        D=$(echo "$N" | awk -F '-' '{print $2}')
        ;;
        [0-9]*)
        D=$(echo "$N" | awk -F '_' '{print $1}')
        ;;
        [a-z]*" "[0-9]*_*)
        D=$(echo "$N" | awk '{print $NF}' | awk -F '_' '{print $1}')
        ;;
        *)
        D="$N"
        ;;
    esac
    
    echo "Id=[$D]: $N"
    ls -1 *"$D"*
    if [ $(ls -1 *"$D"* | wc -l) -lt 0 ]; then
        echo "DUPLICATE"
    else
        echo "SAFE"
    fi
done
```
