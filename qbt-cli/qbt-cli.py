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
        dest='url_api', type=str, default='http://127.0.0.1:8080/api/v2/torrents/add'
        help='API\'s URL, default "http://127.0.0.1:8080/api/v2/torrents/add"')
    parser.add_argument('-o', '--output', 
        dest='path_out', type=str, default=None, 
        help='Save path, default unspecified, uses application\'s default save location')
    parser.add_argument('-t', '--tag', 
        dest='name_tag', type=str, default=None, 
        help='Tag torrents under "Category", default no tagging')
    parser.add_argument('-s', '--start', dest = 'auto_start', action = 'store_true')
    parser.set_defaults(auto_start = False)
    console_args = parser.parse_args()
    
    data_post = {}
    data_urls = set([])
    for a_trnt in console_args.list_trnt:
        if '://' in a_trnt or 'magnet:' in a_trnt:
            data_urls.add(a_trnt)
        else:
            if os.path.isfile(a_trnt):
                if 'torrents' not in data_post.keys():
                    data_post['torrents'] = []
                else:
                    pass
                # ('images', ('foo.png', open('foo.png', 'rb'), 'image/png'))
                a_file = os.path.basename(a_trnt)
                with open(a_trnt, 'rb') as byte_data:
                    data_post['torrents].append(tuple(a_file, byte_data, "application/x-bittorrent"))
                              
    data_post['urls'] = tuple(list(data_urls))
    if console_args.path_out is not None and len(console_args.path_out) > 0:
        data_post['savepath'] = console_args.path_out
    else:
        pass
    if console_args.name_tag is not None and len(console_args.name_tag) > 0:
        data_post['category'] = console_args.name_tag
    data_post['paused'] = 'true' if not console_args.auto_start else 'false'
    data_encoder = MultipartEncoder(fields=data_post)
    
