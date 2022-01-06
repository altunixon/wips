### 3226070-higashi\_taishi-東太子
```bash
unar 3226070-higashi_taishi-東太子.zip
IFS=$'\r\n'; for x in $(ls -1); do y=$(echo "$x" | sed -nE 's/(^[0-9]*)_([^0-9].*)_([0-9]*_p[0-9]{1,2}\.[a-z]{3,4})/\1_\3/p'); [ ! -z "$y" ] && mv -v --no-clobber "$x" "$y"; done
```

### seura\_isago
```bash
IFS=$'\r\n'; for x in $(grep -v "\]/$" seu.txt | sed 's/\///g'); do y=$(zcat ex.gz | grep -F "$x" | sed -nE "s/.*COMMENT='.*\/g\/(.*\/.*)\/ (.*)';.*/\2 \[\1\]/p" | sed 's/\//_/g'); echo "${x}|${y}" | tee -a seu-id.txt; done
IFS=$'\r\n'; for x in $(cat seu-id.txt); do y=$(echo "$x" | sed -nE 's/^\(([^)]*)\) ?.*/\1/p'); z=$(echo "$x" | sed -nE 's/.* \[(.*_.*)\]$/\1/p'); i=$(echo "$x" | awk -F '|' '{print $1}'); if [ ! -z "$y" ]; then for o in $(grep -F "$y" seu-re.txt | sed 's/\///g'); do echo "${i}|${o} [${z}]" | tee -a seu-fin.txt; done; fi; done
```

### rit
```bash
ls -1 rit/ | tee /tmp/rit-ls.txt
ls -1 rit/empty | tee -a /tmp/rit-ls.txt
k=($(grep '^(' z.txt | sed -nE 's/^\(([^\)]*)\).*/\1/p' | sort -u))
IFS=$'\r\n'; for v in ${k[@]}; do n=($(grep -F "$v" /tmp/rit-ls.txt)); [ ${#n[@]} -ge 2 ] && echo "${n[0]}|${n[1]}" | tee -a /tmp/rit-paired.txt; done
sed -i 's/\///g' /tmp/rit-paired.txt
zcat rit.gz > rit-sql.txt
for z in $(cat /tmp/rit-paired.txt); do m=$(echo "$z" | awk -F '|' '{print $1}'); n=$(echo "$z" | awk -F '|' '{print $NF}'); o=$(grep -F "$m" rit-sql.txt | sed -nE "s/^INSERT INTO .(.*). VALUES.*/\1/p" | sed 's/\//_/g' | head -n 1); echo "mv -v --no-clobber '$m' '${n} [${o}]'" | tee -a rit-fix.txt; done
```
```python
with open('/tmp/rit_merged.txt', 'r') as rf:
    rlines=[x.strip('\n') for x in rf.readlines() if '|' in x and not x.startswith('#')]

nlines = []
for z in rlines:
    w=z.split('|')
    old = w[0]
    print ('OLD Dir: "%s"' % old)
    news = w[1:]
    if len(news) == 1:
        mvline = ("mv -v --noclobber '{old}' '{new}' && ls -A '_empty/{new}' && echo 'Not Empty _empty/{new}' || rm -v -rf '_empty/{new}'".format(old=old, new=news[0]))
    else:
        for n, i in enumerate(news):
            print ('[%s]: "%s"' % (n, i))
        selection=int(input("Select One: ") or 0)
        mvline = ("mv -v --noclobber '{old}' '{new}' && ls -A '_empty/{new}' && echo 'Not Empty _empty/{new}' || rm -v -rf '_empty/{new}'".format(old=old, new=news[selection]))
    nlines.append(mvline)

with open('/tmp/rit_mv.txt', 'w+') as wf:
    wf.write('\n'.join(nlines))
```

## rename using mysql \_\_toc\_\_
```bash
ls -1pv | sed -nE 's/.* \[([^]]*)]\/$/\/g\/\1/p' | sed 's/_/\//g'
IFS=$'\r\n'; for x in $(ex-asearch hirofumi exh); do y=($(echo "$x" | sed 's/\// /g; s/|/\n/g')); z="${y[0]} [${y[2]}]"; echo "[ -d '${y[1]}' ] && mv -v --no-clobber '${y[1]}' '${z%% }'"; done | tee /media/ramdisk/nkh.txt
IFS=$'\r\n'; for x in $(ex-asearch xxzero exh); do y=($(echo "$x" | sed 's/\// /g; s/:/ /g; s/|/\n/g')); [ "${y[0]}" != "None" ] && z="${y[0]} [${y[2]}]" || z="${y[1]} [${y[2]}]"; echo -e "[ -d '${y[1]}' ] && mv -v --no-clobber '${y[1]}' '${z%% }'\n[ -d '${y[0]}' ] && mv -v --no-clobber '${y[0]}' '${z%% }'"; done | tee /media/ramdisk/xx.txt
IFS=$'\r\n'; for x in $(mysql-dlview '192.168.11.61:python:anaconda:exhg_nexus' artists __toc__ isako_rokuroh alt | sed 's/'"'"'/ /g; s/"/ /g; s/\/$//'); do readarray  -d '|' y <<< "$x"; z=$(echo "${y[2]}" | tr -d '\n' | awk -F '/' '{print $(NF-1)"_"$NF}'); [[ "${y[0]%%|}" != "None" && "${y[0]%%|}" != "${y[1]%%|}" ]] && echo "[ -d '${y[1]%%|} [${z}]' ] && mv -v --no-clobber '${y[1]%%|} [${z}]' '${y[0]%%|} [${z}]'" | tee -a ./nfix.txt; done
```

## grep sqldump
```bash
grep -F 'Kangoku Buta' /media/ramdisk/x.txt | awk -F '\\)\\,\\(' '{print $1}' | sed -nE 's/^INSERT .*`(.*)` .*.,.\/.*\/(\[.*)\/.*/mv -v --no-clobber "\2" "\2 [\1]"/p'
```

## Dupicate dirs
```bash
ls | grep あおいまなぶ
mkd ../img-exhg/aoi_manabu/__fix
mv *あおいまなぶ* ../img-exhg/aoi_manabu/__fix
cd ../img-exhg/aoi_manabu/__fix
IFS=$'\r\n'; for x in $(ls -1); do [ -d "../${x}" ] && mv -v --no-clobber "../${x%%/}"/* "./${x}"; done
find ../ -mindepth 1 -maxdepth 1 -empty -exec mv {} /tmp/recyclebin/ \;
mv ./* ../
cd ..
rm -rf __fix/

function ck ()
{
    mkdir -pv "../img-exhg/${2}" && mv --no-clobber -v ./*"${1}"* "../img-exhg/${2}";
    sed -i "/${1}/d" /media/ramdisk/ck.txt
}
```
