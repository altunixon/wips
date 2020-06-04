#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'ALT'

#import sys
import lxml
from lxml import html
from collections import defaultdict
from helpers.misc import telltime, print_log, print_color
#from selenium.webdriver.common.keys import Keys
#from selenium.webdriver.support.select import Select


def curl_my_html(my_browser, html_href):
    curl_res = my_browser.curl(html_href)
    if curl_res is not None:
        return curl_res
    else:
        raise Exception(telltime() + 'ERROR - Page:%s - 404' % html_href)

def dump_html(html_string, html_file):
    try:
        from bs4 import BeautifulSoup
        bs=True
    except ImportError:
        bs=False
        pass
    if bs:
        pretty_html = BeautifulSoup(html_string, features="lxml").prettify()
        with open(html_file, 'w+') as o:
            o.write(pretty_html)
    else:
        with open(html_file, 'w+') as o:
            o.write(html_string)

def html_scraper(html_txt, **xpath_supplied):
    verbosity = xpath_supplied.pop('verbose', True)
    refer_url = xpath_supplied.pop('refer', None)
    filter_uniq = xpath_supplied.pop('uniq', False)
    filter_match_all = xpath_supplied.pop('match_all', False)
    if len(xpath_supplied) > 0:
        if html_txt is not None:
            # print (len(html_txt), html_txt)
            scraped_results = defaultdict(list)
            html_obj = html.fromstring(html_txt)
            paired_xpath = xpath_supplied.pop('pair', None)
            if paired_xpath is not None:
                # print ('PAIR:', paired_xpath)
                pair_html = html_scraper(html_txt, refer=refer_url, tag_content=paired_xpath, verbose=verbosity)
                # print (pair_html)
                if len(pair_html) > 0:
                    for pair_text in pair_html['tag_content']:
                        # print (pair_text)
                        pair_value = html_scraper(pair_text, refer=refer_url, **xpath_supplied, verbose=verbosity)
                        # print (pair_value)
                        if len(pair_value.keys()) < len(xpath_supplied.keys()):
                            if verbosity:
                                print_log('warn', 'SLXML [HTML] - Pair: %s Missing Attribute: %s', pair_value, xpath_supplied.keys())
                            else:
                                pass
                            if not filter_match_all:
                                scraped_results['pair'].append(pair_value)
                            else:
                                pass
                        else:
                            scraped_results['pair'].append(pair_value)
                else:
                    if verbosity:
                        print_log('warn', 'SLXML [HTML] - Pair: <%s> CANNOT FIND UPPER TAG, Url: "%s"', paired_xpath, refer_url)
                    else:
                        pass
            else:
                for xpath_attribute in xpath_supplied.keys():
                    xpath_pool = xpath_supplied[xpath_attribute] \
                        if isinstance(xpath_supplied[xpath_attribute], list) \
                        else [xpath_supplied[xpath_attribute]]
                    for xpath_accept in xpath_pool:
                        try:
                            # print (xpath_attribute, xpath_accept)
                            tag_object = html_obj.xpath(xpath_accept)
                            # print (xpath_attribute, xpath_accept, len(tag_object))
                            if len(tag_object) > 0:
                                for tag_data in tag_object:
                                    if xpath_attribute.startswith('text_'):
                                        scraped_results[xpath_attribute].append(tag_data.text_content().strip())
                                    elif xpath_attribute.startswith('tag_'):
                                        html_as_str = html.tostring(tag_data)
                                        ### DEBUG
                                        print ('SCRAPER tag_ Type:', type(html_as_str))
                                        scraped_results[xpath_attribute].append(html_as_str)
                                    else:
                                        if isinstance(tag_data, lxml.etree._ElementUnicodeResult):
                                            scraped_results[xpath_attribute].append(str(tag_data))
                                        else:
                                            for atr in tag_data.attrib.keys():
                                                if xpath_attribute.startswith(atr):
                                                    if not filter_uniq \
                                                    or tag_data.attrib[atr] not in scraped_results[xpath_attribute]:
                                                        scraped_results[xpath_attribute].append(tag_data.attrib[atr])
                                                    else:
                                                        if verbosity:
                                                            print_log('debug', 'SLXML [HTML] - Attribute %s="%s" Duplicate', xpath_attribute, tag_data.attrib[atr])
                                                        else:
                                                            pass
                                                else:
                                                    pass
                                            if len(scraped_results[xpath_attribute]) > 0:
                                                pass
                                            else:
                                                if verbosity: print_log('warn', 
                                                    'SLXML [HTML] - Url: "%s", XPath %s: <%s> Has no ATTRIB: [%s(%s)]', 
                                                    refer_url, 
                                                    scraped_results[xpath_attribute], 
                                                    xpath_accept, 
                                                    xpath_attribute, 
                                                    xpath_attribute.split('_',1)[0])
                            else:
                                if verbosity:
                                    print_log('warn', 
                                    'SLXML [HTML] - Url: "%s", XPath [%s]: <%s> Return %s', 
                                    refer_url, 
                                    xpath_attribute, 
                                    xpath_accept, 
                                    scraped_results[xpath_attribute])
                                else:
                                    pass
                        except Exception as excp:
                            print (telltime() + ' SLXML [ERR1] - Url: "%s", XPath [%s]: <%s>' % (refer_url, xpath_accept, xpath_attribute))
                            raise excp
        else:
            raise Exception(telltime() + ' SLXML [ERR1] - #404 Url: "%s"' % refer_url)
    else:
        raise Exception(telltime() + ' SLXML [ERR1] - NO VALID XPATH SUPPLIED - Url: "%s", XPaths: %s' % (refer_url, xpath_supplied))
    ### DEBUG
    for x, y in enumerate(scraped_results):
        print ('SCRAPE RETURN [%s] Type:' % x, type(y))
    return scraped_results

