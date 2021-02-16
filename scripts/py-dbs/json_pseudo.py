#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, json

class json_keystore():
    def __init__(self, json_file, **options):
        self.file = json_file
        self.json = None
        self.verbose = options.pop('verbose', True)

    def load(self, **options):
        load_verbose = options.pop('verbose', self.verbose)
        if self.file is None:
            self.json = {}
        else:
            try:
                with open(self.file, 'r') as ljs:
                    self.json = json.load(ljs)
            except Exception as excp:
                if load_verbose:
                    print('Keystore JSON [LOAD] "%s" Error\n%s' % (self.file, excp))
                else:
                    pass
                self.json = {}
        return self.json

    def update(self, json_key, json_value):
        if json_key not in self.json.keys():
            self.json[json_key] = json_value
            return True
        else:
            return False

    def dump(self, **options):
        json_indent = options.pop('indent', 4)
        json_sortkey = options.pop('sort', True)
        json_ascii  = options.pop('ensure_ascii', False)
        dump_verbose = options.pop('verbose', self.verbose)
        if self.json is not None and len(self.json.keys()) > 0:
            try:
                with open(self.file, 'w+') as ljs:
                    json.dump(
                        self.json, ljs, 
                        indent = json_indent, 
                        sort_keys = json_sortkey, 
                        ensure_ascii = json_ascii)
                return True
            except Exception as excp:
                if dump_verbose:
                    print('Keystore JSON [DUMP] "%s" Error\n%s' % (self.file, excp))
                else:
                    pass
                return False
        else:
            return False
