#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import os, sys, time, platform, traceback
if platform.system() == "Windows":
    import msvcrt
from select         import select as console_select
from random         import randint
from urllib.parse   import unquote

# Database Helper
def db_init(db_connect_str):
    if db_connect_str is not None:
        if db_connect_str.lower().startswith('mysql:'):
            from databases.dldb_mysql_connector import dldb_mysql
            mydb = dldb_mysql(string=db_connect_str.split(':',1)[1])
        else:
            if os.path.isfile(db_connect_str):
                from databases.dldb_sqlite import dldb_sqlite
                mydb = dldb_sqlite(db_connect_str)
            elif db_connect_str.startswith('sqlite:'):
                from databases.dldb_sqlite import dldb_sqlite
                mydb = dldb_sqlite(db_connect_str.split(':', 1)[1])
            elif db_connect_str.startswith('json:'):
                from databases.dldb_json import json_db
                mydb = json_db(db_connect_str.split(':', 1)[1])
            else:
                mydb = None
    else:
        mydb = None
    return mydb

class wrapper_listfile():
    def __init__(self, file_path, **options):
        if ':' in file_path:
            self.list_key, self.list_file = file_path.split(':', 1)
        else:
            self.list_key, self.list_file = None, file_path
        if self.list_key is not None:
            from helpers.text_file import keyed_list
            self.list_obj = keyed_list(match=self.list_key)
            self.warn_msg = 'LIST file "{file}" is of type ReadOnly(Keyed) [{key}] and does not support %s function'.format(file=self.list_file, key=self.list_key)
            self.readonly = True
        else:
            from helpers.text_caching import text_cache
            self.list_obj = text_cache(expire=1800)
            self.warn_msg = 'LIST file "{file}" is of type TextCache, Which is wierd since its suppsed to support %s function'.format(file=self.list_file)
            self.readonly = False

    def read(self, **options):
        if self.readonly:
            return self.list_obj.read(asdict=False)
        else:
            return self.list_obj.read(self.list_file)
        
    def comment(self, file_line, **options):
        if self.readonly:
            print (self.warn_msg % 'comment()')
        else:
            self.list_obj.comment(self.list_file, file_line, **options)
    
    def upsert(self, current_list, **options)
        if self.readonly:
            print (self.warn_msg % 'upsert()')
        else:
            self.list_obj.upsert(self.list_file, current_list, comment='# ')
    
    def dump(self):
        if self.readonly:
            print (self.warn_msg % 'dump()')
        else:
            self.list_obj.dump(self.list_file)
            
    def check_dump(self):
        if self.readonly:
            print (self.warn_msg % 'check_dump()')
        else:
            self.list_obj.check_dump(self.list_file)
            
    def close(self):
        if self.readonly:
            print (self.warn_msg % 'close()')
        else:
            self.list_obj.close()

class FormatDefault(dict):
    def __missing__(self, key):
        return key

# Input Helper
def input_with_timeout_sane(prompt, timeout, default):
    """Read an input from the user or timeout"""
    print(prompt, end=' ')
    sys.stdout.flush()
    rlist, _, _ = console_select([sys.stdin], [], [], timeout)
    if rlist:
        s = sys.stdin.readline().replace('\n','')
    else:
        s = default
        print(s)
    return s

def input_with_timeout_windows(prompt, timeout, default): 
    start_time = time.time()
    print(prompt, end=' ')
    sys.stdout.flush()
    input = ''
    while True:
        if msvcrt.kbhit():
            chr = msvcrt.getche()
            if ord(chr) == 13: # enter_key
                break
            elif ord(chr) >= 32: #space_char
                input += chr
        if len(input) == 0 and (time.time() - start_time) > timeout:
            break
    if len(input) > 0:
        return input
    else:
        return default

def input_with_timeout(prompt, timeout, default=None):
    if platform.system() == "Windows":
        return input_with_timeout_windows(prompt, timeout, default)
    else:
        return input_with_timeout_sane(prompt, timeout, default)

import math
def mathround(x, d, u=True):
    return math.ceil(int(x) / d) * 10 if u else \
            math.floor(int(x) / d) * 10
    
# Print Helper    
def telltime(cmode=0):
    timestring = {0:'%Y-%m-%d - %H:%M:%S',
                  1:'%a %Y/%m/%d - %I:%M:%S %p',
                  2:'%Y-%m-%d/%H:%M:%S',
                  'iso': '%Y-%m-%dT%H:%M:%S',
                  'iso-nix': '%Y-%m-%dT%H:%M:%S%TZ', # %T (timezone) is not compatible with windows
                  'nix': '%Y-%m-%d %H:%M:%S %z',
                  'nix-human': '%Y/%b/%d %H:%M:%S %z/%Z' }
    if cmode in timestring:
        return time.strftime(timestring[cmode])
    else:
        return time.strftime(timestring[0])
        
