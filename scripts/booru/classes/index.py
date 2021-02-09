#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from collections import namedtuple
from classes.utils import merge_two_dicts
from classes import spider as spider_macro
from helpers.misc import print_log
from helpers.str_helper import string_sanitizer
from browsers.scrapers import lxml_spider

class page():
    def __init__(self, mech_browser, **index_options):
        self.browser = mech_browser
        self.xpath_view = index_options.get('views', None)
        self.xpath_next = index_options.get('next', None)
        self.xpath_last = index_options.get('last', None)
        self.xpath_list = index_options.get('list', None)
        self.debug = index_options.get('debug', False)
        # print (self.xpath_next, self.xpath_last, self.xpath_list)

    def list_views(self, index_html, **options):
        #global console_args
        index_is_spider     = options.get('lxml_spider', False)
        index_html_refer    = options.get('refer', None)
        list_views_uniq     = options.get('uniq', True)
        list_views_verbose  = options.get('verbose', True)
        if not index_is_spider or isinstance(index_html, str):
            indexspider = lxml_spider(
                index_html, 
                refer   = index_html_refer,
                uniq    = list_views_uniq,
                verbose = list_views_verbose)
            return spider_macro.sanic(indexspider, href = self.xpath_view)['href']
        else:
            return spider_macro.sanic(index_html, href = self.xpath_view)['href']

    def get_views(self, index_url, **options):
        view_verbose = options.get('verbose', True)
        paginator_ignores = options.get('ignores', set([]))
        view_returns = {
            'views': None, 
            'next': None, 
            'list': None, 
            'code404': False, 
            'vcount': 0, 
        }
        # print (index_url, self.xpath_view)
        view_html = self.browser.read(index_url) #, dump='/tmp/zil.html')
        if view_html is not None:
            viewsspider = lxml_spider(
                view_html, 
                refer=index_url,
                uniq=True,
                verbose=view_verbose)
            view_returns['views'] = spider_macro.sanic(viewsspider, href=self.xpath_view)['href']
            if self.xpath_list is None:
                view_returns['list'] = None
                view_default = None
            else:
                view_returns['list'] = self.info_scraper(viewsspider, self.xpath_list)
                view_default = next(filter(lambda x: x not in paginator_ignores, view_returns['list']))
            if self.xpath_next is None:
                view_returns['next'] = view_default
            else:
                view_returns['next'] = self.info_scraper(viewsspider, self.xpath_next, -1)
                if view_returns['next'] is None:
                    view_returns['next'] = view_default
            view_returns['vcount'] = len(view_returns['views'])
        else:
            view_returns['code404'] = True
        index_views_tuple = namedtuple(
            'IndexPage', list(view_returns.keys())
        )
        # print (next_page, views_href, len(views_href))
        return index_views_tuple(**view_returns)
    # ^
    # Feed String (URL), Dict (xpaths), return Dict
    def info_scraper(self, scrapespider, scrape_xpath, scrape_item = None):
        scrape_list = spider_macro.sanic(scrapespider, href=scrape_xpath)['href']
        if len(scrape_list) > 0:
            if scrape_item is None:
                return scrape_list
            else:
                return scrape_list[scrape_item] \
                    if len(scrape_list) > scrape_item \
                    else scrape_list[-1]
        else:
            return None

    def get_landing(self, landing_url, **options):
        index_verbose = options.get('verbose', True)
        landing_returns = {
            'next' : None, 'list' : None, 'last' : None, 
            'views': None, 'code404': False, 'vcount': 0
        }
        landing_html = self.browser.read(landing_url) #, dump='/tmp/zil-land.html')
        if landing_html is not None:
            landingspider = lxml_spider(
                landing_html, 
                refer=landing_url,
                uniq=True,
                verbose=index_verbose)
            if self.xpath_next is None:
                landing_returns['views'] = self.list_views(
                    landingspider, lxml_spider = True
                )
            else:
                landing_returns['next'] = self.info_scraper(landingspider, self.xpath_next, -1)
                landing_returns['last'] = self.info_scraper(landingspider, self.xpath_last, -1)
                landing_returns['list'] = self.info_scraper(landingspider, self.xpath_list, None)
                landing_returns['views'] = self.list_views(landingspider, lxml_spider=True)
                if self.debug:
                    print_log('debug', 
                        'INDEX [LAND] - Url: "%s", Next: "%s", Last: "%s", List: %s', 
                        landing_url, 
                        landing_returns['next'], 
                        landing_returns['last'], 
                        landing_returns['list'], 
                        #json.dumps(landing_returns, indent=True),
                    )
                else:
                    pass
                # print (json.dumps(landing_returns, indent=True))
            landing_returns['vcount'] = len(landing_returns['views'])
        else:
            landing_returns['code404'] = True
        landing_ntuple = namedtuple(
            'LandingPage', list(landing_returns.keys())
        )
        return landing_ntuple(**landing_returns)
