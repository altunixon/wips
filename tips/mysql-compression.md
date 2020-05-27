
### MySQL/MariaDB
**Query below returns the size of each Database in MB.**
```sql
SELECT table_schema 
 "DB Name", Round(Sum(data_length + index_length) / 1024 / 1024, 1) "DB Size in MB"
 FROM information_schema.tables
 GROUP BY table_schema;
```
**Query below returns the size of each Table in MB.**
```sql
SELECT table_schema
 AS `Database`,table_name AS `Table`,round(((data_length + index_length) / 1024 / 1024), 2) `Size in MB`
 FROM information_schema.TABLES
 ORDER BY (data_length + index_length) DESC
 LIMIT 5;
```
### InnoDB Enabling Table Compression [MariaDB](https://mariadb.com/kb/en/innodb-page-compression/)/[MySQL](https://dev.mysql.com/doc/refman/5.7/en/innodb-compression.html)
- my.cnf:
  - innodb_file_per_table = ON
  - innodb_file_format = Barracuda
  - [innodb_page_size = 16384](https://mariadb.com/kb/en/innodb-system-variables/#innodb_page_size)
  - optimizer_search_depth = 0
  - [innodb_buffer_pool_size = 134217728](https://mariadb.com/kb/en/innodb-system-variables/#innodb_buffer_pool_size)
- Enable columns compression
    ```sql
    ALTER TABLE `gsum_sum` ROW_FORMAT=COMPRESSED;
    ```
  - Or
    ```sql
    CREATE TABLE gsum_sum (view VARCHAR(32) PRIMARY KEY, save TEXT) ROW_FORMAT=COMPRESSED;
    ```
  - You could also add KEY_BLOCK_SIZE for further data compression. and/or [*provide performance benefits*](https://dev.mysql.com/doc/refman/5.7/en/glossary.html#glos_page_size)<br/>
    MySQL uses a page size of 1, 2, 4, 8 or 16KB (Default =16 if not ROW_FORMAT=COMPRESSED else 8)<br/>
    **KEY_BLOCK_SIZE** depends on **FILE_BLOCK_SIZE** which in turns related to **innodb_page_size** config value<br/>
    In this particular case, we will use the following combination:<br/>
    
    | innodb_page_size | FILE_BLOCK_SIZE | KEY_BLOCK_SIZE |
    |-----------------:|----------------:|---------------:|
    |            16384 |            2048 |              2 |
    
    For available compression combinations, refer to [**Table 14.3 Combinations for Compressed Tables**](https://dev.mysql.com/doc/refman/5.7/en/general-tablespaces.html)<br/>
    For more information, refer to [**InnoDB Compression Tuning**](https://dev.mysql.com/doc/refman/5.7/en/innodb-compression-tuning.html), Section: General Tablespace Row Format Support
    ```sql
    CREATE TABLE gsum_sum (view VARCHAR(32) PRIMARY KEY, save TEXT) ROW_FORMAT=COMPRESSED KEY_BLOCK_SIZE=8;
    ```
  - Optional, Enable InnoDB with [**Transparent Page Compression**](https://dev.mysql.com/doc/refman/5.7/en/innodb-page-compression.html)
    ```sql
    ALTER TABLE t1 COMPRESSION="zlib";
    OPTIMIZE TABLE t1;
    ```
### Compression Migration Procedure
- Declare databases list
  ```bash
  db_list=( 'exhg_nexus' 'booru' 'pixiv' 'hfoundry' 'sanka' 'idol' )
  mkdir -p ./before/ ./after/
  ```
- Backup databases
  ```bash
  for x in ${db_list[@]}; do mysqldump -uroot -proot -h127.0.0.1 --single-transaction --add-drop-database "$x" > "./before/${x}.sql"; done
  ```
- Modify dump file
  ```bash
  for y in $(ls -1 ./before/*.sql); do echo "MODDING [$y]"; sed 's/KEY_BLOCK_SIZE=4/FILE_BLOCK_SIZE=2048 KEY_BLOCK_SIZE=2 COMPRESSION="zlib"/' "./before/$y" > "./after/$y" ; done
  ```
- Stop container
  ```bash
  docker stop mariadb
  ```
- Backup & delete current data folder
  ```bash
  rsync-backup ./mariadb _dl-env/
  rm -rf ./mariadb/data
  ```
- Edit "./mariadb/conf/my.cnf", add variables needed for compression to \[mysqld\] config block
- Start container
  ```bash
  docker start mariadb
  ```
- Import modified dumps
  ```bash
  for z in $(ls -1 ./after/*.sql); do echo "IMPORT [$y]"; mysql -uroot -proot -h127.0.0.1 < "./after/$z"; done
  ```
- Rollback
  ```bash
  docker stop mariadb
  rm -rf ./mariadb/data
  docker start mariadb
  for z in $(ls -1 ./before/*.sql); do echo "IMPORT [$y]"; mysql -uroot -proot -h127.0.0.1 < "./before/$z"; done
  ```