def countdown(t, **options):
    txt = options.pop('txt', 'Continue in:')
    multiplier = int(options.pop('mutiply', 0))
    showcounter = options.pop('verbose', True)
    sleep_t = int(t) * int(multiplier) \
        if int(multiplier) > 1 \
        else int(t)
    if sleep_t > 0:
        if showcounter:
            while sleep_t >= 0:
                #mins, secs = divmod(t, 60)
                #timeformat = '{:02d}:{:02d}'.format(mins, secs)
                print_txt = '{0} {1:02d}s'.format(txt, sleep_t)
                print (print_txt, end='\r', flush=True)
                time.sleep(1)
                sleep_t -= 1
            # print(' ' * (len(print_txt) + 5), end='\r')
        else:
            time.sleep(sleep_t)
    else:
        pass

from datetime import datetime
def epoch2human(epoch_str, human_format=None):
    local_time = datetime.fromtimestamp(int(epoch_str))
    return local_time.strftime('%H:%M:%S %Z') \
        if human_format is None \
        else local_time.strftime(human_format)

from calendar import timegm
def time2epoch(time_str, format_str):
    # 2015-02-04 11:49
    # %Y-%m-%d H:%M
    utc_time = datetime.strptime(time_str, format_str)
    return timegm(utc_time)
    # -> 1236472051.807

def print_color(log_type, format_string, *insert_strings):
    if len(insert_strings) > 0:
        try:
            print_data = format_string % insert_strings
        except:
            insert_tuple = tuple(insert_strings)
            print_data = format_string % insert_tuple
    else:
        print_data = format_string
    if log_type == 'info':
        message_type= '\033[1;34mINFO\033[0m' # Blue
    elif log_type == 'ok' or log_type == 'success':
        message_type= '\033[1;32m_OK_\033[0m' # Green
    elif log_type == 'warn' or log_type == 'warning':
        message_type= '\033[1;33mWARN\033[0m' # Yellow
    elif log_type == 'error' or log_type == 'err':
        message_type= '\033[1;4;31mERR_\033[0m' # Red
    elif log_type == 'debug' or log_type == 'dbg':
        message_type = '\033[1;36mDBUG\033[0m' # Cyan
    else:
        message_type = '\033[1;35m%s\033[0m' % '{:_^4.4}'.format(
            log_type.upper()) # Purple
    print (
        '{time} [{type}]: {msg}'.format(
            time = telltime('nix'), 
            type = message_type, 
            msg  = print_data
        )
    )

def print_log(log_type, format_string, *insert_strings):
    if len(insert_strings) > 0:
        try:
            print_data = format_string % insert_strings
        except:
            insert_tuple = tuple(insert_strings)
            print_data = format_string % insert_tuple
    else:
        print_data = format_string
    if   log_type == 'info': message_type= 'INFO'
    elif log_type == 'ok' or log_type == 'success': message_type= 'OK'
    elif log_type == 'warn' or log_type == 'warning': message_type= 'WARN'
    elif log_type == 'error' or log_type == 'err': message_type= 'ERR'
    elif log_type == 'debug' or log_type == 'dbg': message_type= 'DBUG'
    else: message_type = log_type
    print(
        '{time} [{type:_^4.4}]: {msg}'.format(
            time = telltime('nix'), 
            type = message_type, 
            msg  = print_data
        )
    )

def bandwith_calc(time_start, time_end, size_downloaded):
    time_total = time_end - time_start
    # speed_ave = (size_downloaded / 1024) / time_total if \
    #     int(time_total) > 0 else \
    #     size_downloaded / 1024
    speed_ave = (size_downloaded / 1024) / time_total
    return {'duration': time_total, 'speed': speed_ave}

