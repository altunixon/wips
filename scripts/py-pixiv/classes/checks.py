#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from glob import glob
from collections import namedtuple
from helpers.misc import print_log, print_color
from helpers.dir_helper import MkDirP
from classes.utils import pixiv_viewid, nijie_viewid

class dlcheck():
    def __init__(self, mah_database, mah_workdir, **options):
        self.database = mah_database
        self.verbose = options.pop('verbose', False)
        self.redl = options.pop('redl', False)
        self._brint = print_log if not options.pop('color', False) else print_color
        self.vcheck = namedtuple('CheckViewSingle', ['skip', 'data', 'done'])
        self.vchecks = namedtuple('CheckViewMulti', ['skip', 'data', 'done', 'total'])
        self.vcheck_null = self.vcheck(skip=False, data=None, done=0)
        self.vchecks_null = self.vchecks(skip=False, data=None, done=0, total=0)

    def view(self, u_tbl, v_id, **options):
        if self.database is not None:
            pix_downloaded = self.database.run(
                mode='select row', 
                table=u_tbl, 
                view=v_id
            )
            if len(pix_downloaded) > 0:
                if self.redl: #or isnew_multipage:
                    if self.database is not None:
                        self.database.run(mode='delete row', table=u_tbl, view=v_id)
                    else:
                        pass
                    v_exists = False
                else:
                    v_exists = True
            else:
                v_exists = False
            return self.vcheck(
                skip = v_exists, 
                data = pix_downloaded, 
                done = len(pix_downloaded)
            )
        else:
            return self.vcheck_null

    def views(self, u_tbl, vs_all, **options):
        if self.database is not None:
            vs_dcount = 0
            vs_data = []
            vs_total = options.pop('total', None)
            if vs_total is None:
                vs_total = len(vs_all)
            else:
                pass
            for v_ref in vs_all:
                v_id = pixiv_viewid(v_ref)
                v_schk = self.view(u_tbl, v_id)
                vs_data.append(v_schk.data)
                if v_schk.skip:
                    vs_dcount += 1
                    if self.verbose:
                        self._brint('debug', 'LAZY CHECK (ALL) Href: "%s" exists "%s"', v_ref, v_schk.data)
                    else:
                        pass
                else:
                    break
            return self.vchecks(
                skip = True \
                    if vs_dcount == vs_total \
                    and vs_dcount > 0 \
                    else False, 
                data = vs_data, 
                done = vs_dcount,
                total = vs_total
            )
        else:
            return self.vchecks_null
    
    def bypass(self, u_tbl, v_id, **options):
        if self.database is not None:
            pix_search = self.database.run(
                mode='select row', 
                table=u_tbl, 
                view=v_id, 
                fetch='one'
            )
            if pix_search is None or len(pix_search) == 0:
                return self.vcheck_null
            else:
                # if any('_p0-' in str(x) or '_p0.' in str(x) for x in pix_search):
                if any('_p0' in str(x) for x in pix_search):
                    return self.vcheck_null
                else:
                    self._brint('debug', 'VIEWM [PASS] - Db: "%s"', ', '.join(pix_search))
                    return self.vcheck(skip=True, data=pix_search, done=666)
        else:
            return self.vcheck_null

    def glob_glob(self, save_path, user_id, view_id, **options):
        glob_path = os.path.join(save_path, '{uid}_{vid}_p*.*'.format(uid=user_id, vid=view_id))
        glob_found = glob(glob_path)
        if len(glob_found) > 0:
            return self.vcheck(skip=True, data=glob_found, done=len(glob_found))
        else:
            return self.vcheck_null

    def createnew(self, u_tbl, pix_saveto):
        MkDirP(pix_saveto, meltdown=True)
        if self.database is not None \
        and u_tbl is not None:
            self.database.run(
                mode='create table', 
                table=u_tbl, 
                view='VARCHAR(32) PRIMARY KEY', 
                save='TEXT NOT NULL'
            )
        else:
            pass


