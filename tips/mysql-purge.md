#### Set db_name variable
```bash
db_name="hfoundry"
sudo ls -1 "/media/alt/ramdisk1/maria/data/$db_name/" | awk -F '.' '{print tolower($1)}' | sort | uniq -c | grep -Ev '2 | db'

db_name="booru"
sudo ls -1 "/media/alt/ramdisk1/maria/data/$db_name/" | awk -F '.' '{print tolower($1)}' | sort | uniq -c | grep -Ev '2 | db'
```
#### Check primary key column of one table
```sql
SELECT key_column_usage.column_name
FROM   INFORMATION_SCHEMA.key_column_usage
WHERE  TABLE_SCHEMA = schema()
AND    CONSTRAINT_NAME = 'PRIMARY'
AND    TABLE_NAME = '<your-table-name>';
```
#### Or primary key of all tables
```sql
SELECT TABLE_NAME, COLUMN_NAME
FROM   INFORMATION_SCHEMA.key_column_usage
WHERE  TABLE_SCHEMA = '$db_name'
AND    CONSTRAINT_NAME = 'PRIMARY'
```
#### Should probly take a snapshot first
```bash
mysqldump -uroot -proot -h127.0.0.1 --single-transaction $db_name | gzip -c > "./${db_name}-snapshot.gz"
```
#### Then use following script to merge table new to old, then rename old to new
```bash
IFS=$'\r\n'
for x in $(sudo ls -1 "/media/alt/ramdisk1/maria/data/$db_name/" | awk -F '.' '{print tolower($1)}' | sort | uniq -c | grep -Ev '2 | db'); do
table_lowr=$(echo $x | awk '{print $NF}')
echo $table_lowr
table_uppr=$(echo "$table_lowr"  | python2 -c "print (raw_input().capitalize().strip())")
echo -e "INSERT IGNORE INTO ${db_name}.${table_uppr} (view, save) SELECT view, save FROM ${db_name}.${table_lowr};
DROP TABLE IF EXISTS ${db_name}.${table_lowr};
RENAME TABLE ${db_name}.${table_uppr} TO booru.${table_lowr};
" | tee -a "./${db_name}-purge.sql"
done
```
