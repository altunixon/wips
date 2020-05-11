#!/usr/bin/env python

import requests, os, json
from urllib.parse import urlencode
from requests_toolbelt import MultipartEncoder

# qb v4.0.3 nox
# https://github.com/qbittorrent/qBittorrent/wiki/WebUI-API-Documentation
# POST /command/upload HTTP/1.1
qbtapi_download = '/command/download'
qbtapi_upload = '/command/upload'
qbtapi_list = '/query/torrents'
qbtapi_start = '/command/resume'
qbtapi_pause = '/command/pause'
qbtapi_delete = '/command/delete'
type_urls = ('http://', 'https://', 'magnet:', 'bc://')
type_query = ('start', 'stop', 'ls', 'rm')

# FUNCTIONS
def check_result(json_response, **kwargs):
    json_desc = kwargs.get('desc', 'no-desc')
    check_field = kwargs.get('field', None)
    check_value = kwargs.get('value', None)
    if json_response is None or len(json_response) == 0:
        print ('Invalid JSON response [%s]' % json_response)
        return False
    else:
        print (json_response)
        try:
            dict_response = json.loads(json_response)
        except Exception as excp:
            print ('Malformed JSON response\n', excp)
            return False
        if check_field is not None and check_value is not None:
            response_value = json_response.get(check_field, None)
            if response_value is not None:
                return True if response_value == check_value else False
            else:
                print ('Could not find [%s] in\n%s' % (
                    check_field, 
                    json.dumps(dict_response, indent=4, sort_keys=True, ensure_ascii=False)
                ))
                return False
        else:
            print ('Skip response checking due to un-defined check values: %s' % kwargs)
            return True

def add_file(t_uri, t_file, post_form={}):
    post_data = dict(post_form)
    post_data['torrents'] = None
    file_desc = os.path.basename(t_file)
    # print (t_uri)
    if os.path.isfile(t_file):
        with open(t_file, 'rb') as rb_file:
            post_data['torrents'] = (file_desc, rb_file, "application/x-bittorrent")
            data_encoded = MultipartEncoder(fields=post_data)
            data_response = requests.post(
                t_uri, data = data_encoded, 
                headers = {'Content-Type': data_encoded.content_type}
            )
        # print (data_response.headers)
        if data_response.status_code == 200:
            # return check_result(
            #     data_response.json(), 
            #     desc=file_desc, 
            #     field='PLACEHOLDER', 
            #     value='PLACEHOLDER'
            # )
            print ('[OK__] #%s File "%s" [Succeeded]' % (data_response.status_code, file_desc))
            return True
        else:
            print ('[FAIL] #%s File "%s" [Failed]' % (data_response.status_code, file_desc))
            return False
    else:
        print ('[ERR_] File "%s" missing' % a_trnt)
        return False

def add_urls(t_uri, t_urls, post_form={}):
    post_data = dict(post_form)
    post_data['urls'] = list(t_urls)
    # https://stackoverflow.com/questions/48211143/building-multipart-form-data-with-multiline-swift-strings-does-not-work
    # according to qbt document, urls are seperated by LF which is \n, if failed, try using CR(\r) like above exmaple instead
    # post_data['urls'] = '\n'.join(list(t_urls))
    # data_encoded = MultipartEncoder(fields=post_data)
    data_response = requests.post(
        t_uri, json = post_data, # ??? might not be accepted with current header, maybe will work with 'application/json'
        headers = {'Content-Type': 'multipart/form-data'}
        # data = data_encoded, 
        # headers = {'Content-Type': data_encoded.content_type}
    )
    if data_response.status_code == 200:
        return check_result(
            data_response.json(), 
            desc='magnet/url', 
            field='PLACEHOLDER', 
            value='PLACEHOLDER'
        )
    else:
        return False

def list_torrents(t_uri, t_category, **kwargs):
    query_filter = kwargs.get('filter', 'all')
    query_category = kwargs.get('category', None)
    query_list = {
        'filter': query_filter,
        'sort': 'state'
    }
    if query_category is not None:
        query_list['category'] = query_category
    query_url = '{api}?{query}'.format(api=t_uri, query=urlencode(query_list))
    data_response = requests.get(query_url)
    if data_response.status_code == 200 \
    and data_response.headers['content-length'] > 0:
        return data_response.json()
    else:
        return None
    
def list_print(dict_json, **kwargs):
    return None

# END FUNCTIONS

if __name__ == '__main__':
    path_base = os.path.dirname(os.path.realpath(__file__))
    
    import argparse
    parser = argparse.ArgumentParser(description='Scraping Arguments.')
    parser.add_argument(
        dest='list_trnt', nargs='*', default=[],
        help='List of Torrents to process, could be a mix of file paths, urls, or magnets')
    parser.add_argument('--api', 
        dest='url_api', type=str, default='http://127.0.0.1:8080', 
        help='API\'s URL, default "http://127.0.0.1:8080"')
    parser.add_argument('-o', '--output', 
        dest='path_out', type=str, default=None, 
        help='Save path, default unspecified, uses application\'s default save location')
    parser.add_argument('-t', '--tag', 
        dest='name_tag', type=str, default=None, 
        help='Tag torrents under "Category", default no tagging')
    parser.add_argument('-q', '--query', dest='query_str', type=str, default=None, 
        help='Run various query such as: start|stop|ls|rm')
    parser.add_argument('-f', '--filter', dest='query_filter', type=str, default=None, 
        help='Filter torrent list. Allowed filters: all, downloading, completed, paused, active, inactive')
    parser.add_argument('-s', '--start', dest='auto_start', action='store_true', 
        help='Start torrent immediately')
    parser.set_defaults(auto_start = False)
    console_args = parser.parse_args()
    
    data_post = {}
    if console_args.path_out is not None and len(console_args.path_out) > 0:
        data_post['savepath'] = console_args.path_out
    if console_args.name_tag is not None and len(console_args.name_tag) > 0:
        data_post['category'] = console_args.name_tag
    data_post['paused'] = 'true' if not console_args.auto_start else 'false'

    if console_args.query_str is None \
    or all(q != console_args.query_str for q in type_query):
        post_url = '{api}/{uri}'.format(
            api = console_args.url_api.strip('/'), 
            uri = qbtapi_upload.strip('/')
        )
        data_urls = set([])
        result_error = 0
        for a_trnt in console_args.list_trnt:
            if any(x in a_trnt for x in type_urls):
                data_urls.add(a_trnt)
            elif ':' in a_trnt:
                print ('Un-support Link Type: "%s"' % a_trnt)
            else:
                result_action = add_file(post_url, a_trnt, data_post)
                result_error += 1 if not result_action else 0
                # TODO add cleanup fuction
                # file_cleanup(a_trnt, result_action)
        if len(data_urls) > 0:
            post_url = '{api}/{uri}'.format(
                api = console_args.url_api.strip('/'), 
                uri = qbtapi_download.strip('/')
            )
            data_post.pop('torrents')
            result_action = add_urls(post_url, data_urls, data_post)
            result_error += 1 if not result_action else 0
    else:
        pass
else:
    pass
