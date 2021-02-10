### Cleanup
```bash
x=($(mysql -uroot -proot -h127.0.0.1 -e 'SELECT TABLES FROM booru;' | awk '{print $2}'))
echo ${x[@]} | grep -v ^[a-z]
echo ${x[@]} | grep -v ^[a-z] | xargs -I {} bash -c 'mysql -uroot -proot -h127.0.0.1 -e "DROP TABLE booru.$1"' -- {}
```
### Repair and Optimize
mysql command
```mysql
# For each table
REPAIR TABLE table_name;
OPTIMIZE TABLE table_name;
```
mysqlcheck tool
```bash
mysqlcheck -u root -p --auto-repair --optimize --all-databases
```
also see [mysql-compression](https://github.com/altunixon/wips/blob/master/tips/mysql-compression.md) for client side compression
### Change mysql config
stop mysql server
```bash
docker stop maria-server
```
Add to my.cnf
```bash
[client]
default-character-set = utf8mb4

[mysql]
default-character-set = utf8mb4

[mysqld]
character-set-client-handshake = FALSE
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci
```
start mysql server
```bash
docker start maria-server
```