class spiderman():
    def __init__(self, my_html=None, **my_opts):
        self.myrefer = my_opts.pop('refer', None)
        if my_html is not None:
            self.myhtml = html.fromstring(my_html)
        else:
            # raise Exception(telltime() + ' ERROR - SLXML [OBJ#] - URL: %s 404 - DEBUG: %s' % (self.myrefer, my_opts))
            self.myhtml = None
        self.pcolor = my_opts.pop('color', False)
        self.verbose = my_opts.pop('verbose', True)
        self.uniq = my_opts.pop('uniq', False)
        self.match_all = my_opts.pop('match_all', False)
        if self.verbose:
            self._brint = print_log if not self.pcolor else print_color
        else:
            self._brint = lambda *x: None
        self._fbrint = print_log if not self.pcolor else print_color

    def title(self):
        return self.myhtml.find(".//title").text

    def scraper(self, string_html=None, **xpath_supplied):
        filter_uniq = xpath_supplied.pop('uniq', self.uniq)
        filter_notnull = xpath_supplied.pop('match_all', self.match_all)
        scraper_refer = xpath_supplied.pop('refer', self.myrefer)
        # verbose = xpath_supplied.pop('verbose', self.verbose)
        if len(xpath_supplied) > 0:
            scraped_results = defaultdict(list)
            paired_xpath = xpath_supplied.pop('pair', None)
            if paired_xpath is not None:
                #if there is a paired triggered in xpath_supplied, 
                pair_html = self.scraper(tag_content=paired_xpath)
                if len(pair_html) > 0:
                    for pair_text in pair_html['tag_content']:
                        pair_value = self.scraper(pair_text, **xpath_supplied)
                        if len(pair_value.keys()) < len(xpath_supplied.keys()):
                            self._brint('warn', 'SLXML [OBJ#] - Url: "%s", Pair: <%s>, Attr: [%s] NotFound %s', scraper_refer, paired_xpath, ', '.join(xpath_supplied.keys()), pair_value)
                            if not filter_notnull:
                                scraped_results['pair'].append(pair_value)
                            else:
                                pass
                        else:
                            scraped_results['pair'].append(pair_value)
                else:
                    self._brint('warn', 'SLXML [OBJ#] - Url: "%s", Pair: <%s>, Element NotFound', scraper_refer, paired_xpath)
            else:
                if string_html is not None:
                    myhtml_object = html.fromstring(string_html)
                else:
                    myhtml_object = self.myhtml
                if myhtml_object is not None:
                    for xpath_attribute in xpath_supplied.keys():
                        xpath_pool = xpath_supplied[xpath_attribute] \
                            if isinstance(
                                xpath_supplied[xpath_attribute], list) \
                            else [xpath_supplied[xpath_attribute]]
                        for xpath_accept in xpath_pool:
                            try:
                                if xpath_accept is None:
                                    pass
                                else:
                                    tag_object = myhtml_object.xpath(xpath_accept)
                                    if len(tag_object) > 0:
                                        for tag_data in tag_object:
                                            if xpath_attribute.startswith('text_'):
                                                # if xpath_accept.endswith('text()'):
                                                #     scraped_value = tag_data.text.strip()
                                                # else:
                                                #     scraped_value = tag_data.text_content().strip()
                                                scraped_value = tag_data.text_content().strip()
                                            elif xpath_attribute.startswith('tag_'):
                                                scraped_value = html.tostring(tag_data).decode('utf8')
                                            else:
                                                if isinstance(tag_data, lxml.etree._ElementUnicodeResult):
                                                    scraped_value = str(tag_data).strip()
                                                else:
                                                    scraped_value = ''
                                                    for atr in tag_data.attrib.keys():
                                                        if xpath_attribute == 'auto_link':
                                                            if atr == 'href' \
                                                            or atr == 'src':
                                                                scraped_value = tag_data.attrib[atr]
                                                                break
                                                            else:
                                                                pass
                                                        else:
                                                            if xpath_attribute.startswith(atr):
                                                                scraped_value = tag_data.attrib[atr]
                                                                break
                                                            else:
                                                                pass
                                                    if len(scraped_value) > 0:
                                                        pass
                                                    else:
                                                        self._fbrint('error', 'SLXML [OBJ#] - Url: "%s", XPath: <%s>, Attr: [%s] NotFound', scraper_refer, xpath_accept, xpath_attribute)
                                            if not filter_uniq \
                                            or scraped_value not in scraped_results[xpath_attribute]:
                                                scraped_results[xpath_attribute].append(scraped_value)
                                            else:
                                                pass
                                    else:
                                        self._brint('warn', 'SLXML [OBJ#] - Url: %s, Xpath [%s]: <%s> Element NotFound', scraper_refer, xpath_attribute, xpath_accept)
                            except Exception as excp:
                                self._fbrint('err', ' SLXML [ERRO] - Url: "%s", XPath [%s]: <%s> Exception', scraper_refer, xpath_attribute, xpath_accept)
                                raise excp
                else:
                    self._fbrint('err', 'SLXML [OBJ#] - Url: "%s", HTML Invalid', scraper_refer)
                    raise Exception('LXML Invalid HTML')
        else:
            self._fbrint('err', 'SLXML [OBJ#] - Url: "%s", XPaths: %s Invalid', scraper_refer, xpath_supplied)
            raise Exception('LXML Invalid XPath')
        return scraped_results
