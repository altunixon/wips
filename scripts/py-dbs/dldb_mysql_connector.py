#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import mysql.connector
#from time import sleep
from helpers.misc import telltime, print_log
from databases.dldb_sqlweaver import sql_query_templates, FormatDefault, sql_weaver

class dldb_mysql():
    def __init__(self, **db_infos):
        self.type = 'mysql'
        db_connect_dict = db_infos
        db_connect_str = db_infos.get('string', None)
        if db_connect_str is not None:
            for frag in [x for x in db_connect_str.split(',') if len(x.trim()) > 0]:
                if '=' in frag:
                    k, v = frag.split('=',1)
                    db_connect_dict[k] = v
                else:
                    pass
        else:
            pass
        #print(db_connect_dict)
        self.db_host = db_connect_dict.get('h', None)
        self.db_user = db_connect_dict.get('u', None)
        self.db_pass = db_connect_dict.get('p', None)
        self.db_port = db_connect_dict.get('port', None)
        self.db_name = db_connect_dict.get('database', None)
        db_must = (self.db_host, self.db_user, self.db_pass)
        if any(not_db is None for not_db in db_must):
            print_log ('error', 'DLDB [MYSQL] - Connector value error: %s', db_must)
            raise Exception('MYSQL Connector Value Error:\n%s' % db_infos)
        else:
            self.db_connector = mysql.connector.connect(
                host=self.db_host,
                user=self.db_user, 
                password=self.db_pass,
                database=self.db_name,
                charset='utf8'
            )
            if db_connect_dict.get('fetch_dict', False):
                self.db_cursor = self.db_connector.cursor(dictionary=True, buffered=True)
            else:
                self.db_cursor = self.db_connector.cursor(buffered=True)

    def exe(self, sql_query, fetch=None):
        try:
            self.db_cursor.execute(sql_query)
            self.db_connector.commit()
        except Exception as excp:
            print (sql_query)
            raise excp
        if fetch is not None:
            return self.db_cursor.fetchone() \
                if fetch == 'one' \
                else self.db_cursor.fetchall()
        else:
            return None

    def run(self, **query_data):
        query_mode = query_data.pop('mode', None)
        #table_comm = query_data.pop('comment', None)
        verbosity  = query_data.pop('verbose', True)
        query_dbug = query_data.pop('debug', False)
        query_null = query_data.pop('default', False)
        query_parse = sql_weaver(
            query_mode, 
            type=self.type, 
            schema=self.db_name, 
            **query_data
        )
        if query_parse.query is None:
            if verbosity:
                print_log('error', 'DLDB [MYSQL] - Run: "%s", Query: %s', query_mode, query_parse.query)
            raise Exception('MYSQL No Table name/query mode\n%s' % query_data)
        else:
            if query_dbug:
                print_log('debug', 'DLDB [MYSQL] - Run: "%s", Query: %s, Fetch: %s', query_mode, query_parse.query, query_parse.fetch)
            try:
                return self.exe(query_parse.query, query_parse.fetch)
            except mysql.connector.errors.InterfaceError:
                #sleep(60)
                try:
                    self.db_connector.reconnect(attempts=1, delay=60)
                    return self.exe(query_parse.query, query_parse.fetch)
                except:
                    if verbosity: print_log('error', 'DLDB [MYSQL] - Run: "%s", Query: %s', query_mode, query_parse.query)
                    if query_null:
                        return None
                    else:
                        self.close()
                        raise
            except:
                raise
    
    def create_table(self, **query_data):
        assert query_data.get('table', None) is not None, \
            print_log('error', 'DLDB [MYSQL] - Could not CREATE TABLE with %s', query_data)
        table_comment = query_data.get('comment', None)
        query_parse = sql_weaver(
            'create table', 
            type=self.type, 
            schema=self.db_name, 
            **query_data
        )
        create_cmd = query_parse.query if \
            table_comment is None else \
            '{cmd} COMMENT="{comment}";'.format(cmd=query_parse.query.strip(';'), comment=table_comment)
        self.exe(create_cmd, None)
    
    def select_from(self, **query_data):
        assert query_data.get('table', None) is not None, \
            print_log('error', 'DLDB [MYSQL] - Could not SELECT FROM with %s', query_data)
        query_parse = sql_weaver(
            'select row', 
            type=self.type, 
            schema=self.db_name, 
            **query_data
        )
        return self.exe(query_parse.query, query_parse.fetch)
    
    def insert_into(self, **query_data):
        assert query_data.get('table', None) is not None, \
            print_log('error', 'DLDB [MYSQL] - Could not SELECT FROM with %s', query_data)
        query_parse = sql_weaver(
            'insert row', 
            type=self.type, 
            schema=self.db_name, 
            **query_data
        )
        self.exe(query_parse.query, None)
        
    def flush(self, **options):
        # for JSON DB compatibility purpose, doesnt actually do anything
        return None

    #from databases.DLDB [MYSQL]_connector import *
    #h={'h':'127.0.0.1', 'u':'root', 'p':'root', 'database':'mdex'}
    #m=DLDB [MYSQL](**h)
    #m.cheat_import_sqlite('hdb_exhg.sqlite')
    def cheat_import_sqlite(self, *sqlite_dbs):
        from databases.dldb_sqlite import dldb_sqlite
        for mergedb in sqlite_dbs:
            sqlite_db = dldb_sqlite(mergedb)
            for sqlite_table in sqlite_db.cheat_client("SELECT name FROM sqlite_master WHERE type='table'"):
                print(sqlite_table[0])
                self.run(mode='drop table', table=sqlite_table[0])
                self.run(mode='create table', table=sqlite_table[0], view='VARCHAR(64) PRIMARY KEY', save='TEXT NOT NULL', debug='on')
                for sqlite_row in sqlite_db.cheat_client("SELECT view, save FROM '%s'" % sqlite_table[0]):
                    self.run(
                        mode='insert row', 
                        table=sqlite_table[0], 
                        image_view='_'.join(sqlite_row[0].split('/')[-2:]), image_save=sqlite_row[1], 
                        uniq='view', 
                        debug='on')
                #self.run(mode='select all', table=db_table, debug='on')
            sqlite_db.close()

    def search_artist(self, artist_name):
        list_tables = """SELECT table_name FROM information_schema.tables
    WHERE table_type='base table'
    AND   table_schema='%s';""" % self.db_name

    def close(self):
        self.db_cursor.close()
        self.db_connector.disconnect()
        self.db_connector.close()
