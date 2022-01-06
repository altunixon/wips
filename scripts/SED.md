#### replacing last occurrence
```bash
$ # can also use sed -E 's/:([^:]*)$/-\1/'
$ echo 'foo:123:bar:baz' | sed -E 's/(.*):/\1-/'
foo:123:bar-baz
$ echo '456:foo:123:bar:789:baz' | sed -E 's/(.*):/\1-/'
456:foo:123:bar:789-baz
$ echo 'foo and bar and baz land good' | sed -E 's/(.*)and/\1XYZ/'
foo and bar and baz lXYZ good
```
#### use word boundaries as necessary - GNU sed
```bash
$ echo 'foo and bar and baz land good' | sed -E 's/(.*)\band\b/\1XYZ/'
foo and bar XYZ baz land good
```
#### replace with positioning
```bash
$ # replacing last but one
$ echo 'foo:123:bar:baz' | sed -E 's/(.*):(.*:)/\1-\2/'
foo:123-bar:baz
$ echo '456:foo:123:bar:789:baz' | sed -E 's/(.*):(.*:)/\1-\2/'
456:foo:123:bar-789:baz
$ # replacing last but two
$ echo '456:foo:123:bar:789:baz' | sed -E 's/(.*):((.*:){2})/\1-\2/'
456:foo:123-bar:789:baz
$ # replacing last but three
$ echo '456:foo:123:bar:789:baz' | sed -E 's/(.*):((.*:){3})/\1-\2/'
456:foo-123:bar:789:baz
```
#### hfmigrate view
```bash
mysql -uroot -proot -h127.0.0.1 -e "SELECT view, save from hfoundry._lite WHERE view REGEXP '^[0-9]+$';" | tee /media/ramdisk/hf.txt
IFS=$'\r\n'; for x in $(cat /media/ramdisk/hf.txt); do echo "$x" | sed -nE 's/.*\/(.*)-([0-9][^-]*)-.*/UPDATE hfoundry._lite SET view="\1_\2" WHERE view="\2"\;/p') | tee -a /media/ramdisk/hf.sql; done
#; viewid_format: <artist>_<id>
ls *.{jpg,png,gif} | sed -nE 's/.*\/(.*)-([0-9][^-]*)-.*/INSERT IGNORE INTO hfoundry._lite (view, save) VALUES ("\1_\2", "\0");/p' | tee -a /media/ramdisk/xx.sql
#; viewid_format: <id>
find /media/diskstation/download-imgs/img-boards/www.hentai-foundry.com -not -path '@'* -type f | sed -nE 's/.*\/.*-([0-9]*)-.*/INSERT IGNORE INTO hfoundry._lite (view, save) VALUES ("\1", "\0");/p' | tee -a /media/ramdisk/xxx.sql
#; fix stuffs
mysql -uroot -proot -h127.0.0.1 -e "SELECT view, save from hfoundry._lite WHERE view NOT REGEXP '^[0-9]+$';"  | awk '{print $NF}' | sed -nE 's/.*\/.*-([0-9]*)-.*/INSERT IGNORE INTO hfoundry._lite (view, save) VALUES ("\1", "\0");/p' > /media/ramdisk/x.sql
```
