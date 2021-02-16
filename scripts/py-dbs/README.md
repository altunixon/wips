### Docker MySQL 5.7
```bash
docker pull mysql:5.7
cat << EOT >> /media/$USER/ramdisk1/mysql/conf/my.cnf
[mysql]
default-character-set = utf8mb4

[mysqld]
character-set-client-handshake = FALSE
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci
init_connect='SET NAMES utf8mb4'
loose-default-character-set = utf8mb4
innodb_file_per_table = ON
innodb_file_format = Barracuda
innodb_page_size = 8KB
optimizer_search_depth = 0
innodb_buffer_pool_size = 134217728

[client]
default-character-set = utf8mb4
loose-default-character-set = utf8mb4
EOT
docker run --detach --name mysql-57 -d mysql:5.7 \
  -v /media/$USER/ramdisk1/mysql/conf:/etc/mysql/conf.d \
  -v /media/$USER/ramdisk1/mysql/data:/var/lib/mysql \
  -e "MYSQL_ROOT_PASSWORD=root" \
  --user 1033:1033 \
  --port 3306:3306 \
  --sysctl net.ipv6.conf.all.disable_ipv6=1 \
  --character-set-server=utf8mb4 \
  --collation-server=utf8mb4_unicode_ci
```
### Patch
```bash
for x in $(ls ./*.py); do
  if [ -f ~/git-repo/script-python3/databases/$x ]; then
    ../patchme.sh ~/git-repo/script-python3/databases/$x $x
  else
    cp $x ~/git-repo/script-python3/databases/
  fi
done
```
