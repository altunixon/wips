
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
### InnoDB Enabling Table Compression [MariaDB](https://mariadb.com/kb/en/innodb-page-compression/)/[MySQL](https://dev.mysql.com/doc/refman/5.6/en/innodb-compression.html)
- my.cnf:
  - innodb_file_per_table = ON
  - innodb_file_format = Barracuda
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
  - You could also add KEY_BLOCK_SIZE for further compression.<br/>
    MySQL uses a page size of 1, 2, 4, 8 or 16KB (Default =16 if not ROW_FORMAT=COMPRESSED else 8)<br/>
    For more information, refer to [**InnoDB Compression Tuning**](https://dev.mysql.com/doc/refman/5.6/en/innodb-compression-tuning.html)
    ```sql
    CREATE TABLE gsum_sum (view VARCHAR(32) PRIMARY KEY, save TEXT) ROW_FORMAT=COMPRESSED KEY_BLOCK_SIZE=8;
    ```
  - Optional, Enable InnoDB with [**Transparent Page Compression**](https://dev.mysql.com/doc/refman/5.7/en/innodb-page-compression.html)
    ```sql
    ALTER TABLE t1 COMPRESSION="zlib";
    OPTIMIZE TABLE t1;
    ```