def print_progress_bar(curr, total, **styling):
    mlabel  = styling.pop('label', 'Progress')
    bar_color = styling.pop('color', False)
    bar_len = int(styling.pop('length', 32))
    if total > 0 and total >= curr:
        # Shows progress in 9608█
        bar_prog = int((curr * bar_len) / total)
        bar_remn = bar_len - bar_prog
        if bar_color:
            #message  = '%s: |\033[32m{bar_l:%s}\033[0m{bar_r:%s}| {percent:>3}%% {done:>9} of {total:9}' % (mlabel, bar_prog, bar_remn)
            message  = '%s: |\033[32m{bar_l}\033[0m\033[1;33m{bar_r}\033[0m| {percent:>3}%% {done:>9} of {total:9}' % mlabel
        else:
            #message  = '%s: |{bar_l:%s}{bar_r:%s}| {percent:>3}%% {done:>9} of {total:9}' % (mlabel, bar_prog, bar_remn)
            message  = '%s: |{bar_l}{bar_r}| {percent:>3}%% {done:>9} of {total:9}' % mlabel
        print('\r', end='')
        print(message.format(
                bar_l   = chr(9608) * bar_prog,
                bar_r   = chr(183) * bar_remn, 
                percent = int((curr * 100) / total),
                done    = humanize_bytes(curr),
                total   = humanize_bytes(total)
                #done    = curr,
                #total   = total
            ),
        end='')
    else:
        # indeterminite 10060❌/10006✖
        print('\r', end='')
        rand_seed = int(bar_len/3)
        bar_prog = randint(rand_seed, bar_len - rand_seed * 2)
        bar_remn = bar_len - bar_prog
        if bar_color:
            #message  = '%s: |\033[33m{bar_l:%s}\033[0m\033[31m{bar_r:%s}\033[0m| {percent:>3}%% {done:>9} of {total:9}' % (mlabel, bar_prog, bar_remn)
            message  = '%s: |\033[33m{bar_l}\033[0m\033[31m{bar_r}\033[0m| {percent:>3}%% {done:>9} of {total:9}' % mlabel
        else:
            message  = '%s: |{bar_l}{bar_r}| {percent:>3}%% {done:>9} of {total:9}' % mlabel
        print(message.format(
                bar_l   = chr(9608) * bar_prog,
                bar_r   = chr(10006) * bar_remn, 
                percent = '???',
                done    = humanize_bytes(curr),
                total   = humanize_bytes(total)
            ), 
        end=''
        )

# Calculate
def humanize_bytes(size_bytes, precision=2, **options): 
    """Return a humanized string representation of a number of size_bytes. 
    Assumes `from __future__ import division`. 
    >>> humanize_size_bytes(1) 
    '1 byte' 
    >>> humanize_size_bytes(1024) 
    '1.0 kB' 
    >>> humanize_size_bytes(1024*123) 
    '123.0 kB' 
    >>> humanize_size_bytes(1024*12342) 
    '12.1 MB' 
    >>> humanize_size_bytes(1024*12342,2) 
    '12.05 MB' 
    >>> humanize_size_bytes(1024*1234,2) 
    '1.21 MB' 
    >>> humanize_size_bytes(1024*1234*1111,2) 
    '1.31 GB' 
    >>> humanize_size_bytes(1024*1234*1111,1) 
    '1.3 GB' 
    """
    abbrevs = ( 
        (1<<50, 'PB'), 
        (1<<40, 'TB'), 
        (1<<30, 'GB'), 
        (1<<20, 'MB'), 
        (1<<10, 'kB'), 
        (1,     'bytes') 
    )
    if size_bytes is not None:
        human_format = '{value:.%sf} {unit}' % precision
        if int(size_bytes) == 1: 
            return human_format.format(value=1, unit='byte')
        else:
            pass
        for factor, suffix in abbrevs: 
            if int(size_bytes) >= factor: break
            else: pass
        return human_format.format(
            value=(float(size_bytes) / float(factor)), 
            unit=suffix
            )
    else:
        return None

# ./class_browser.py ./class_browser_selenium.py
def cal_duration(tm_bs, tm_es, humanize=False):
    tm_dur = int(tm_es - tm_bs)
    tm_dur = 1 if tm_dur == 0 else tm_dur
    if humanize:
        tm_str = '{:02}:{:02}:{:02}'.format(
            tm_dur // 3600, 
            tm_dur % 3600 // 60, 
            tm_dur % 60)
    else:
        tm_str = str(tm_dur)
    return tm_str

def seconds2human(int_seconds):
    if int_seconds < 60:
        return '{:02d}s'.format(int_second)
    elif 60 < int_seconds < 3600:
        m, s = divmod(int_seconds, 60)
        return '{:02d}m{:02d}s'.format(m, s)
    else:
        m, s = divmod(int_seconds, 60)
        h, m = divmod(m, 60)
        return '{:02d}h{:02d}m{:02d}s'.format(h, m, s)
# Misc Func
def check_null(v_ariable):
    if v_ariable is None:
        return True
    else:
        return True if len(v_ariable) == 0 else False
#grep -lri raise_trace ./
# ./bato.py ./booru.py ./class_browser_selenium.py ./exht.py ./module_page_login.py ./nyaa.py ./sanka.py
def raise_trace(debugl=None):
    print('\n\n\n')
    traceback.print_exc()
    print('\n\nDEBUG - Message: "%s"\n\n' % debugl)
    print("Press return to exit..")
    input()
    exit()
# Used by ./module_page_login.py
def check_either(c_one, c_other, c_in):
    if (c_one in c_in and c_other not in c_in) or (c_one not in c_in and c_other in c_in):
        return True
    else:
        return False
    
