#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import json
from os.path import isfile
from collections import defaultdict, namedtuple
#Class Text reader. consider split this to another file?
class text_file():
    def __init__(self, t_file):
        self.file = t_file
        self.check = False if not isfile(self.file) else True
        
    def read_raw(self):
        with open(self.file, 'rt') as text_file:
            return text_file
    
    def write_raw(self, tcontent, mode='a'):
        with open(self.file, mode) as text_file:
            text_file.write(tcontent + '\n')
        
    def read_as_list(self):
        with open(self.file, 'rt') as text_file:
            raw_lines = text_file.readlines()
        processed_lines = [raw_line.rstrip() for raw_line in raw_lines]
        return processed_lines
    
    def read_no_comment(self):
        valid_lines = []
        with open(self.file, 'rt') as text_file:
            for line in text_file.readlines():
                line_stripd = line.strip()
                if not line_stripd.startswith('#') and len(line_stripd) > 0: 
                    valid_lines.append(line_stripd)
                else:
                    pass
        return valid_lines
        
    def read_as_config(self): 
        configs = {} 
        for line in self.read_no_comment(): 
            c_value = line[line.find('=') + 1:].strip() 
            c_ident = line[:line.find('=')].strip()
            if c_ident not in list(configs.keys()):
                configs[c_ident] = c_value
            else:
                configs[c_ident] = '%s|%s' % (configs[c_ident], c_value)
        return configs
    
    def read_as_prioritize(self, **opts):
        return_http = True \
            if 'type' in opts.keys() \
            and opts['type'].lower() == 'http' \
            else False
        return_list = opts['list'] if 'list' in opts.keys() and isinstance(opts['list'], bool) else True
        hp_lines = set([])
        np_lines = set([])
        lp_lines = set([])
        for line in self.read_no_comment(): 
            if line.startswith('$'): 
                np_lines.add(line.lstrip('$'))
            elif line.startswith('@'): 
                hp_lines.add(line.lstrip('@')) 
            else: 
                lp_lines.add(line.strip())
        if return_list:
            prioritize_results = []
            for line_list in [hp_lines, np_lines, lp_lines] : 
                for line_text in line_list:
                    if return_http:
                        if line_text.startswith('http://') or line_text.startswith('https://'): 
                            prioritize_results.append(line_text)
                        else:    
                            print ('warn', 'FILE - Read Invalid URL "%s"' % url)
                    else:
                        prioritize_results.append(line_text)
        else:
            muh_https = lambda x: [u for u in x if u.startswith('http://') or u.startswith('https://')]
            prioritize_results = {
                'hp': muh_https(hp_lines), 
                'np': muh_https(np_lines), 
                'lp': muh_https(lp_lines)
            }
        return prioritize_results
    
    def write_to_add(self, text_list, comment=False): 
        with open(self.file, 'a') as text_file:
            for text_item in text_list: 
                write_item = '#' + text_item if comment else text_item
                text_file.write('%s\n' % write_item)
      
    def write_to_over(self, file_path, text_list):
        with open(self.file, 'w') as text_file:
            for text_item in text_list:
                text_file.write('%s\n' % text_item)
          
    def update_list(self, text_item, leading_char='# '):
        text_list = self.read_as_list()
        for list_item in text_list:
            if text_item in list_item:
                i = text_list.index(list_item)
                text_list[i] = leading_char + list_item if not list_item.startswith(leading_char) else list_item
        return text_list 
      
    def write_to_update(self, text_item, leading_char='# '):
        #current_file = list_normalize(self.read_as_list())
        updated_list = self.update_list(text_item, leading_char)
        self.write_to_over(self.file, updated_list)
        
    def pixivutil_norm(self):
        # from module_utility_functions import text_file
        # text_file('/cygdrive/c/Users/Alt/Google Drive/CROSS PLATFORM/git-repo/notes-txt/list_combined.txt').pixivutil_norm()
        pixiv_out  = '%s_normalized.txt' % self.file.rsplit('.',1)[0]
        pixiv_list = set([])
        with open(pixiv_out, 'a') as text_file:
            items_list = self.read_as_list()
            for list_item in items_list:
                if list_item not in pixiv_list:
                    pixiv_list.add(list_item)
                    text_file.write('%s\n' % list_item)
                else:
                    pass
        return len(pixiv_list)

# xml to array of dicts
class xml_file():
    def __init__(self, xfile):
        from xml.dom import minidom
        self.check = True if isfile(xfile) else False
        self.xdoc = minidom.parse(xfile)
        
    def xml2dictarray(self, iname):
        xitms = self.xdoc.getElementsByTagName(iname)
        xtags = []
        for xitem in xitms:
            xtval = xitem.childNodes
            xattr = dict(list(xitem.attributes.items()))
            xtext = []
            for xnode in xtval:
                if xnode.nodeType == xnode.TEXT_NODE:
                    xtext += xnode.data.strip().splitlines()
                    if len(xtext) > 0: xtags.append({'text':xtext, 'attrib':xattr})
                    else: pass
        return xtags if len(xtags) > 0 else None

class ini_file():
    def __init__(self, ifile):
        import configparser
        self.ini_reader = configparser.ConfigParser(allow_no_value=True)
        self.file  = ifile

    def read_file(self, r_file=None):
        in_file = r_file if r_file is not None else self.file
        if isfile(in_file):
            self.ini_reader.read(in_file)
            ini_dict = {}
            for k in self.ini_reader.sections():
                ini_dict[k] = list(self.ini_reader[k])
            return ini_dict
        else:
            return None

    def write_file(self, w_file=None):
        out_file = w_file if w_file is not None else self.file
        with open(out_file, 'w+') as configfile:
            self.ini_reader.write(configfile)

