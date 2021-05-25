### Using mysql2sqlite scripts
Which are basically a "cat dump.sql | awk | sqlite3 into.sqlite", allegedly doesn't work great with UTF-8\)</br>
**awk, newer: \[[mysql2sqlite]\]**
```bash
mysqldump --skip-extended-insert --compact -u root -p root -h localhost booru > booru.sql
awk mysql2sqlite booru.sql | sqlite3 booru.sqlite
```
**sh wrapper: \[[mysql2sqlite.sh]\]**
```bash
mysql2sqlite.sh -u root -p root -h localhost booru | sqlite3 booru.sqlite
```
**\[[mysql-forum]\]** A quick way to convert a MySQL DB to SQLite3 is the following shell script (it does not claim to be complete):
```bash
mysqldump --compact --compatible=ansi --default-character-set=binary -u root -p root -h localhost booru | \
grep -v ' KEY "' | \
grep -v ' UNIQUE KEY "' | \
perl -e 'local $/;$_=<>;s/,\n\)/\n\)/gs;print "BEGIN;\n";print;print "COMMIT;\n"' | \
perl -pe '
if (/^(INSERT.+?)\(/) {
$a=$1;
s/\\'\''/'\'\''/g;
s/\\n/\n/g;
s/\),\(/\);\n$a\(/g;
}
' | \
sqlite3 booru.sqlite
```
### Using [mysql-to-sqlite3] python package
```bash
pip install mysql-to-sqlite3
mysql2sqlite -u root -p root -h localhost -P 3306 -d booru -f booru.sqlite --vacuum
```
Optional: convert sqlite to mysql with [sqlite3-to-mysql] package
```bash
pip install sqlite3-to-mysql
sqlite3mysql -u root -p root -h localhost -P 3306 -d booru -f booru.sqlite
```


[mysql2sqlite]: https://github.com/dumblob/mysql2sqlite/blob/master/mysql2sqlite
[mysql2sqlite.sh]: https://gist.github.com/esperlu/943776
[mysql-forum]: https://forums.mysql.com/read.php?145,68269,92627#msg-92627
[mysql-to-sqlite3]: https://pypi.org/project/mysql-to-sqlite3/
[sqlite3-to-mysql]: https://pypi.org/project/sqlite3-to-mysql/
