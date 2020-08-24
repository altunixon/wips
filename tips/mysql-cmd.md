### Queries
Search table by name
```sql
SELECT TABLE_NAME FROM information_schema.TABLES WHERE TABLE_NAME LIKE '%_x_%'
```
Rename Table [and more](https://www.techonthenet.com/mysql/tables/alter_table.php)
```sql
ALTER TABLE `official_art+order-popular&commit=Search` RENAME TO `official_art`;
```
Drop tables matching
```bash
mysql -uroot -proot -h127.0.0.1 -D mangadex -e "show tables" -s | grep '44115\|910399\|26301\|50074\|26401\|42020\|22715\|19526\|39828\|42409\|36258\|21699' | xargs -I "{}" echo mysql -uroot -proot -h127.0.0.1 -D mangadex -e "DROP TABLE {}" | tee -a /tmp/cull.sql

find /media/nfs/mounts-hub/download-miscs/img-manga-translated/ -type d -mtime -90 | grep '\]$' | tee /tmp/cull.txt
cat /tmp/cull.txt | awk -F '[' '{print $NF}' | cut -d ']' -f 1 | tee /tmp/cullsql.txt
for x in $(cat /tmp/cullsql.txt); do mysql -uroot -proot -h127.0.0.1 -D mangadex -e "show tables" -s | grep "$x" | xargs -I "{}" echo mysql -uroot -proot -h127.0.0.1 -D mangadex -e "DROP TABLE {}" | tee -a /tmp/cull.sql; done
```