class json_file():
    def __init__(self, jfile):
        self.file  = jfile
        if isfile(jfile):
            try:
                with open(jfile, 'r') as r:
                    self.json_dict = json.load(r)
            except Exception as excp:
                print('JSON Return None,', excp)
                self.json_dict = None
        else:
            self.json_dict = None

    def read_file(self, r_file=None):
        if r_file is None:
            return self.json_dict
        else:
            if isfile(r_file):
                with open(r_file, 'r') as r:
                    my_json_dict = json.load(r)
                return my_json_dict
            else:
                return None

    def write_file(self, w_file=None, j_dict=None):
        out_file = w_file if w_file is not None else self.file
        if j_dict is None:
            pass
        else:
            if isfile(out_file):
                with open(out_file, 'w+') as w:
                    json.dump(
                        j_dict, w, 
                        indent = 4, 
                        sort_keys = True, 
                        ensure_ascii = False)
            else:
                pass

class keyed_list():
    def __init__(self, **list_options):
        self.file_path = list_options.get('file', None)
        self.file_style = list_options.get('style', 'ini')
        self.check = isfile(list_file)
        self.read_key = list_options.get('match', None)
        self.list_key = None
        self.list_cache = []
        
    def read_position(self, get_key, list_content, **options):
        print ('PLACEBO for keyed_list compatibility')
        return None
    # text_caching compatibility purpose
    def comment(self, file_name, file_line, **options):
        print ('PLACEBO for keyed_list compatibility')
        return None
                
    def check_dump(self, file_name, **options):
        print ('PLACEBO for keyed_list compatibility')
        return None
    
    def close(self):
        print ('PLACEBO for keyed_list compatibility')
        return None
    
    def upsert(self, file_name, list_current, **options):
        print ('PLACEBO for keyed_list compatibility')
        return None
    
    def dump(self, file_name):
        print ('PLACEBO for keyed_list compatibility')
        return None

    def read(self, file_path, **options):
        read_asdict = options.get('asdict', False)
        if self.check:
            with open(file_path, 'r') as lf:
                content_lines = [t for t in lf.read().splitlines() if len(t) > 0 and not t.startswith('#')]
            list_keys = []
            list_range= []
            for i, l in enumerate(content_lines):
                if l.startswith('['):
                    l_k = l.strip('[').strip(']').strip()
                    list_keys.append(l_k)
                    list_range.append(i) # line counter, for linebreak/bracket detecting
                else:
                    pass
            list_range.append(len(content_lines)) # add eof index

            list_dict = defaultdict(list)
            #print(list_dict, list_range)
            for i, k in enumerate(list_keys):
                l_b = list_range[i]+1
                l_e = list_range[i+1]
                list_sub = content_lines[l_b:l_e]
                #print(k, l_b, l_e)
                if '|' in k:
                    k_fomat = k.split('|', 1)[-1]
                else:
                    k_fomat = k
                if '{}' in k_fomat:
                    list_flines = [k_fomat.format(e) if '://' not in e else e for e in list_sub]
                elif '%s' in k_fomat:
                    list_flines = [(k_fomat % e) if '://' not in e else e for e in list_sub]
                else:
                    list_flines = [(k_fomat + e) if '://' not in e else e for e in list_sub]
                #print(k, list_flines)
                list_dict[k] = list_flines
  
            if not read_asdict:
                if self.read_key is not None:
                    for k, v in list_dict.iteritems():
                        if read_key in k:
                            self.list_key = k
                            self.list_cache = v
                            return self.list_cache
                        else:
                            pass
                else:
                    for k, v in list_dict.iteritems():
                        self.list_cache += v
                    return self.list_cache
            else:
                return list_dict
        else:
            return []

class custom_list():
    def __init__(self, d_file, k_marker="[]"):
        self.file   = d_file
        self.key_m  = list(k_marker)
        self.check  = True if isfile(d_file) else False

    def read(self, **options):
        if self.check:
            with open(self.file, 'rt') as lfile:
                lines_raw = [l for l in lfile.read().splitlines() if len(l) > 0 and not l.startswith('#')]
            to_list     = options.pop('to_list', True)
            key_prefix  = options.pop('key_prefix', True)
            key_match   = options.pop('key_match', None)
            lines_key = []
            for l in lines_raw:
                if any(l.startswith(lk) for lk in self.key_m):
                    if l not in lines_key:
                        lines_key.append(l)
                    else:
                        pass
                else:
                    pass
            if len(lines_key) > 0:
                lines_dic = defaultdict(list)
                l_end   = len(lines_raw)
                n_start = 0
                n_end   = l_end
                for i, k in enumerate(lines_key):
                    if lines_raw[i] == k:
                        n_start = i + 1
                    else:
                        if any(lines_raw[i].startswith(lk) for lk in self.key_m):
                            if i > n_start:
                                n_end = i
                                break
                            else:
                                pass
                        else:
                            if i == l_end - 1:
                                n_end = l_end
                            else:
                                pass
                    lines_dic[k].extends(lines_raw[n_start:n_end])
                #print(lines_dic)
                if to_list:
                    read_return = []
                    for k, v in lines_dic.items():
                        k_clean = k
                        for km in self.key_m: k_clean = k_clean.strip(km)
                        k_match = False if key_match is not None and key_match not in k else True
                        if k_match:
                            if key_prefix:
                                for i in v:
                                    read_return.append(k_clean + i.strip())
                            else:
                                read_return += v
                        else:
                            pass
                    return read_return
                else:
                    return lines_dic
            else:
                return lines_raw if to_list else {}
        else:
            return [] if to_list else {}
