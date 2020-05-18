#!/usr/bin/env python

import requests, os, shutil, json, time
from urllib.parse import urlencode
from requests_toolbelt import MultipartEncoder

# qb v4.0.3 nox
# https://github.com/qbittorrent/qBittorrent/wiki/WebUI-API-Documentation
# POST /command/upload HTTP/1.1
qbtapi_download = '/command/download'
qbtapi_upload = '/command/upload'
qbtapi_list = '/query/torrents'
qbtapi_start = '/command/resume'
qbtapi_stop = '/command/pause'
qbtapi_rm = '/command/delete'
qbtapi_lsh = '/query/propertiesGeneral'
type_urls = ('http://', 'https://', 'magnet:', 'bc://')
type_query = ('start', 'stop', 'ls', 'rm')
# bit-wise shift use y = 1 for KB, 2 for MB, 3 for GB
byte_convert = lambda x, y: round(x / (1<<(y*10)), 2)
time_human = lambda x: time.strftime("%Z - %Y/%m/%d %H:%M:%S", time.localtime(x))

# FUNCTIONS
def time_delta(delta_seconds, **kwargs):
    delta_days, delta_seconds = divmod(delta_seconds, 86400)
    delta_hours, delta_seconds = divmod(delta_seconds, 3600)
    delta_minutes, delta_seconds = divmod(delta_seconds, 60)
    return '%s Days & %s:%s:%s' % (delta_days, delta_hours, delta_minutes, delta_seconds)

def check_result(response_data, **kwargs):
    check_len = kwargs.get('check_len', False)
    response_desc = kwargs.get('desc', None)
    response_len = int(response_data.headers.get('content-length', 0))
    if response_data.status_code == 200:
        if not check_len or response_len > 0:
            message_type, check_result = ('_OK_', True)
        else:
            message_type, check_result = ('WARN', False)
    else:
        message_type, check_result = ('ERRO', False)
        response_desc = response_data.reason
    print ('[{msg_type}] #{http_code} {check_desc}, Content-Length: {content_len} Bytes'.format(
        msg_type = message_type, 
        http_code = response_data.status_code, 
        check_desc = response_desc, 
        content_len = response_len
    ))
    return check_result

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
        # will always reply with "HTTP/1.1 200 OK" no matter if the file is actualy added or not
        return check_result(data_response, desc='POST File "%s"' % file_desc, check_len=False)
    else:
        print ('[ERRO] File "%s" missing' % a_trnt)
        return False
    
def recycle(t_file, t_bin, **kwargs):
    if t_bin is not None:
        t_name = os.path.basename(t_file)
        t_dest = os.path.join(t_bin, t_name)
        shutil.move(t_file, t_dest)
    else:
        if os.path.exists(t_file):
            os.remove(t_file)

def add_urls(t_uri, t_urls, post_data):
    # https://stackoverflow.com/questions/48211143/building-multipart-form-data-with-multiline-swift-strings-does-not-work
    # according to qbt document, urls are seperated by LF which is \n, if failed, try using CR(\r) like above exmaple instead
    data_encoded = MultipartEncoder(fields=post_data)
    data_response = requests.post(
        t_uri, data = data_encoded, 
        headers = {'Content-Type': data_encoded.content_type}
    )
    return check_result(data_response, desc='POST Urls (%s)' % len(t_urls), check_len=False)
    
def list_torrents(t_uri, **kwargs):
    query_filter = kwargs.get('filter_type', 'all')
    query_category = kwargs.get('category', None)
    query_list = {
        'filter': query_filter,
        'sort': 'state'
    }
    if query_category is not None:
        query_list['category'] = query_category
    query_url = '{api}?{query}'.format(api=t_uri, query=urlencode(query_list))
    data_response = requests.get(query_url)
    reply_check = check_result(
        data_response, desc='GET "%s" Category: %s' % (t_uri, query_category), check_len=True)
    if reply_check:
        # returns a list of dicts, use .content or .text for json formatted text
        return data_response.json()
    else:
        return None
    
def list_thash(t_uri, t_hash):
    data_response = requests.get(t_uri)
    reply_check = check_result(
        data_response, desc='GET "%s" Category: %s' % (t_uri, query_category), check_len=True)
    if reply_check:
        # returns a list of dicts, use .content or .text for json formatted text
        return data_response.json()
    else:
        return None

def post_api(t_uri, post_data, **kwargs):
    data_header = kwargs.get('headers', None)
    data_encoded = MultipartEncoder(fields=post_data)
    print ('[DEBG] POST %s to "%s"' % (data_encoded.content_type, t_uri))
    data_response = requests.post(
        t_uri, data=data_encoded, 
        headers = {'Content-Type': data_encoded.content_type} \
            if data_header is None \
            else data_header
    )
    return check_result(data_response, desc='POST Uri "%s"' % t_uri, check_len=False)
    
