#!/usr/bin/env python
# -*- coding: utf-8 -*-

from random import randint
from collections import namedtuple
from urllib.parse import unquote
from helpers.str_helper import string_sanitizer
from helpers.misc import print_log
from vars.conf_booru import supported_sites, url_type_index

# Feed String (URL), return Dict (supported_sites dict matcher)
def get_siteconfigs(site_url):
    for site in supported_sites:
        if site['fqdn'] in site_url:
            site_namedtuple = namedtuple(
                'ImgBoard', list(site.keys()))
            return site_namedtuple(**site)
        else:
            pass
    return None

def gen_randwait(wait_seconds, **options):
    wait_half = options.pop('half', False)
    wait_more = options.pop('more', 1)
    if wait_half and wait_seconds > 10:
        wait_min = int(wait_seconds/2) + 1
    else:
        wait_min = wait_seconds
    if wait_more > 1:
        wait_max = int(wait_seconds * wait_more)
        return randint(wait_min, wait_max) \
            if wait_max > wait_min \
            else wait_min
    else:
        return randint(wait_min, wait_seconds) \
            if wait_seconds > wait_min and wait_seconds > 10 \
            else randint(wait_min, int(wait_seconds * 1.5))

def gen_viewid(view_url, **options):
    deviant = options.pop('deviant', False)
    view_strip = view_url.strip('/')
    if '/' in view_strip:
        if not deviant \
        or 'www.deviantart.com' not in view_url:
            vwid_raw = view_strip.rsplit('/', 1)[1]
        else:
            vwid_raw = view_strip.rsplit('-', 1)[1]
    else:
        vwid_raw = view_strip.split('id=', 1)[-1].split('&', 1)[0]
    # print(view_url, vwid_raw)
    vwid = vwid_raw \
        if vwid_raw.isdigit() \
        else view_strip.rsplit('/', 2)[1]
    return vwid

def gen_tag(url_string, **options):
    fifo = options.pop('fifo', True)
    deviant = True if 'deviant' in url_string else False
    rule34 = True if 'rule34' in url_string else False
    if '/' in url_string:
        if rule34:
            if '?' not in url_string:
                tail_uri = unquote(url_string.strip('/').rsplit('/', 2)[1])
            else:
                tail_uri = unquote(url_string.strip('/').rsplit('tags=', 1)[1].split('&', 1)[0])
        elif deviant:
            tail_uri = url_string.strip('/').rsplit('.com/', 1)[-1].split('/', 1)[0]
        else:
            tail_uri = unquote(url_string.strip('/').rsplit('/', 1)[-1])
    else:
        tail_uri = unquote(url_string)
    if '?' in tail_uri:
        tail_fields = tail_uri.split('?', 1)[-1].split('&')
        tail_attrs = {}
        for t in tail_fields:
            x, y = t.split('=', 1)
            tail_attrs[x] = y
        tags_uri = tail_attrs.pop('tags', 'tagme')
    else:
        tags_uri = tail_uri.split('tags=', 1)[1] if \
            'tags=' in tail_uri and not deviant else \
            tail_uri
    # print(tags_uri)
    if fifo or deviant:
        return string_sanitizer(
            tags_uri.split()[0] \
                if '+' not in tags_uri \
                else tags_uri.split('+', 1)[0], 
            dir=True, 
            urldecode=True, 
            paranoia=True, 
            lowercase=True, 
        )
    else:
        return string_sanitizer(
            '+'.join([t for t in tags_uri.split() if ':' not in t]), 
            dir=True, 
            urldecode=True, 
            paranoia=True, 
            lowercase=True, 
        )

def merge_two_dicts(x, y):
    z = x.copy()   # start with x's keys and values
    z.update(y)    # modifies z with y's keys and values & returns None
    return z

def isindex(some_url):
    if all(type_i not in some_url for type_i in url_type_index):
        if '/pictures/user/' in some_url: # NG?
            return False \
                if some_url.strip('/').split('/')[-1].isdigit() \
                else True
        else:
            return True
    else:
        return False

def gen_savename(tags, id, file, **options):
    string_ntsafe = options.pop('paranoia', False)
    if tags in file and id in file:
        return file
    else:
        if id not in file:
            namewid = '{id}_{name}'.format(
                id   = id,
                name = string_sanitizer(file, 
                    urldecode = True, 
                    paranoia = string_ntsafe)
            )
        else:
            namewid = string_sanitizer(file, 
                urldecode = True, 
                paranoia = string_ntsafe)
        if tags not in file:
            savename = '{tags} {idwname}'.format(
                tags    = tags, 
                idwname = namewid
            )
        else:
            savename = namewid
        return savename
