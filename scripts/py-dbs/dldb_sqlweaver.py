#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from helpers.misc import print_log

class FormatDefault(dict):
    def __missing__(self, key):
        return key

def sql_weaver(template_name, **template_inserts):
    assert template_name in sql_query_templates.keys(), 'SQL_PARSER - Invalid Template: "%s", Values: %s' % (template_name, template_inserts)
    query_template  = sql_query_templates[template_name]
    query_format    = template_inserts.pop('type', 'mysql')
    query_command   = query_template[query_format] \
        if query_template[query_format] is not None \
        else query_template['mysql']
    query_table     = template_inserts.pop('table', None)
    query_schema    = template_inserts.pop('schema', None)
    query_uniq      = template_inserts.pop('uniq', None)
    query_fetch     = template_inserts.pop('fetch', query_template['fetch'])
    if query_table is not None:
        if query_template['inserts'] is None:
            query_string = query_command.format_map(
                FormatDefault(
                    table   = query_table, 
                    schema  = query_schema, 
                    **template_inserts
                )
            )
        else:
            if query_template['join'] is None:
                insert_names    = ', '.join(template_inserts.keys())
                insert_values   = ', '.join(
                    ["'%s'" % template_inserts[b] \
                    for b in template_inserts.keys()]
                )
                query_values = query_template['inserts'].format(
                    key     = insert_names,
                    value   = insert_values
                )
            else:
                key_values_pair = []
                for k, v in template_inserts.items():
                    key_values_pair.append(
                        query_template['inserts'].format(
                            key     = k,
                            value   = v
                        )
                    )
                query_values = query_template['join'].join(key_values_pair)
            query_string = query_command.format_map(
                FormatDefault(
                    table   = query_table, 
                    schema  = query_schema, 
                    values  = query_values
                )
            )
            if query_template['uniq'] and query_uniq is not None:
                query_tacky = sql_query_templates['tackon uniq']
                query_tackf = query_tacky[query_format] \
                    if query_tacky[query_format] is not None \
                    else query_tacky['mysql']
                query_string += query_tackf.format(
                    values = query_tacky['join'].join(
                        [query_tacky['inserts'].format(key=k, value=v) \
                            for k, v in template_inserts.items()]
                    )
                )
            else:
                pass
            query_string += ';'
    else:
        print_log(
            'error', 
            'SQL_PARSER - Invalid Table: "%s.%s", Values: %s', 
            query_schema, 
            query_table, 
            template_inserts
        )
        query_string = None
    #print('DEBUG:', query_string, query_fetch)
    query_out = namedtuple('QueryDetails', ['query', 'fetch'])
    return query_out(query_string, query_fetch)

sql_charset = 'utf8mb4'
sql_collate = 'utf8mb4_unicode_ci'

sql_query_templates = {
    'select all'    : {
        'mysql'     : "SELECT * FROM `{table}`",
        'sqlite'    : None,
        'inserts'   : None,
        'join'      : None,
        'fetch'     : 'all',
        'uniq'      : False
    },
    'select table'  : {
        'mysql'     : "SELECT * FROM information_schema.tables WHERE table_schema='{schema}' AND table_name='{table}' LIMIT 1",
        'sqlite'    : "SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'",
        'inserts'   : None,
        'join'      : None,
        'fetch'     : 'all',
        'uniq'      : False
    },
    'create table'  : {
        #'mysql'     : "CREATE TABLE IF NOT EXISTS `{table}` ({values}) CHARSET=utf8 COLLATE=utf8_unicode_ci ROW_FORMAT=COMPRESSED KEY_BLOCK_SIZE=4",
        'mysql'     : "CREATE TABLE IF NOT EXISTS `{table}` ({values}) CHARSET=%s COLLATE=%s ROW_FORMAT=COMPRESSED KEY_BLOCK_SIZE=4" % (sql_charset, sql_collate),
        'sqlite'    : "CREATE TABLE IF NOT EXISTS `{table}` ({values})",
        'inserts'   : '{key} {value}',
        'join'      : ', ',
        'fetch'     : None,
        'uniq'      : False
    },
    'update table'  : {
        'mysql'     : "ALTER TABLE '{table}' RENAME TO 'UPDATE_TEMP'; CREATE TABLE '{table}' LIKE 'UPDATE_TEMP'; INSERT INTO '{table}' SELECT * FROM 'UPDATE_TEMP'; DROP TABLE 'UPDATE_TEMP'",
        'sqlite'    : None,
        'inserts'   : None,
        'join'      : None,
        'fetch'     : None,
        'uniq'      : False
    },
    'drop table'    : {
        'mysql'     : 'DROP TABLE IF EXISTS `{table}`',
        'sqlite'    : None,
        'inserts'   : None,
        'join'      : None,
        'fetch'     : None,
        'uniq'      : False
    },
    'select row'    : {
        'mysql'     : "SELECT * FROM `{table}` WHERE {values}",
        'sqlite'    : None,
        'inserts'   : "{key}='{value}'",
        'join'      : ' AND ',
        'fetch'     : 'all',
        'uniq'      : False
    },
    'insert row'    : {
        'mysql'     : "INSERT IGNORE INTO `{table}` {values}",
        'sqlite'    : "INSERT OR IGNORE INTO `{table}` {values}",
        'inserts'   : '({key}) VALUES ({value})',
        'join'      : None,
        'fetch'     : None,
        'uniq'      : False
    },
    'upsert row'    : {
        'mysql'     : "INSERT OR REPLACE INTO '{table}' {values}",
        'sqlite'    : None,
        'inserts'   : '({key}) VALUES ({value})',
        'join'      : None,
        'fetch'     : None,
        'uniq'      : False
    },
    'delete row'    : {
        'mysql'       : "DELETE FROM `{table}` WHERE {values}",
        'sqlite'    : None,
        'inserts'   : "{key}='{value}'",
        'join'      : ' AND ',
        'fetch'     : None,
        'uniq'      : False
    },
    'tackon uniq'   : {
        'mysql'     : " ON DUPLICATE KEY UPDATE {values}",
        'sqlite'    : None,
        'inserts'   : "{key}='{value}'",
        'join'      : ', ',
        'fetch'     : None,
        'uniq'      : False
    },
}
