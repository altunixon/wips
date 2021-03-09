import json
from os import path
from glob import glob
from time import time, localtime, strftime

# treats storage folder as database, save each table as one json file
# only support dictionary data type, which means tables are limit to 2 column
# flush on table close

class json_db:
    def __init__(self, db_root, **options):
        self.db_type = 'json'
        self.db_root = db_root
        self.db_cache = {}
        self.db_meltdown = options.get('meltdown', True)
        if self.db_root is not None:
            if path.isdir(self.db_root):
                self.db_tables = {}
                for x in glob('%s/*.json' % path.normpath(self.db_root)):
                    table_name = path.splitext(path.basename(x))[0]
                    self.db_tables[table_name] = x
            else:
                raise Exception('[JSON DB] Database ROOT_PATH jsondb(db="%s") NotFound.')
        else:
            raise Exception('[JSON DB] Database ROOT_PATH jsondb(db="x") has not been defined.')
        self.db_dirty_tables = set([])
        self.db_delete_on_drop = options.get('delete_on_drop', True)
        self.warn_not_cached = lambda x: 'Query table [%s] has not been cached\nCurrent Cache:\n%s\n' % \
            (x, json.dumps(self.db_cache, indent=4))
        
    def timestamp(self):
        table_ctime = time()
        return strftime('{epoch} | %Y-%m-%d %H:%M:%S %z%Z'.format(epoch=table_ctime), localtime(table_ctime))
    
    def read_table(self, table_name, **options):
        set_dirty = options.get('dirty', False)
        if table_name not in self.db_tables.keys():
            self.table_create(table_name)
        else:
            with open(self.db_tables[table_name], 'rt') as fp:
                self.db_cache[table_name] = json.load(fp)

    def create_table(self, **query_data):
        table_name = query_data.pop('table', None)
        assert (table_name is not None), \
            '[JSON DB] Could not CREATE TABLE with NUL <table_name> value: %s' % query_data
        table_file = '{root}/{table}.json'.format(root=self.db_root, table=table_name)
        table_comment = query_data.pop('comment', None)
        col_key = col_val = None
        for k, v in query_data.items():
            if 'key' in v.lower():
                col_key = k
            else:
                col_val = k
        assert (col_key is not None and col_val is not None), \
            '[JSON DB] Could not CREATE TABLE with Invalid key/value pairs: %s' % query_data
        if table_name not in self.db_tables.keys() or not path.isfile(table_file):
            table_cdate = self.timestamp()
            table_new = {
                'name': table_name,
                'comment': table_comment,
                'data': {},
                'key': col_key,
                'value': col_val,
                'create_date': table_cdate,
                'modified_date': table_cdate,
                'rows': 0
            }
            self.db_tables[table_name] = table_file
            self.db_cache[table_name] = table_new
            self.db_dirty_tables.add(table_name)
        else:
            with open(self.db_tables[table_name], 'rt') as fp:
                self.db_cache[table_name] = json.load(fp)
    
    def insert_into(self, **query_data):
        table_name = query_data.pop('table', None)
        assert (table_name is not None and table_name in self.db_cache.keys()), self.warn_not_cached(table_name)
        col_key = self.db_cache[table_name]['key']
        data_key = query_data.get(col_key, None)
        col_val = self.db_cache[table_name]['value']
        data_val = query_data.get(col_val, None)
        assert (data_key is not None and data_val is not None), \
            '[JSON DB] Could not INSERT INTO "%s" with Invalid key/value pairs: %s' % (table_name, query_data)
        mode_update = query_data.pop('update', True)
        data_old = None
        if data_key in self.db_cache[table_name]['data'].keys():
            data_old = self.db_cache[table_name]['data'][data_key]
        if mode_update or data_old is None:
            self.db_cache[table_name]['data'][data_key] = data_val
            self.db_dirty_tables.add(table_name)
            print ('[JSON DB] INSERT or UPDATE into {table}|{key}: "{value_old}" -> "{value_new}" flag Update={uflag}'.format(
                table=table_name, key=data_key, 
                value_old=data_old, value_new=data_val, 
                uflag=mode_update
            ))
        else:
            print ('[JSON DB] IGNORE UPDATE into {table}|{key}: "{value_old}" -> "{value_new}" since Update={uflag}'.format(
                table=table_name, key=data_key, 
                value_old=data_old, value_new=data_val, 
                uflag=mode_update
            ))
        
    def select_from(self, **query_data):
        table_name = query_data.pop('table', None)
        assert (table_name is not None and table_name in self.db_cache.keys()), self.warn_not_cached(table_name)
        col_key = self.db_cache[table_name]['key']
        data_match = query_data.get(col_key, None)
        assert (data_match is not None), \
            '[JSON DB] Could not INSERT INTO "%s" with Invalid key/value pairs: %s' % (table_name, query_data)
        match_exact = query_data.get('exact', True)
        match_count = query_data.get('count', False)
        match_key = match_value = None
        if match_exact:
            if data_match in self.db_cache[table_name]['data'].keys():
                match_key = data_match
                match_value = self.db_cache[table_name]['data'][data_match]
            else:
                pass
        else:
            for k, v in self.db_cache[table_name]['data'].items():
                if data_match in k:
                    match_key = k
                    match_value = v
                    break
                else:
                    pass
        if match_key is not None:
            return 1 if match_count else {match_key: match_value}
        else:
            return 0 if match_count else None

    def flush(self, **options):
        # from_msg = options.get('msg', None)
        if len(self.db_cache.keys()) > 0:
            for table_name, table_data in self.db_cache.items():
                if table_name in self.db_dirty_tables:
                    table_path = self.db_tables[table_name]
                    table_data['rows'] = len(table_data['data'].keys())
                    table_data['modified_date'] = self.timestamp()
                    print ('[JSON DB] Flushing Table "%s" to "%s" @%s' % (table_name, table_path, table_data['modified_date']))
                    with open(table_path, 'w+') as fp:
                        json.dump(table_data, fp)
                    print ('[JSON DB] Table "%s" Flushed %s rows to "%s"' % (table_name, table_data['rows'], table_path))
                else:
                    print ('[JSON DB] Table "%s" is clean, skip flushing to "%s"' % (table_name, table_path))
            self.db_cache = {}
            print ('[JSON DB] Cache cleared: %s' % self.db_cache)
        else:
            print ('[JSON DB] Cache Empty no need to flush()')
    
    def __del__(self):
        self.flush()
    
        
        
