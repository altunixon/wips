#!/usr/bin/env python
# -*- coding: utf-8 -*-

from classes.utils import merge_two_dicts
from helpers.str_helper import string_sanitizer

def sanic(htmlspider, **html_xpath):
    sane_xpaths     = {}
    unsane_result   = {}
    for x_key, x_path in html_xpath.items():
        if x_path is not None and len(x_path) > 0:
            sane_xpaths[x_key] = x_path
        else:
            unsane_result[x_key] = []
    if len(sane_xpaths.keys()) > 0:
        sane_result = htmlspider.scraper(**sane_xpaths)
    else:
        sane_result = {}
    return merge_two_dicts(sane_result, unsane_result)

def get_tags_str(postspider, xpath_infos, **options):
    if xpath_infos is not None:
        info_alltag = options.pop('all', False)
        xpath_pair  = options.get('pair', None)
        xpath_name  = options.get('name', None)
        xpath_count = options.get('count', None)
        # print(xpath_pair, xpath_name, xpath_count)
        post_tagscounts = postspider.scraper(
            pair        = xpath_pair, 
            text_name   = xpath_name, 
            text_count  = xpath_count, 
        )['pair']
        if len(post_tagscounts) == 0:
            return 'tagme'
        elif len(post_tagscounts) == 1:
            return string_sanitizer(
                    post_tagscounts[0]['text_name'][0].replace(' ', '_'), 
                    dir=True, 
                    urldecode=True
                ) \
                if len(post_tagscounts[0]['text_name']) > 0 \
                else 'tagme'
        else:
            if info_alltag:
                return string_sanitizer(
                    ' '.join([
                        t['text_name'][0].replace(' ', '_') \
                        for t in post_tagscounts \
                            if len(t['text_name']) > 0
                    ]), 
                    dir=True, 
                    urldecode=True
                )
            else:
                top_mvp, top_cnt = None, 0
                for tag_infos in post_tagscounts:
                    tag_nme = string_sanitizer(
                            tag_infos['text_name'][0].replace(' ', '_'), 
                            dir=True, 
                            urldecode=True
                        ) \
                        if len(tag_infos['text_name']) > 0 else None
                    tag_cnt = tag_infos['text_count'][0] \
                        if len(tag_infos['text_count']) > 0 else 0
                    tag_int = int(float(tag_cnt.strip('k')) * 1000) \
                        if 'k' in tag_cnt else int(float(tag_cnt))
                    # print(tag_infos['text_name'], tag_infos['text_count'], tag_int)
                    if tag_int > top_cnt:
                        top_mvp, top_cnt = tag_nme, tag_int
                        # print(top_mvp, top_cnt, '[Changed]')
                    else:
                        # print(top_mvp, top_cnt, '[=]')
                        pass
                return top_mvp
    else:
        return None

def get_post_lst(postspider, xpath_attrib, xpath_list):
    xpath_opts = {}
    if xpath_list is not None and len(xpath_list) > 0:
        xpath_opts[xpath_attrib] = xpath_list
        return postspider.scraper(
            **xpath_opts
        )[xpath_attrib]
    else:
        return []
