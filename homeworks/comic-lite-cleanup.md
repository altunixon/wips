### Find files with suspicious size
```bash
find ./ -type f -size -10 | tee -a /volume1/storage/clite-10.txt
grep -v '/_broken\|.htm$\|@eaDir'clite-10.txt > clite-fix.txt
vim clite-fix.txt
:%s/^./\/media\/ds416slim\/download-cgs\/comics-lite/
```
### Generate action files
```bash
for x in $(grep -v '^#' clite-empty-noea.txt); do
  x_dat=$(echo "$x" | awk -F '/' '{print $(NF-1)":"$NF}')
  x_tbl=$(echo "$x_dat" | sed -nE 's/.* \[(.*)\]\:.*/\1/p')
  x_sav=$(echo "$x_dat" | awk -F ':' '{print $NF}')
  echo "DELETE FROM \`$x_tbl\` WHERE save LIKE \"%$x_sav%\";" | tee -a /media/ramdisk/clite-cleanup.sql
  x_red=$(echo "$x_tbl" | sed 's/_/\//')
  grep -rI "$x_red" /home/alt/git-repo/txt-lists/ | tee -a /media/ramdisk/clite-redl.txt
done
sort clite-redl.txt | uniq | awk -F ':' '{print "https:"$NF}' > comic-lite-fix.txt
```
### Also cleanup broken files
```bash
grep '/_broken' clite-10.txt > clite-brok.txt
for x in $(cat clite-brok.txt); do
  x_dat=$(echo "$x" | awk -F '/' '{print $(NF-1)":"$NF}')
  x_tbl=$(echo "$x_dat" | sed -nE 's/.* \[(.*)\]\:.*/\1/p')
  x_sav=$(echo "$x_dat" | awk -F ':' '{x=split($NF, y, "-"); print y[2]"-"y[3]}')
  echo "DELETE FROM \`$x_tbl\` WHERE save LIKE \"%${x_sav%%.*}%\";" | tee -a /media/ramdisk/clite-cleanup-brok.sql
  x_red=$(echo "$x_tbl" | sed 's/_/\//')
  grep -rI "$x_red" /home/alt/git-repo/txt-lists/ | tee -a /media/ramdisk/clite-rebrok.txt
done
sort clite-rebrok.txt | uniq | awk -F ':' '{print "https:"$NF}' > comic-brok-fix.txt
```
