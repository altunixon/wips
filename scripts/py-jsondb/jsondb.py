import json
from os import path, normpath
from glob import glob
from time import time, localtime, strftime

# treats storage folder as database, save each table as one json file
# only support dictionary data type, which means tables are limit to 2 column
# flush on table close

class json_table:
    def __init__(self, table_dict, **options):
        self.table_name = "PLACEHOLDER"

class json_db:
    def __init__(self, db_root, **options):
        self.db_root = db_root
        self.db_meltdown = options.get('meltdown', True)
        if self.db_root is not None:
            if path.isdir(self.db_root):
                self.db_tables = {}
                for x in glob('%s/*.json' % normpath(self.db_root)):
                    table_name = path.splitext(path.basename(x))[0]
                    self.db_tables[table_name] = x
            else:
                raise Exception('[JSON DB] Database ROOT_PATH jsondb(db="%s") NotFound.')
        else:
            raise Exception('[JSON DB] Database ROOT_PATH jsondb(db="x") has not been defined.')
        self.db_delete_on_drop = options.get('delete_on_drop', True)
        self.db_template = {
            "name": "NOT_NUL",
            "comment": "NUL",
            "data": {},
            "create_date": "NUL",
            "modified_date": "NUL",
            "rows": 0,
            "dirty": 0
        }
        
    def timestamp(self):
        table_ctime = time()
        return strftime('{epoch} | %Y-%m-%d %H:%M:%S %z%Z'.format(epoch=table_ctime), localtime(table_ctime))
    
    def table_read(self, table_name, **options)):
        set_dirty = options.get('dirty', None)
        if table_name not in self.db_tables.keys():
            return self.table_create(table_name)
        else:
            with open(self.db_tables[table_name], 'rt') as fp:
                table_dict = json.load(fp)
            if set_dirty is not None:
                table_dict['dirty'] = int(set_dirty)
            return table_dict
        
    def table_insert(self, table_dict, data_key, data_value, **options):
        mode_update = options.get('update', True)
        if mode_update or data_key not in table_dict['data'].keys():
            table_dict['data'][data_key] = data_value
            table_dict['dirty'] = 1
        else:
            pass
        
    def table_search(self):
        return "PLACEHOLDER"

    def table_create(self, table_name, **options):
        if table_name not in self.db_tables.keys():
            table_comment = options.get('comment', None)
            table_cdate = self.timestamp()
            table_new = {
                "name": table_name
                "comment": table_comment,
                "data": {},
                "create_date": table_cdate,
                "modified_date": table_cdate,
                "rows": 0,
                "dirty": 1
            }
            table_file = '{root}/{table}.json'.format(root=self.db_root, table=table_name)
            self.db_tables[table_name] = table_file
            return table_new
        else:
            return self.table_read(table_name)
    
    def table_close(self, table_dict, **options):
        if table_dict["dirty"] > 0:
            table_path = self.db_tables[table_dict["name"]]
            with open(table_path, "w+") as fp:
                json.dump(table_dict, fp)
            print ('[JSON DB] Table "%s" Flushed to "%s"' % (table_dict["name"], table_path))
        else:
            print ('[JSON DB] Table "%s" is clean, skip flushing to "%s"' % (table_dict["name"], table_path))
        
        
        