def print_reply(dict_json, **kwargs):
    dump_json = kwargs.get('dump', None)
    print_compact = kwargs.get('compact', False)
    print_ifs = kwargs.get('ifs', '|')
    if not print_compact:
        print (
'''================================================
File : {t_name}
    Hash     : "{t_hash}", [{t_category}], {t_adate}
    SavePath : "{t_path}"
    Status   : {t_sizenow}MB / {t_sizetotal}MB [{t_progress}%%]
    Speed    : [{t_state}] {t_speed} KB/s, ETA {t_eta}, {t_seeder} Seeders
'''.format(
            t_name = dict_json.get('name', 'UNKNOWN'), 
            t_hash = dict_json.get('hash', 'UNKNOWN'), 
            t_path = dict_json.get('save_path', 'UNKNOWN'), 
            t_category = dict_json.get('category', 'UNKNOWN'), 
            t_adate = time_human(dict_json.get('added_on', 0)), # epoch to human readable
            t_sizenow = byte_convert(dict_json.get('size', 0), 2), # Bytes to MB
            t_sizetotal = byte_convert(dict_json.get('total_size', 0), 2), # Bytes to MB
            t_progress = (dict_json.get('progress', 0) * 100), 
            t_state = dict_json.get('state', 'UNKNOWN'), 
            t_speed = byte_convert(dict_json.get('dlspeed', 0), 1), # Bytes to KB
            t_eta = time_delta(dict_json.get('eta', 0)), # timedelta seconds to human readable
            t_seeder = dict_json.get('num_seeds', 0), 
        ))
    else:
        print ('{t_hash}{ifs}{t_path}{ifs}{t_name}{ifs}{t_sizetotal}MB{ifs}{t_progress}{ifs}{t_state}'.format(
            t_name = dict_json.get('name', 'UNKNOWN'), 
            t_hash = dict_json.get('hash', 'UNKNOWN'), 
            t_path = dict_json.get('save_path', 'UNKNOWN'), 
            t_sizetotal = byte_convert(dict_json.get('total_size', 0), 2), # Bytes to MB
            t_progress = (dict_json.get('progress', 0) * 100), 
            t_state = dict_json.get('state', 'UNKNOWN'), 
            ifs = print_ifs, 
        ))
        pass
    if dump_json is not None:
        with open(dump_json, 'a+') as dja:
            dja.write(json.dump(dict_json, indent=4, sort_keys=False, ensure_ascii=False))
    else:
        pass

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
    parser.add_argument('--recyclebin', 
        dest='path_recycle', type=str, default=None, 
        help='Recycle bin path, if not provided, delete file on add success')
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
    
    if console_args.path_recycle is not None \
    and not os.path.isdir(console_args.path_recycle):
        os.makedirs(console_args.path_recycle)
    
    gen_uri = lambda x: '{api}/{uri}'.format(
        api = console_args.url_api.strip('/'), 
        uri = x.strip('/')
    )
    if console_args.query_str is None \
    or all(q != console_args.query_str for q in type_query):
        data_post = {}
        if console_args.path_out is not None and len(console_args.path_out) > 0:
            data_post['savepath'] = console_args.path_out
        if console_args.name_tag is not None and len(console_args.name_tag) > 0:
            data_post['category'] = console_args.name_tag
        else:
            if console_args.path_out is None or len(console_args.path_out) == 0:
                data_post['category'] = '_misc'
            else:
                data_post['category'] = console_args.path_out.strip(os.sep).rsplit(os.sep)[-1]

        data_post['paused'] = 'true' if not console_args.auto_start else 'false'
        post_url = gen_uri(qbtapi_upload)
        data_urls = set([])
        result_error = 0
        for a_trnt in console_args.list_trnt:
            if any(x in a_trnt for x in type_urls):
                data_urls.add(a_trnt)
            elif ':' in a_trnt:
                print ('Un-support Link Type: "%s"' % a_trnt)
            else:
                result_ok = add_file(post_url, a_trnt, data_post)
                if result_ok:
                    recycle(a_trnt, console_args.path_recycle)
                else:
                    result_error += 1
                time.sleep(1)
        if len(data_urls) > 0:
            post_url = gen_uri(qbtapi_download)
            data_post.pop('torrents', None)
            data_post['urls'] = '\n'.join(list(data_urls))
            result_ok = post_api(post_url, data_post)
            result_error += 1 if not result_ok else 0
    else:
        if console_args.query_str == 'ls':
            get_url = '{api}/{uri}'.format(
                api = console_args.url_api.strip('/'), 
                uri = qbtapi_list.strip('/')
            )
            list_reply = list_torrents(get_url, category=console_args.name_tag)
            if len(console_args.list_trnt) > 0:
                for list_data in list_reply:
                    search_name = list_data.get('name')
                    if any(x.lower() in search_name.lower() for x in console_args.list_trnt):
                        print_reply(list_data)
                    else:
                        print ('[DEBG] LS %s Not Match "%s"' % (console_args.list_trnt, search_name))
                        pass
            else:
                for t_reply in list_reply:
                    print_reply(t_reply)
            print ('[INFO] Found %s Result' % len(list_reply))
        else:
            switcher_dict = {
                'start': gen_uri(qbtapi_start), 
                'stop': gen_uri(qbtapi_stop), 
                'rm': gen_uri(qbtapi_rm), 
            }
            api_url = switcher_dict.get(console_args.query_str)
            if len(console_args.list_trnt) > 0:
                if console_args.query_str != 'rm':
                    for trnt_hash in console_args.list_trnt:
                        post_api(api_url, {'hash': trnt_hash})
                        post_check = list_thash('{api}/{t_hash}'.format(api=gen_uri(qbtapi_lsh), t_hash=trnt_hash))
                        print_reply(post_check)
                else:
                    for trnt_hash in console_args.list_trnt:
                        post_check = list_thash('{api}/{t_hash}'.format(api=gen_uri(qbtapi_lsh), t_hash=trnt_hash))
                        print_reply(post_check)
                    post_api(api_url, {'hashes': '|'.join(console_args.list_trnt)})
                    print ('[INFO] POST Deleted [%s] Torrents' % len(console_args.list_trnt))
            else:
                print ('[WARN] Needs torrent hash to run [%s]' % console_args.query_str)
else:
    pass