# Text files
def text_write(text_file, text_lines, write_mode='w+'):
    try:
        if isinstance(text_lines, str):
            with open(text_file, write_mode) as file_desc:
                file_desc.write(text_lines + '\n')
        else:
            with open(text_file, write_mode) as file_desc:
                for l in text_lines:
                    file_desc.write(l + '\n')
        return True
    except Exception as excp:
        print ('Unable to write File: "%s"\n' % text_file, excp)
        return False

#===============================================================================
# DEBUG
#===============================================================================
# Debug purpose only, not used anywhere
def print_list(text_list, comment=''): 
    l_n = 0
    if isinstance(text_list, list):
        for text_line in text_list:
            if isinstance(text_line, list):
                print_list(text_list)
            else:
                print(('%s: "%s"' % (comment, text_line)) if len(comment) > 0 else ('%i: "%s"' % (l_n, text_line)))
            l_n += 1
    else:
        print('%s (type=string): "%s"' % (comment, text_list))

# Debug        
def printntable(thisarray, rowofn=None):
    i = len(thisarray)
    if rowofn is None:
        n = 3
        while i % n != 0:
            n += 1
        n = 5 if n == i and i / 2 > 5 else i
    else:
        n = rowofn if i > rowofn else 1

    print_array = '['
    p = 0
    while p < i:
        print_array += '"%s"' % thisarray[p]
        if (p + 1) % n == 0 and (p + 1) != i:
            print_array += ',\n'
        else:
            if (p + 1) != i:
                print_array += ','
        p += 1
    print_array += ']'
    return print_array
    
#DEPRECATED
# Used by ./nijie.py
def list_normalize(list_items, leading_char='#'): 
    norm_list = [] 
    for l_item in list_items: 
        while leading_char * 2 in l_item: 
            l_item = l_item.replace(leading_char * 2, leading_char) 
        cond_a = (l_item not in norm_list) if l_item.startswith('#') else ('#' + l_item not in norm_list) 
        cond_b = (l_item.lstrip('#') not in norm_list) 
        if l_item == '': 
            norm_list.append(l_item) 
        elif (cond_a and cond_b): 
            norm_list.append(l_item) 
    return norm_list

#only used by nijie.py
def return_url(your_url, url_prefix=None):
    if url_prefix is not None:
        if not your_url.startswith(url_prefix):
            return_url = '%s/%s' % (url_prefix.rstrip('/'), your_url.lstrip('/'))
        else:
            return_url = your_url
    else:
        if not your_url.startswith('https://') and not your_url.startswith('http://'):
            return_url = 'http://' + your_url.lstrip('/')
        else:
            return_url = your_url
    return return_url

def array2string(array, **options):
    string_join = options.pop('join', False)
    string_sep = options.pop('sep', '_')
    string_limit = options.pop('limit', 0)
    string_empty = options.pop('null', False)
    if string_empty:
        array_norm = array
    else:
        array_norm = [str(s).strip() for s in array if len(str(s).strip()) > 0]
    if string_limit > 0 and string_limit < len(array_norm):
        return_string = array_norm[:string_limit]
        if string_join:
            return string_sep.join(return_string) \
                if len(return_string) > 0 \
                else None
        else:
            return return_string[0] \
                if len(return_string) > 0 \
                else None
    else:
        if string_join:
            return_string = string_sep.join(array_norm) \
                if len(array_norm) > 0 \
                else None
        else:
            return_string = None
            for s in array_norm:
                if len(str(s).strip()) > 0:
                    return str(s).strip()
                else:
                    pass
            return return_string


# Not used anywhere, debug functions
def array2chunk(array, chunksize):
    chunk_array = []
    for i in range(0, len(array), chunksize):
        chunk_array.append(array[i:i+chunksize])
    return chunk_array

#grep -lri create_folder ./ > ./booru.py ./exht.py ./nijie.py ./nyaa.py ./sanka.py
def create_folder(full_path): 
    f_dir = os.path.normpath(full_path.strip()) 
    if not os.path.exists(f_dir):
        try:
            os.makedirs(f_dir)
        except:
            raise
    else:
        pass
    return f_dir
# Unused
def dict_seperator(text_str, value_sep):
    if value_sep in text_str:
        str_key = text_str[:text_str.find(value_sep)].strip()
        str_val = text_str[text_str.find(value_sep) + 1:].strip()
        if len(str_key) == 0:
            str_key = None
        if len(str_val) == 0:
            str_val = None
        return {'key': str_key, 'value': str_val}
# Unused
def dict_combine(default_dict, supplied_dict):
    combined_dict = {'debug':''}
    for dict_key in list(default_dict.keys()):
        if dict_key in list(supplied_dict.keys()):
            combined_dict[dict_key] = supplied_dict[dict_key]
            combined_dict['debug'] += '%s=file;' % dict_key
        else:
            combined_dict[dict_key] = supplied_dict[dict_key]
            combined_dict['debug'] += '%s=default;' % dict_key
    return combined_dict
