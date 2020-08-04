#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, json, feedparser, time
from datetime               import datetime
from helpers.misc           import print_log
from helpers.str_helper     import urlStripper, arr2str, string_sanitizer
from databases.json_pseudo  import json_keystore
import urllib.parse as urllib_parse

nyaa_opts = {
    'category': [
        'anime - raw', 
        'anime - english-translated', 
        'literature - raw'
    ], 
    'categoryId': ['1_2', '1_4', '5_1', '3_3'], 
    'keyword': ['720','1080','raw']
}

nyaa_search = 'https://nyaa.si/?page=rss&q={query}'

def search_urlformat(search_str):
    return nyaa_search.format(
        query = urllib_parse.quote(search_str)
    )

def main(rss_feeds, **rss_options):
    global console_args, print_decor
    if console_args.rss_file is not None:
        with open(console_args.rss_file, 'r') as rf:
            rss_feeds.extend(rf.read().splitlines(False))
    else:
        pass
    if console_args.dump_json is not None:
        rss_store = json_keystore(console_args.dump_json)
        rss_store.load(verbose = console_args.verbose)
    else:
        rss_store = None
    new_text = []
    for rss_string in rss_feeds:
        if '://' in rss_string:
            a_feed = feedparser.parse(rss_string)
        else:
            a_feed = feedparser.parse(search_urlformat(rss_string))
        for post in a_feed.entries:
            # print (type(post), json.dumps(post, indent=True)); exit()
            if console_args.category is None \
            and console_args.categoryid is None:
                rss_accept_post = True
            else:
                match_cat = True \
                    if console_args.category is not None \
                    and console_args.category.lower() \
                        in post.nyaa_category.lower() \
                    else False
                match_cid = True \
                    if console_args.categoryid is not None \
                    and console_args.categoryid.lower() \
                        in post.nyaa_categoryid.lower() \
                    else False
                if match_cat or match_cid:
                    rss_accept_post = True
                else:
                    rss_accept_post = False
            # print ('DEBUG!!!!!!', rss_accept_post, console_args.keyword)
            if rss_accept_post and console_args.keyword is not None:
                rss_accept_post = True \
                    if console_args.keyword.lower() in post.title.lower() \
                    else False
                # print ('DEBUG!!!!!!', console_args.keyword.lower(), post.title.lower(), rss_accept_post)
            else:
                pass
            # print ('DEBUG!!!!!!', rss_accept_post)
            if rss_accept_post:
                if rss_store is not None:
                    rss_block = {
                        'title': post.title, 
                        'size': post.nyaa_size, 
                        'category': post.nyaa_category, 
                        'categoryId': post.nyaa_categoryid, 
                        'link': post.link, 
                        'magnet': post.links
                    }
                    if rss_string not in rss_store.json.keys():
                        new_record = rss_store.update(
                            rss_string, {post.guid: rss_block}
                        )
                    else:
                        if post.guid not in rss_store.json[rss_string].keys():
                            new_record = True
                            rss_store.json[rss_string][post.guid] = rss_block
                        else:
                            new_record = False
                else:
                    new_record = True
                if console_args.verbose and print_decor:
                    print (
                        "[{msg}: {category}] {title} | {link}".format(
                            msg = 'NEW!' if new_record else 'SKIP', 
                            category = post.nyaa_category, 
                            title = post.title, 
                            link = post.link
                        )
                    )
                else:
                    if new_record:
                        new_text.append(post.link)
                        if console_args.verbose:
                            print (post.link)
                        else:
                            pass
                    else:
                        pass
            else:
                pass

    if console_args.dump_text is not None \
    and len(new_text) > 0:
        with open(console_args.dump_text, 'a+') as dump:
            dump.write('\n'.join(new_text))
    else:
        pass

    if rss_store is not None:
        rss_store.json['new'] = {
            'links': new_text, 
            'date': datetime.now().strftime(
                "%Y/%m/%d %a %H:%M:%S {zone}".format(zone = time.tzname[0]))
        }
        # rss_store.json['new']['links'] = new_text
        # rss_store.json['new']['date'] = datetime.now().strftime(
        #     "%Y/%m/%d %a %H:%M:%S {zone}".format(zone = time.tzname[0]))
        rss_store.dump(indent = 4, ensure_ascii = False)
    else:
        pass
    
    return len(new_text)

if __name__ == '__main__':
    working_path = os.path.dirname(os.path.realpath(__file__))
    import argparse
    from argparse import RawTextHelpFormatter
    parser = argparse.ArgumentParser(
        description='Download URL to "./downloads"',
        argument_default=argparse.SUPPRESS, 
        formatter_class=RawTextHelpFormatter)
    parser.add_argument(dest='rss_list', nargs='*', default=None,
        help='RSS feed for the accumulator')
    parser.add_argument('-f', '--file', dest='rss_file', nargs='?', default=None, 
        help='Using external listfile.txt')
    parser.add_argument('-o', '--output-dir', dest='save_path', nargs='?', 
        default=os.path.join(working_path, 'downloads'), 
        help='Download Destination, Over written by list file appendix if custom dir exists in listfile')
    parser.add_argument('-j', '--json', dest='dump_json', nargs='?', default=None, 
        help='dump to JSON file, implied quiet mode.')
    parser.add_argument('-t', '--txt', dest='dump_text', nargs='?', default=None, 
        help='dump to TEXT file, implied quiet mode.')
    parser.add_argument('--categoryid', dest='categoryid', nargs='?', default=None, 
        help='Filter media matches Category')
    parser.add_argument('--category', dest='category', nargs='?', default=None, 
        help='Filter media matches CategoryID')
    parser.add_argument('-k', '--keyword', dest='keyword', nargs='?', default=None, 
        help='Filter media contains keyword in description/title')
    parser.add_argument('-q', '--quiet', dest='verbose', action='store_false', 
        help='Quiet, subdue all output print only essential info, disable delete corrupt prompt')
    parser.set_defaults(verbose=True)
    console_args = parser.parse_args()
    print_decor = True \
        if console_args.dump_json is None \
        and console_args.dump_text is None \
        else False
    count_new = main(console_args.rss_list)
    if console_args.verbose and print_decor:
        print_log(
            'debug', 
            'FINISHED\nDL Path: "%s"\n   File: "%s"\n   Urls: %s', 
            console_args.save_path, 
            console_args.rss_file, 
            len(console_args.rss_list)
        )
    else:
        if console_args.verbose:
            print ('# Found [%s] New Torrent(s)' % count_new)
        else:
            pass
else:
    pass
