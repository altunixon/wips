#!/usr/bin/env python3

import requests, os, json

# FUNCTIONS

# END FUNCTIONS

if __name__ == '__main__':
    path_base = os.path.dirname(os.path.realpath(__file__))
    
    import argparse
    parser = argparse.ArgumentParser(description='Scraping Arguments.')
    parser.add_argument(
        dest='list_trnt', nargs='*', default=[],
        help='List of Torrents to process, could be a mix of file paths, urls, or magnets')
    parser.add_argument('--api', 
        dest='url_api', type=str, default='127.0.0.1:8080'
        help='API\'s URL')
    parser.add_argument('-o', '--output', 
        dest='path_out', type=str, default=None, 
        help='Save path')
    parser.add_argument('-s', '--start', dest = 'auto_start', action = 'store_true')
    parser.set_defaults(auto_start = False)
    console_args = parser.parse_args()
    
    data_post = []
    data_urls = set([])
    data_magnets = set([])
    for a_trnt in console_args.list_trnt:
        if '://' in a_trnt or 'magnet:' in a_trnt:
            data_urls.add(a_trnt)
        else:
            if os.path.isfile(a_trnt):
                # ('images', ('foo.png', open('foo.png', 'rb'), 'image/png'))
                a_file = os.path.basename(a_trnt)
                with open(a_trnt, 'rb') as byte_data:
                    data_post.append(('torrents', (a_file, byte_data, 'application/x-bittorrent')))
    data_post.append(('urls', tuple(list(data_urls))))
        
    
