#!/usr/bin/env python

import requests, os, json
from requests_toolbelt import MultipartEncoder

# qb v4.0.3 nox
# https://github.com/qbittorrent/qBittorrent/wiki/WebUI-API-Documentation
# POST /command/upload HTTP/1.1

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
        dest='url_api', type=str, default='http://127.0.0.1:8080/command/upload', 
        help='API\'s URL, default "http://127.0.0.1:8080/command/upload"')
    parser.add_argument('-o', '--output', 
        dest='path_out', type=str, default=None, 
        help='Save path, default unspecified, uses application\'s default save location')
    parser.add_argument('-t', '--tag', 
        dest='name_tag', type=str, default=None, 
        help='Tag torrents under "Category", default no tagging')
    parser.add_argument('-s', '--start', dest = 'auto_start', action = 'store_true', 
        help='Start torrent immediately')
    parser.set_defaults(auto_start = False)
    console_args = parser.parse_args()
    
    data_post = {}
    if console_args.path_out is not None and len(console_args.path_out) > 0:
        data_post['savepath'] = console_args.path_out
    if console_args.name_tag is not None and len(console_args.name_tag) > 0:
        data_post['category'] = console_args.name_tag
    data_post['paused'] = 'true' if not console_args.auto_start else 'false'

    data_urls = set([])
    for a_trnt in console_args.list_trnt:
        if '://' in a_trnt or 'magnet:' in a_trnt:
            data_urls.add(a_trnt)
        else:
            if os.path.isfile(a_trnt):
                data_post['torrents'] = (
                    os.path.basename(a_trnt), 
                    open(a_trnt, 'rb'), 
                    "application/x-bittorrent"
                )
                data_encoded = MultipartEncoder(fields=data_post)
                data_response = requests.post(
                    console_args.url_api,
                    data = data_encoded, 
                    headers = {'Content-Type': data_encoded.content_type}
                )
                print ('[#{status}] Content:\n{response}'.format(
                    status = data_response.status_code, 
                    response = data_response.headers
                    # response = json.dumps(data_response.headers, indent=4, sort_keys=True, ensure_ascii=False)
                    )
                )
            else:
                print ('[ERR_] File "%s" missing' % a_trnt)
else:
    pass
