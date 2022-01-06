### Check twitter for purged pics
```bash
mkdir -p ../_missing/
for a in $(find ./ -mindepth 1 -maxdepth 1 -type d); do
mkdir -v -p "$a/_purged/"
mkdir -v -p "$a/_done/"
b="/media/diskstation/download-imgs/img-boards/twitter.com/"$(echo "$a" | awk -F '/' '{print $NF}')
echo "Check:$a:$b"
if [ -d "$b" ]; then
for c in $(find "$a" -maxdepth 1 -type f | awk -F '/' '{split($NF,x," "); split(x[2],y,"."); print y[1]}' | sort -u); do
compgen -G "$b/*$c*" && mv -v "$a/"*$c* "$a/_done/" || mv -v "$a/"*$c* "$a/_purged/"
done
else
echo "NotIsDir:$b"
mv -v --no-clobber "$a" ../_missing/
fi
done
```
### Sync purged twitpics
```bash
mkdir -p ../___backed/
for x in $(ls -1); do
z="/media/diskstation/download-imgs/img-boards/twitter.com/${x%%/}"
for i in $(ls -1 "${x%%/}/_purged/"); do
y=$(echo "$i" | sed -E 's|(.*) orig(\..{3,4})|\1\2|; s|(.*)(\.[^\.]{3})|\1 purged\2|')
cp -v --no-clobber "${x%%/}/_purged/$i" "$z/$y"
done
done
```
### Consolidate garvure archives
```bash
find ./ -type f \( -name '*.zip' -o -name '*.rar' -o -name '*.7z' \) -not -path './_ARCHIVES/*' -not -path './Shinozaki*' -exec mv -v --no-clobber {} ./_ARCHIVES/ \;
find ./ -type f \( -name '*.zip' -o -name '*.rar' -o -name '*.7z' \) -not -path './_ARCHIVES/*' -not -path './Shinozaki*' -exec md5sum {} \; | tee -a /media/ramdisk/grav.txt
mkdir _dupes; IFS=$'\r\n'; for x in $(cat /media/ramdisk/grav.txt); do y=$(echo "$x" | awk '{print $1}'); z=$(echo "$x" | awk -F '/' '{print $NF}'); m=$(md5sum "./$z" | awk '{print $1}'); [ "$y" == "$m" ] && mv -v --no-clobber "$z" ./_dupes/ || echo "Mismatch:$z"; done
```