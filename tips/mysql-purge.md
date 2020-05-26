db_name="hfoundry"
ls -1 "/media/alt/ramdisk1/maria/data/$db_name/" | awk -F '.' '{print tolower($1)}' | sort | uniq -c | grep -Ev ^2

db_name="booru"
ls -1 "/media/alt/ramdisk1/maria/data/$db_name/" | awk -F '.' '{print tolower($1)}' | sort | uniq -c | grep -Ev ^2

for x in $(ls -1 "/media/alt/ramdisk1/maria/data/$db_name/" | awk -F '.' '{print tolower($1)}' | sort | uniq -c | grep -Ev ^2); do
table_lowr=$(echo $x | awk '{print $NF}')
table_uppr=$(echo "$table_lowr"  | python -c "print (raw_input().capitalize().strip())")
echo -e "INSERT IGNORE INTO ${db_name}.${table_uppr} SELECT * FROM ${db_name}.${table_lowr};
PURGE TABLE ${db_name}.${table_lowr};
RENAME TABLE ${db_name}.${table_uppr} TO booru.${table_lowr};
" | tee -a "./${db_name}-purge.sql"
done
