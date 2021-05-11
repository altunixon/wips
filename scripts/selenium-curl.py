#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os, time, urllib, json, re
from lxml                   import html
from browsers.selenium      import SeleniumBrowser
from browsers.login         import page_login_sel
from browsers.scrapers      import lxmlhtml_scraper

default_path = os.path.dirname(os.path.abspath(__file__))

form_example = {
    'url': '',
    'formname': '',
    'username': '',
    'formpass': '',
    'password': '',
    'submit': '',
    'home': '',
}

def login(driver, **form_data):
    loginurl = form_data.get('url', None)
    driver.get(loginurl)
    name_input = form_data.get('formname', None)
    name_value = form_data.get('username', None)
    pass_input = form_data.get('formpass', None)
    pass_value = form_data.get('password', None)
    xpath_submit = form_data.get('submit', None)
    login_verify = form_data.get('home', None)
    u = driver.find_element_by_name(name_input) #input_selector(login_infos['form_usr'])
    driver.implicitly_wait(1)
    u.send_keys(name_value)
    p = driver.find_element_by_name(pass_input) #input_selector(login_infos['form_pwd'])
    driver.implicitly_wait(1)
    p.send_keys(pass_value)
    driver.find_element_by_xpath(xpath_submit).click()
    countdown(20, txt = 'POSTING login to "%s"' % loginurl)
    driver.implicitly_wait(1)

#https://twitter.com/sherryken777/media
def main():
    global console_args, console_color
    if console_args.env_display is not None:
        os.environ['DISPLAY'] = ':%s' % console_args.env_display.strip(':')

    mybr = SeleniumBrowser(
        private     = console_args.incognito, 
        capability  = console_args.browser, 
        driverbin   = console_args.driver, 
        hide        = console_args.hide, 
        headless    = console_args.headless, 
        javascript  = True,
        verify      = False, 
        verbose     = False, 
        color       = console_color,
        wait        = 1
    )

    if console_args.login_json is not None:
        json_type, json_src = console_args.login_json.split(':', 1)
        if json_type == 'file':
            assert os.path.isfile(json_src), ('Login form data not found: "%s"' % json_src)
            with open(json_src, 'r') as jfd:
                login(mybr.driver, **json.load(jfd))
        else:
            login(mybr.driver, **json.loads(json_src))
    else:
        pass

    if console_args.py_readable:
        from readability import Document
        
    re_filter = None if console_args.result_filter is None else re.compile(console_args.result_filter)

    try:
        for url_js in console_args.urls:
            mybr.get(url_js)
            time.sleep(console_args.wait)
            if console_args.py_readable:
                html_doc = Document(mybr.read()).summary()
            elif console_args.moz_readable:
                html_doc = mybr.read()
            else:
                html_doc = mybr.read()

            if console_args.links_only or console_args.elem_xpath is not None:
                if console_args.links_only:
                    xpath_collection = {'href': '//a', 'src': '//img'}
                else:
                    xpath_collection = {}
                    for x in console_args.elem_xpath.split('|'):
                        y, z = x.split(':', 1)
                        xpath_collection[y] = z
                element_collection = lxmlhtml_scraper(html_doc, refer=url_js, **xpath_collection)
                scrape_result = []
                for tag_data, data_value in element_collection.items():
                    scrape_result.extend([x.strip() for x in data_value if len(x.strip()) > 0])

                if re_filter is not None:
                    for scrape_d in scrape_result:
                        if re_filter.search(scrape_d):
                            print (scrape_d)
                        else:
                            pass
                 else:
                    print (('\n' if console_args.linebreak else ' ').join(scrape_result))
            else:
                print (html_doc)
            
    except Exception as excp:
        raise excp

if __name__ == '__main__':
    import argparse
    from argparse import RawTextHelpFormatter
    script_name =  '.'.join(os.path.basename(__file__).split('.')[:-1]).strip()
    parser = argparse.ArgumentParser(description='URL(s)',
        argument_default=argparse.SUPPRESS, formatter_class=RawTextHelpFormatter)
    parser.add_argument('urls', nargs='*', default=[],
        help='URL(s) for the accumulator.')
    parser.add_argument('--out-file', dest='save_file', nargs='?', default=None,
        help='Save result to file, sort of like tee')
    parser.add_argument('-w', '--wait', nargs='?', type=int, default=5,
        help='wait n seconds between requests (default = 5 seconds).')
    parser.add_argument('-r', '--retry', dest='retry', type=int, default=0,
        help='Re-Try n times, default=0.')
    parser.add_argument('-b', '--browser', dest='browser', nargs='?', default='chrome',
        help='Browser type: default=chrome (via native chromewebdriver) use firefox if needed be.')
    parser.add_argument('--driver', dest='driver', nargs='?', default=None, 
        help='WebDriver binary path, by default, selenium will uses whichever apropriate webdriver found in env PATH.')
    parser.add_argument('-i', '--incognito', dest='incognito', action='store_true',
        help='Use Private browsing')
    parser.set_defaults(incognito=False)
    parser.add_argument('--hidden', dest='hide', action='store_true',
        help='Hide browser window off-screen (needed for on focus load function of twatter).')
    parser.set_defaults(hide=False)
    parser.add_argument('--headless', dest='headless', action='store_true',
        help='Headless mode.')
    parser.set_defaults(headless=False)
    parser.add_argument('--xpath', dest='env_display', nargs='?', default=None,
        help='Set output display, see /tmp/.X11-unix/X* for available display values')
    parser.add_argument('--read-moz', dest='moz_readable', action='store_true',
        help='Parse html content with readability module, needs nodejs and npm install @mozilla/readability')
    parser.set_defaults(moz_readable=False)
    parser.add_argument('--read-py', dest='py_readable', action='store_true',
        help='Parse html content with buriy\'s python implementation of the readability module, requires pip install readability-lxml')
    parser.set_defaults(py_readable=False)
    parser.add_argument('--links', dest='links_only', action='store_true',
        help='scrape html for links')
    parser.set_defaults(links_only=False)
    parser.add_argument('--xpath', dest='elem_xpath', nargs='?', default=None,
        help='Scrape html with xpath, ex: href://a[@id="xxx"]')
    parser.add_argument('--no-eol', dest='linebreak', action='store_false', 
        help='Do not print linebreak, only applies to links and xpath flag')
    parser.set_defaults(linebreak=True)
    parser.add_argument('--regex', dest='result_filter', nargs='?', default=None,
        help='Post process filter result with regex match, usually uses with links, use with other flags may produce unpredictable result')
    parser.add_argument('--login', dest='login_json', nargs='?', default=None,
        help='Login using json, also accept json file, use json:{string} or file:/path/to/file.json')
    parser.add_argument('-q', '--quiet', dest='verbose', action='store_false', 
        help='Quiet, subdue all output print only essential info, disable delete corrupt prompt')
    parser.set_defaults(verbose=True)
    console_args = parser.parse_args()
    console_color = True if os.name != 'nt' else False
    #print(main_opts)
    main()
    #time.sleep(999)
    #del mybr
else:
    pass
