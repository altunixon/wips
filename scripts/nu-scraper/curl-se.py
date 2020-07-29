#!/usr/bin/env python3
import os
from bs4 import BeautifulSoup
from browsers.selenium import SeleniumBrowser
from browsers.scraper_lxml import html_scraper

if __name__ == '__main__':
    try:
        import argparse
        parser = argparse.ArgumentParser(description = 'Scraping Arguments.')
        parser.add_argument('url', nargs = '*',
            default = [],
            help = 'an URL for the accumulator.')
        parser.add_argument('-o', '--output', 
            dest = 'path_out', type = str, 
            default = None, 
            help = 'Output path')
        parser.add_argument('-b', '--bs4', dest = 'soup_out', action = 'store_true')
        parser.set_defaults(soup_out = False)
        parser.add_argument('-x', '--xpath', 
            dest = 'xpath', type = str, 
            default = None, 
            help = 'Xpath')
        parser.add_argument('-w', '--wait', 
            dest = 'time_wait', type = int, 
            default = 3, 
            help = 'Wait for page to load before reading source HTML.')
        console_args = parser.parse_args()

        path_base = os.path.dirname(os.path.realpath(__file__))
        browser_sel = SeleniumBrowser(
            capability='chrome@localhost:4445',
            driver_bin='/usr/bin/chromedriver'
        )

        if len(console_args.url) > 0:
            url_haz_javascript = console_args.url[0]
            browser_sel.get(url_haz_javascript, read=False, wait=console_args.time_wait)
            url_html = browser_sel.read()
            if console_args.xpath is not None:
                url_article = html_scraper(
                    url_html, refer = url_haz_javascript, tag_content = console_args.xpath
                )['tag_content']
                if len(url_article) > 0:
                    url_content = url_article[0].decode(encoding='UTF-8')
                    # type bytes!? lxml! WTF!?, temporary using decode to convert to str
                    # fixed in browsers.scraper_lxml, maybe...
                else:
                    url_content = 'URL : "%s"\nXpath: <%s>\nNOTFOUND\n' % (url_haz_javascript, console_args.xpath)
            else:
                url_content = url_html
            # print (type(url_content))
            if console_args.soup_out:
                soup_content = BeautifulSoup(url_content, 'html.parser')
                url_content = soup_content.prettyfy()
            else:
                pass
            if console_args.path_out is None:
                print (url_content)
            else:
                with open(console_args.path_out, 'w+', encoding='utf-8') as url_out:
                    url_out.write(url_content)
        else:
            pass
    except Exception as excp:
        with open(os.path.join(path_base, 'error.log'), 'w+', encoding='utf-8') as ex:
            ex.write(repr(excp))
else:
    exit()
