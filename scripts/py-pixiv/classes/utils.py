
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, re
from os.path import isfile
from shutil import move
from random import randint
from urllib.parse import unquote, urlsplit, urlencode
from helpers.str_helper import urlPrefixer, arr2str, string_sanitizer
from helpers.misc import print_log, array2string
from vars.conf_pixiv import pixiv_index_identifier
from vars.conf_nijie import nijie_index_identifier

def gen_artistname(pix_name, pix_jumps):
    if len(pix_name) == 0:
        return None
    else:
        pix_name_single=pix_name[0]
        pix_name_remote= {
            'twitter.com': None,
            'www.patreon.com': None,
            'blogspot': None,
            'blog72.fc2.com': None,
        }
        if len(pix_jumps) > 0:
            for r in pix_jumps:
                jumper_uri = unquote(r)
                print_log('debug', 'MEMBR [HOME] - ExternalLink: "%s"', jumper_uri)
                jumper_href = jumper_uri.split('//',1)[-1].strip('/')
                s, u = jumper_href.split('/', 1) \
                    if '/' in jumper_href \
                    else [jumper_href.split('.')[1], jumper_href]
                pix_name_remote[s] = u
            if pix_name_remote['twitter.com'] is not None:
                return '@%s' % pix_name_remote['twitter.com']
            else:
                for _, user in pix_name_remote.items():
                    if user == pix_name_single:
                        return pix_name_single
                    else:
                        pass
                if pix_name_remote['www.patreon.com'] is not None:
                    return '$%s' % pix_name_remote['www.patreon.com']
                elif pix_name_remote['blogspot'] is not None:
                    return '@%s' % pix_name_remote['blogspot']
                elif pix_name_remote['blog72.fc2.com'] is not None:
                    return '@%s' % pix_name_remote['blog72.fc2.com']
                else: 
                    return pix_name_single
        else:
            return pix_name_single

def pixiv_userid(user_url, **options):
    strict_uid = options.pop('meltdown', False)
    spare_key = options.pop('keyw', None)
    if user_url is not None:
        user_id = user_url.strip('/').rsplit(pixiv_index_identifier, 1)[-1].split('/', 1)[0]
        if strict_uid:
            if len(user_id) == 0 or not user_id.isdigit():
                raise Exception('UserID (%s) invalid: "%s"' % (user_id, user_url))
            else:
                return user_id
        else:
            if user_id.isdigit():
                return user_id
            else:
                if spare_key is not None:
                    return get_urivalue(user_url, spare_key)
                else:
                    return None
    else:
        return None

def pixiv_viewid(view_url, **options):
    strict_vid = options.pop('meltdown', False)
    spare_key = options.pop('keyw', None)
    view_id = view_url.strip('/').rsplit('/', 1)[-1]
    if strict_vid:
        if len(view_id) == 0 or not view_id.isdigit():
            raise Exception('ViewID (%s) invalid: "%s"' % (view_id, view_url))
        else:
            return view_id
    else:
        if view_id.isdigit():
            return view_id
        else:
            if spare_key is not None:
                return get_urivalue(view_url, spare_key)
            else:
                return None

def pixiv_savename(link_href, **name_data):
    name_uri = link_href.strip('/').rsplit('/', 1)[-1]
    name_oly, name_ext = name_uri.rsplit('.', 1) if '.' in name_uri else (name_uri, 'dat')
    name_vid = name_data.get('viewid', None)
    name_uid = name_data.get('userid', None)
    name_tit = name_data.get('title', None)
    # print (name_data)
    if name_vid in name_oly:
        name_raw = name_oly
    else:
        name_raw = '{vid}_p{num}'.format(
            vid = name_vid, 
            num = name_oly
        )
    name_id = string_sanitizer(name_raw)
    # print (name_id)
    if name_tit is not None:
        save_name = '{uid}_{name}-{title}.{ext}'.format(
            uid     = name_uid,
            title   = string_sanitizer(name_tit, nospace='_'),
            name    = name_id,
            ext     = name_ext,
        )
    else:
        save_name = '{uid}_{name}.{ext}'.format(
            uid     = name_uid,
            name    = name_id,
            ext     = name_ext,
        )
    # print (save_name)
    return save_name

def nijie_id(user_url, **options):
    strict_uid = options.pop('meltdown', False)
    spare_key = options.pop('keyw', None)
    if user_url is not None:
        uri_query = urlsplit(unquote(user_url)).query
        uri_params = {}
        for x in uri_query.split('&'):
            y, z = x.split('=', 1)
            uri_params[y] = z
        user_id = uri_params.get('id', None)
        if strict_uid:
            if user_id is None or not user_id.isdigit():
                raise Exception('Invalid ID (%s): "%s"' % (user_id, user_url))
            else:
                return user_id
        else:
            if user_id.isdigit():
                return user_id
            else:
                if spare_key is not None:
                    return get_urivalue(user_url, spare_key)
                else:
                    return None
    else:
        return None
    
def nijie_viewid():
    return None

def nijie_savename():
    return None

def spider_checkattr(check_value, getspider, **xpath):
    if check_value is not None:
        return check_value
    else:
        for k, v in xpath.items():
            replacement = getspider.scraper(**{k: v})[k]
            # print (check_value, k, v, replacement)
            if len(replacement) > 0:
                return array2string(replacement, null=False, join=False)
            else:
                return None

def check_html(text_html, browser):
    if text_html is None or len(text_html) < 100:
        if browser is not None:
            return browser.read()
        else:
            return None
    else:
        return text_html

def gen_randwait(max_wait):
    max_range = int(max_wait if max_wait < 15 else max_wait/2)
    return randint(int(max_range/2) + 1, max_range)

def get_urivalue(uri_string, key_name):
    uri_split = re.split(r'/|\?|=|&', uri_string.strip('/'))
    if len(uri_split) == 1:
        return uri_split[0]
    elif len(uri_split) > 1:
        if isinstance(key_name, int) \
        and int(key_name) <= len(uri_split):
            return uri_split[key_name]
        else:
            for i, uri_e in enumerate(uri_split):
                if key_name == uri_e or key_name in uri_e:
                    return uri_split[i+1]
                else:
                    pass
            return None
    else:
        return None

def move_oldfile(file_old, file_now, **opts):
    keep_duplicates = opts.get('keep', True)
    recycle_bin = opts.get('recyclebin', None)
    if file_old != file_now:
        if not isfile(file_now):
            print_log('debug', 'OLD FILE Move  : "%s" > "%s"', file_old, file_now)
            move(file_old, file_now)
        else:
            file_dupe = '{0}_copy.{1}'.format(*file_old.rsplit('.', 1))
            print_log('debug', 'OLD FILE Duplicate Found : "%s", "%s"', file_old, file_now)
            if keep_duplicates:
                print_log('debug', 'OLD FILE Duplicate Rename: "%s" > "%s"', file_old, file_dupe)
                move(file_old, file_dupe)
            else:
                print_log('debug', 'OLD FILE Duplicate Remove: "%s" > "%s"', file_old, file_dupe)
                pass
    else:
        print_log('debug', 'SKIP OLD File: "%s"', file_old)
        pass
    return None