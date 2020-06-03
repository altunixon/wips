#!/usr/bin/env python3
import requests, os, re, json, feedparser, time
from lxml import html
from bs4 import BeautifulSoup
from helpers.str_helper import urlPrefixer, string_sanitizer
from helpers.misc import countdown
from browsers.selenium import SeleniumBrowser
from browsers.scraper_lxml import html_scraper
from html2md import html2md

if __name__ == '__main__':
    try:
        path_base = os.path.dirname(os.path.realpath(__file__))
        browser_sel = SeleniumBrowser(
            capability='chrome@localhost:4445', 
            driver_bin='/usr/bin/chromedriver'
        )

        import argparse
        parser = argparse.ArgumentParser(description = 'Scraping Arguments.')
        parser.add_argument('url', nargs = '*',
            default = [],
            help = 'an URL for the accumulator.')
        parser.add_argument('-o', '--output', 
            dest = 'path_out', type = str, 
            default = None, 
            help = 'Output dir')
        parser.add_argument('-x', '--xpath', 
            dest = 'xpath', type = str, 
            default = None, 
            help = 'Xpath')
        parser.add_argument('-w', '--wait', 
            dest = 'time_wait', type = int, 
            default = 3, 
            help = 'Wait time in-between curls')
        console_args = parser.parse_args()
        for url_haz_javascript in console_args.url:
            browser_sel.get(url_haz_javascript, read=False, wait=console_args.time_wait)
            url_html = browser_sel.read()
            if console_args.xpath is not None:
                url_content = html_scraper(
                    url_html, refer = url_haz_javascript, tag_content = console_args.xpath
                )['tag_content']
            else:
                url_content = url_html
            if console_args.path_out is None:
                print (url_content)
            else:
                with open(console_args.path_out, 'w+') as url_out:
                    url_out.write(url_content)
    except Exception as excp:
        with open(os.path.join(path_base, 'error.log'), 'w+', encoding='utf-8') as ex:
            ex.write(repr(excp))
else:
    exit()