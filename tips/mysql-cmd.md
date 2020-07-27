### Queries
Search table by name
```sql
SELECT TABLE_NAME FROM information_schema.TABLES WHERE TABLE_NAME LIKE '%_x_%'
```
Rename Table [and more](https://www.techonthenet.com/mysql/tables/alter_table.php)
```sql
ALTER TABLE `official_art+order-popular&commit=Search` RENAME TO `official_art`;
```