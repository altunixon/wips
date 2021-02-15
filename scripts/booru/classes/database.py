#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from collections import namedtuple
from classes.utils import gen_viewid
from helpers.misc import print_log

class checks():
    def __init__(self, database_obj, **options):
        self.database_object = database_obj
        self.database_verbose = options.pop('verbose', False)

    def view(self, view_href, view_table, **options):
        check_verbose = options.pop('verbose', self.database_verbose)
        check_result = namedtuple(
            'DbCheckResultSingle', ['skip', 'data', 'count'])
        if self.database_object is not None:
            view_id = options.pop('id', gen_viewid(view_href))
            view_data = self.database_object.select_from(table=view_table, view=view_id)
            view_dlen = len(view_data) if view_data is not None else 0
            if check_verbose:
                print_log('info', 'CHECK [VSGL] - Table: "%s", Url: "%s", Rows: [%s]', view_table, view_href, view_dlen)
            else:
                pass
            return check_result(
                skip = True if view_dlen > 0 else False, 
                data = view_data, 
                count= view_dlen
            )
        else:
            if check_verbose:
                print_log('warn', 'CHECK [VSGL] - No database')
            else:
                pass
            return check_result(skip = False, data = None, count = None)

    def views(self, index_views, index_table, **options):
        check_verbose = options.pop('verbose', self.database_verbose)
        check_results = namedtuple('DbCheckResultMulti', ['skip', 'data', 'count'])
        if self.database_object is not None:
            check_count = 0
            check_store = []
            for view_href in index_views:
                view_id = gen_viewid(view_href)
                # print(view_id)
                check_single = self.view(view_href, index_table, id=view_id, verbose=check_verbose)
                if check_single.skip:
                    check_count += 1
                    check_store.append(check_single.skip)
                else:
                    pass
            check_skip = True if check_count >= len(index_views) else False
            if check_verbose:
                print_log(
                    'info', 
                    'CHECK [VMUL] - Table: "%s", View: [%s/%s] db/img, Stat: [%s]', 
                    index_table, check_count, len(index_views), 
                    'SkipAll' if check_skip else 'No-Skip'
                )
            else:
                pass
            return check_results(
                skip = check_skip, 
                data = check_store, 
                count= check_count
            )
        else:
            return check_results(skip = False, data = None, count = None)
