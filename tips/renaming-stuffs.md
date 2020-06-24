### Rename the kets
```bash
ls -1 | sed -nE 's/.*\((C[0-9]{1,2})\).*/\1/p'
```
```bash
IFS=$'\r\n'
CUR=$(pwd)
for X in $(ls -1); do
K=$(echo "$X" | sed -nE 's/.*\((C[0-9]{1,2})\).*/\1/p')
cd "$X" && /home/alt/bin-sh/rnpa -p "${K## }" -s "_" ./*
cd "$CUR"
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
