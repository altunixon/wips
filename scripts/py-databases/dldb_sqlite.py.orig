#!/usr/bin/env python
# -*- coding: utf-8 -*-  


import os
from helpers.misc import telltime, print_log
from databases.dldb_sqlweaver import sql_query_templates, FormatDefault, sql_weaver



import sqlite3
class dldb_sqlite():
    def __init__(self, db_path, **options):
        self.type           = 'sqlite'
        self.db_path        = db_path
        self.db_connector   = sqlite3.connect(db_path)
        self.fetch_dict     = options.pop('fetch_dict', False)
        def dict_factory(cursor, row):
            d = {}
            for idx, col in enumerate(cursor.description):
                d[col[0]] = row[idx]
            return d
        self.db_connector.row_factory = sqlite3.Row \
            if not self.fetch_dict \
            else dict_factory
        self.db_cursor      = self.db_connector.cursor()



    def exe(self, sqlite_query, fetch=None):
        self.db_cursor.execute(sqlite_query)
        self.db_connector.commit()
        if fetch is not None:
            return self.db_cursor.fetchone() \
                if fetch == 'one' \
                else self.db_cursor.fetchall()
        else:
            return None

    def run(self, **query_data):
        query_mode = query_data.pop('mode', None)
        query_dbug = query_data.pop('debug', None)
        query_null = query_data.pop('default', False)
        query_parse = sql_weaver(query_mode, type=self.type, **query_data)
        query_fetch = query_parse['fetch']
        query_final = query_parse['query']
        if query_final is None or query_mode is None:
            print_log('error', 'DLDB [SQLTE] - Run: "%s", Values: %s', query_mode, query_data)
            exit()
        else:
            if query_dbug is not None:
                print_log('debug', 'DLDB [SQLTE] - Run: "%s", Values: %s, Fetch: %s', query_mode, query_final, query_fetch)
                return []
            else:
                try:
                    return self.exe(query_final, query_fetch)
                except:
                    print_log('error', 'DLDB [SQLTE] - Run: "%s", Values: %s, Fetch: %s', query_mode, query_final, query_fetch)
                    if query_null:
                        return None
                    else:
                        self.close()
                        raise

    def cheat_merge(self, create_table, *mergedbs):
        #from class_dldb import dldb
        #m=dldb('/cygdrive/g/hdb_exhg.sqlite')
        #m.cheat_merge('CREATE TABLE IF NOT EXISTS "%s" (id INTEGER PRIMARY KEY, image_view TEXT UNIQUE, image_save TEXT);', '/cygdrive/g/exhg_dl.db')
        for mergedb in mergedbs:
            self.db_cursor.execute("ATTACH DATABASE '{0}' AS toMerge".format(mergedb))
            print(self.db_cursor.execute("SELECT name FROM toMerge.sqlite_master WHERE type='table'").fetchall())
            mtbls = [m[0] for m in self.db_cursor.execute("SELECT name FROM toMerge.sqlite_master WHERE type='table'").fetchall()]
            #print mtbls
            print(self.db_cursor.execute("SELECT * FROM toMerge.'{0}'".format(mtbls[0])).fetchall())
            for merge_table in mtbls:
                print(self.db_cursor.execute("SELECT * FROM toMerge.'{0}'".format(merge_table)).fetchall())
                merge_q = "INSERT INTO '{0}' SELECT * FROM toMerge.'{0}'".format(merge_table)
                if self.cheat_table_exists(merge_table):
                    self.db_cursor.execute("DROP TABLE '%s'" % merge_table)
                    self.db_cursor.execute(create_table % merge_table)
                    print(merge_q, self.db_cursor.execute(merge_q).fetchall())
                else:
                    #self.db_cursor.execute('SELECT sql FROM "%s"' % merge_table).fetchone()[0]
                    self.db_cursor.execute(create_table % merge_table)
                    print(merge_q, self.db_cursor.execute(merge_q).fetchall())
            self.db_cursor.execute('DETACH DATABASE toMerge')
        self.db_connector.commit()
            
            
    def cheat_table_exists(self, table_name):
        check_table_query = "SELECT name FROM sqlite_master WHERE type='table' AND name='%s';" % table_name
        return_data = self.db_cursor.execute(check_table_query).fetchall()
        print('CHEAT', return_data)
        return True if len(return_data) > 0 else False
        
    def cheat_client(self, dbquery, fetchone=False):
        return self.db_cursor.execute(dbquery).fetchone() \
            if fetchone \
            else self.db_cursor.execute(dbquery).fetchall()
    
    def close(self): 
        self.db_cursor.close()
        self.db_connector.close()
       


# Quick&Dirty
#import sqlite3
#
#db1='/home/python/Torrents/exht_database.sqlite-old'
#db2='/home/python/Torrents/exht_database.sqlite'
#
#db_old = sqlite3.connect(db1)
#db_old.row_factory = sqlite3.Row
#cu_old = db_old.cursor()
#
#db_new = sqlite3.connect(db2)
#db_new.row_factory = sqlite3.Row
#cu_new = db_new.cursor()
#
#tbl_old= cu_old.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
#
#table_names = [t[0] for t in tbl_old]
#for tbl in table_names:
#    cu_new.execute("CREATE TABLE IF NOT EXISTS `{table}` (gallery VARCHAR(32) PRIMARY KEY, gallery_href TEXT, name_roman TEXT, thumb TEXT, json TEXT, page INTEGER);".format(table=tbl))
#    tbl_rows = cu_old.execute('SELECT * FROM `%s`;' % tbl).fetchall()
#    for row_int, row_old in enumerate(tbl_rows):
#        page=int(row_int/25)
#        data=dict(row_old)
#        data['json'] = data['json'] if data['json'] != 'None' else 'null'
#        data['page'] = page
#        data['table'] = tbl
#        query="INSERT OR REPLACE INTO `{table}` (gallery, gallery_href, name_roman, thumb, json, page) VALUES ('{gallery}', '{gallery_href}', '{name_roman}', '{thumb}', '{json}', '{page}')".format(**data)
#        print(query)
#        cu_new.execute(query)
#    query="INSERT OR REPLACE INTO `{table}` (gallery, gallery_href, name_roman, thumb, json, page) VALUES ('meta_data', 'migration', 'unknown-migration', 'not_available', 'null', '{page}')".format(table=tbl, page=page)
#    cu_new.execute(query)
#
#cu_new.close()
#cu_old.close()
#db_new.commit()
#db_new.close()
#db_old.close()
