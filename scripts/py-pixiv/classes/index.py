#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from collections import namedtuple
from browsers.scrapers import lxml_spider
from helpers.misc import countdown, print_log, print_color
from helpers.str_helper import urlPrefixer, string_sanitizer
from classes.utils import pixiv_userid, nijie_id, gen_artistname, check_html, spider_checkattr
from vars.conf_pixiv import pixiv_fqdn, xpath_pindex_header, xpath_pindex_hpjump, xpath_pindex_nextpg, xpath_pview_pair, xpath_pview_link, xpath_ptype_svg
from vars.conf_nijie import nijie_fqdn, xpath_nindex_header, xpath_nindex_hpjump, xpath_nindex_nextpg, xpath_nview_pair, xpath_nview_link
from random import randint

##########################
# COMMON CLASS FUNCTIONS #
def index_init(self, index_url, index_html, **options):
    self.url = index_url
    self.uid = options.pop('uid', None)
    if self.uid is None:
        self.uid = self.gen_uid(self.url, keyw='id')
    else:
        pass
    self.refer = options.pop('refer', None)
    self.verbose = options.pop('verbose', False)
    self.indexspider = lxml_spider(
        index_html, 
        verbose = self.verbose, 
        refer = self.refer
    )
    # self.macros = macros(self.browser, verbose = self.verbose)
    self._brint  = print_log if not options.pop('color', False) else print_color

def spider_chknul(self, page_html):
    if page_html is None:
        pagespider = self.indexspider
    else:
        pagespider = lxml_spider(page_html, verbose=self.verbose, refer=self.refer)
    return pagespider

def common_userhp(self, **options):
    index_info = self.indexspider.scraper(
        text_head = self.xpath_header, 
        href = self.xpath_hpjump
    )
    index_userhp = gen_artistname(
        index_info['text_head'],
        index_info['href']
    )
    return string_sanitizer(index_userhp)

def common_nextpg(self, page_html=None, **options):
    index_pool = options.pop('pool', set([]))
    # index_refer = options.pop('refer', None)
    pagespider = self.spider_chknul(page_html)
    next_page_detected = pagespider.scraper(href=self.xpath_nextpg)['href']
    ## print (next_page_detected)
    if len(next_page_detected) > 0:
        next_page_lastest = next_page_detected[-1]
        next_page = next_page_lastest \
            if next_page_lastest not in index_pool \
            else None
    else:
        next_page = None
    return next_page

############################
# PIXIV SPECIFIC FUNCTIONS #
def gen_uid_pixiv(self, pixiv_url, **options):
    return pixiv_userid(pixiv_url, **options)

def pixiv_views(self, page_html=None, **options):
    views_dict = {
        'views': [], 
        'multipage': set([]), 
        'singlepage': set([]), 
        'total': 0, 
        'count_multipage': 0, 
        'next': None
    }
    pagespider = self.spider_chknul(page_html)
    views_dict['views'] = pagespider.scraper(
        pair = xpath_pview_pair, 
        href = xpath_pview_link, 
        text_title = xpath_pview_link, 
        # tag_newtype = xpath_ptype_svg,
        uniq = True,
        match_all = True, 
    )['pair']
    next_page = pagespider.scraper(href=self.xpath_nextpg)['href']
    views_dict['next'] = next_page[-1] if len(next_page) > 0 else None
    
    views_dict['total'] = len(views_dict['views'])
    views_dict['multipage'] = set([
        h for h in pagespider.scraper(
            href = xpath_ptype_svg, 
            uniq = True,
            match_all = True, 
        )['href'] \
        if len(h) > 0
    ])
    views_dict['singlepage'] = set([])
    for h in views_dict['views']:
        if len(h['href']) > 0:
            if len(h['href'][0]) > 0 \
            and h['href'][0] not in views_dict['multipage']:
                views_dict['singlepage'].add(h['href'][0])
            else:
                pass
        else:
            pass
    views_dict['count_multipage'] = len(views_dict['multipage'])
    self._brint('debug', 'INDEX [VIEW] - Found %s Views in Index: "%s"', views_dict['total'], self.url)
    views_table = namedtuple('IndexViews', list(views_dict.keys()))
    return views_table(**views_dict)

############################
# NIJIE SPECIFIC FUNCTIONS #
def gen_uid_nijie(self, nijie_url, **options):
    return nijie_id(nijie_url, **options)

def nijie_views(self, page_html=None, **options):
    views_dict = {
        'views': [], 
        'posts': set([]), 
        'total': 0, 
        'next' : None
    }
    pagespider = self.spider_chknul(page_html)
    views_dict['views'] = pagespider.scraper(
        pair = xpath_nview_pair, 
        href = xpath_nview_link, 
        title = xpath_nview_link, 
        uniq = True,
        match_all = True, 
    )['pair']
    next_page = pagespider.scraper(href=self.xpath_nextpg)['href']
    views_dict['next'] = next_page[-1] if len(next_page) > 0 else None
    views_dict['posts'] = set([x['href'] for x in views_dict['views']])
    views_dict['total'] = len(views_dict['posts'])
    views_table = namedtuple('IndexViews', list(views_dict.keys()))
    return views_table(**views_dict)

############################
# PIXIV CLASS CONSTRUCTION #
pixiv_index = type("pixiv_index", (), {
    "gen_uid": gen_uid_pixiv, 
    "xpath_header": xpath_pindex_header, 
    "xpath_hpjump": xpath_pindex_hpjump, 
    "xpath_nextpg": xpath_pindex_nextpg, 
    "__init__": index_init,
    "spider_chknul": spider_chknul, 
    "userhp": common_userhp, 
    "nextpg": common_nextpg, 
    "views" : pixiv_views
})

############################
# NIJIE CLASS CONSTRUCTION #
nijie_index = type("nijie_index", (), {
    "gen_uid": gen_uid_nijie, 
    "xpath_header": xpath_nindex_header, 
    "xpath_hpjump": xpath_nindex_hpjump, 
    "xpath_nextpg": xpath_nindex_nextpg, 
    "__init__": index_init,
    "spider_chknul": spider_chknul, 
    "userhp": common_userhp, 
    "nextpg": common_nextpg, 
    "views" : nijie_views
})
