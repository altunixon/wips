#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from helpers.misc import print_log
from urllib.parse import unquote, urlsplit

windows_illegal = ['<', '>', ':', '"', '\'', '$', '\\', '/', '?', '|', '*', '\t', ',', ';']

def urlStripper(url, match=-1):
    url_prefix  = "{0.scheme}://{0.netloc}".format(urlsplit(url))
    url_uris    = [unquote(u) for u in url.replace(url_prefix, '').split('/') if len(u) > 0]
    return {'prefix': url_prefix,
            'uris'  : url_uris,
            'match' : url_uris[match] if len(url_uris) > 0 else None}

def urlPrefixer(uri, url_prefix=None):
    if url_prefix is None or uri is None:
        return uri
    else:
        url_splitd = urlsplit(url_prefix)
        if uri.startswith('http://') \
        or uri.startswith("%s:" % url_splitd.scheme):
            return uri
        else:
            # print ('{0.scheme}://{0.netloc}{1}'.format(url_splitd, uri))
            if len(uri) > 0:
                # print (uri, url_prefix, default_url)
                if uri.startswith('://'):
                    return '{0.scheme}{1}'.format(url_splitd, uri)
                elif uri.startswith('//'):
                    return '{0}:{1}'.format(url_splitd.scheme, uri)
                elif uri.startswith('/'):
                    return '{0.scheme}://{0.netloc}{1}'.format(url_splitd, uri)
                else:
                    if url_prefix.endswith('='):
                        return url_prefix + uri.strip()
                    else:
                        return '{0.scheme}://{0.netloc}/{1}'.format(
                                url_splitd, uri.strip('/')
                            ) \
                            if len(url_splitd.path.strip('/')) == 0 \
                            or url_splitd.path in uri \
                            or uri.startswith('/') \
                            else '{0.scheme}://{0.netloc}{0.path}{1}'.format(
                                url_splitd, uri.strip('/')
                            )
            else:
                return None


def string_sanitizer(sane_string, **options):
    if sane_string is not None:
        global windows_illegal
        space_unwanted  = ' \t\n\r'
        space_char      = options.pop('space', ' ')
        space_replace   = options.pop('nospace', None)
        sane_maxlen     = int(options.pop('maxlen', 0))
        sane_default    = options.pop('default', None)
        # type_file       = options.pop('file', False)
        # type_dir        = options.pop('dir', False)
        strip_chars     = options.pop('strip', None)
        # dir_illegals = [' ','.','\'', '"',':','..']
        # if type_file:
        #     if '.' in sane_string:
        #         raw_ext  = sane_string.rsplit('.', 1)[1]
        #         sane_ext = raw_ext if 2 < len(raw_ext) < 5 else 'bin'
        #     else:
        #         sane_ext = 'bin'
        # else:
        #     sane_ext = None

        # if type_dir:
        #     for il in dir_illegals:
        #         if sane_string.startswith(il):
        #             fill_r = len(il)
        #             sane_string = sane_string[
        #                 sane_string.index(il) + fill_r:]
        #         else:
        #             pass
        #         if sane_string.endswith(il):
        #             sane_string = sane_string[:sane_string.rfind(il)]
        #         else:
        #             pass
        # else:
        #     pass

        if options.pop('urldecode', False):
            sane_string = unquote(sane_string)
        else:
            pass

        if options.pop('paranoia', False):
            for i in set(sane_string):
                if i in set('0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ -_.+=[]{}()#&@$'):
                    pass
                else:
                    sane_string = sane_string.replace(i, '-')
        else:
            if strip_chars is not None: 
                for strip_this in list(strip_chars): 
                    if strip_this in sane_string: 
                        sane_string = sane_string.replace(strip_this, '')
                    else:
                        pass
            else:
                pass
            if options.pop('ascii', False):
                sane_string = ''.join(
                    [s if ord(s) < 128 else space_char for s in sane_string]
                )
            else:
                pass
                
        for ex_ch in windows_illegal:
            if ex_ch in sane_string:
                #print('String: "%s" contains character "%s"' % (sane_string,ex_ch))
                sane_string = sane_string.replace(ex_ch, '-')
            else:
                pass
        if sane_maxlen is not None and sane_maxlen > 0:
            if len(sane_string) > sane_maxlen:
                if space_char not in sane_string:
                    rep_spaces = ['-','_']
                    if any(rep_space in sane_string \
                    for rep_space in rep_spaces):
                        char_split = {}; split_count = 0
                        for rep_space in rep_spaces:
                            char_num = sane_string.count(rep_space)
                            char_split[rep_space] = char_num
                        for split_key in char_split:
                            if char_split[split_key] > split_count:
                                split_count = char_split[split_key]
                                split_char  = split_key
                            else:
                                pass
                    else:
                        split_char = None
                else:
                    split_char = space_char
                if split_char is not None:
                    word_arr = [s for s in sane_string.split(split_char) if len(s) > 0]
                    while len(split_char.join(word_arr)) > sane_maxlen: 
                        word_arr = word_arr[:-1]
                    sane_string = split_char.join(word_arr)
                    if word_arr[-1].startswith('('): sane_string += '_)'
                    else: pass
                    space_char = split_char
                else:
                    sane_string = sane_string[:sane_maxlen]
                print('This string is too long! at: (%i) characters, the str length limit is (%i)...' % (len(sane_string), sane_maxlen))
            else:
                sane_string = space_char.join(
                    [s for s in sane_string.split(space_char) if len(s) > 0]
                )
        else:
            pass
        re_string = re.sub(' +', space_char, sane_string).strip(space_unwanted).strip('.')
        sanitized_string = re_string.strip(space_char) \
            if space_replace is None \
            else re_string.replace(space_char, space_replace)
        #if type_file and sane_ext is not None:
        #    return '{name}.{ext}'.format(
        #        name=sanitized_string, 
        #        ext=sane_ext
        #    )
        #else:
        #    return sanitized_string
        return sanitized_string \
            if len(sanitized_string) > 0 \
            else sane_default
    else:
        return None

def arr2str(haystack, needle=None):
    if needle is not None:
        result_str = None
        if len(haystack) > 0:
            for astraw in haystack:
                if needle in astraw:
                    result_str = astraw
                    break
                else:
                    pass
        else:
            pass
    else:
        result_str = haystack[0] if len(haystack) > 0 else None
    return result_str

def str2num(mystr, **kargs):
    spacer = kargs['space'] if 'space' in list(kargs.keys()) else '_'
    anumbering = ''
    for chari in range(len(mystr)):
        charc = mystr[chari]
        charn = mystr[chari + 1] if chari < len(mystr) - 1 else 'EOF'
        if charc.isdigit():
            if charn.isdigit(): anumbering += charc
            elif any(charn == s for s in ['.','&','-']): anumbering += charc + charn
            else: anumbering += charc + spacer if chari < len(mystr) - 1 else charc
    return anumbering.rstrip(spacer)

def ifsDetector(delimited_string, default_ifs=None):
    possible_delims = {}
    for ch in delimited_string:
        if ch not in possible_delims.keys():
            possible_delims[ch] = delimited_string.count(ch)
        else:
            pass
    result_delim, number_delim = None, 0
    for d in possible_delims.keys():
        if d in '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ':
            possible_delims.pop(d)
        else:
            if possible_delims[d] > number_delim:
                result_delim, number_delim = d, possible_delims[d]
            print(result_delim, number_delim)
    return result_delim

def nameGenerator(name_str):
    return None

def MangaTitleEx(folder_str, **kargs):
    spacer = kargs['space'] if 'space' in list(kargs.keys()) else '_'
    bracket_pairs= {'[':']', '(':')', '{':'}'}
    special_chars = ('<','>',':','"','$','\\','/','?','|','*')
    bracket_sign = ('~','=')
    manga_title = folder_str
    for brack_open, brack_close in list(bracket_pairs.items()):
        while brack_open in manga_title and brack_close in manga_title:
            bo_split = manga_title.split(brack_open, 1)
            manga_title = bo_split[0] + bo_split[-1].split(brack_close,1)[-1]
            print_log('debug', manga_title)
        if brack_open in manga_title: manga_title = manga_title.replace(brack_open, spacer)
        if brack_close in manga_title: manga_title = manga_title.replace(brack_close, spacer)
    for asign in bracket_sign:
        while manga_title.count(asign) > 1:
            sn_split = manga_title.split(asign,2)
            manga_title = sn_split[0] + spacer + sn_split[-1]
            print_log('debug', manga_title)
        if asign in manga_title: manga_title = manga_title.replace(asign, spacer)
    accelements = [werd for werd in re.split('_| ', manga_title) if len(werd) > 0]
    while len(spacer.join(accelements)) > 50: accelements = accelements[:-1]
    return spacer.join(accelements).strip(spacer)
    
def MangaTitle(folder_str, **kargs):
    spacer = kargs['space'] if 'space' in list(kargs.keys()) else '_'
    bracket_pairs= {'[':']', '(':')', '{':'}'}
    special_chars = ('<','>',':','"','$','\\','/','?','|','*')
    bracket_sign = ('~','=')
    for brack_open, brack_close in list(bracket_pairs.items()):
        #if debug_msg: print 'BRACKS:', brack_open, brack_close
        if brack_open in folder_str or brack_close in folder_str:
            count_open = folder_str.count(brack_open) # count available brackets
            count_close= folder_str.count(brack_close)# same as above
            if count_open == -1: # no open brackets in string
                folder_str = folder_str.replace(brack_close,' ')
            elif count_close== -1: # no close brackets in string
                folder_str = folder_str.replace(brack_open, ' ')
            else:
                open_indexes = [i for i in range(0,len(folder_str)) if folder_str[i] == brack_open]
                close_indexes= [i for i in range(0,len(folder_str)) if folder_str[i] == brack_close]
                for oi in open_indexes:
                    if max(close_indexes) < oi:
                        folder_str = folder_str[:oi] + ' ' + folder_str[oi+1:]
                        break
                    else:
                        for ci in close_indexes:
                            if oi < ci:
                                folder_str = folder_str[:oi] + (' '*(ci+1-oi)) + folder_str[ci+1:]
                                break
                            else:
                                folder_str = folder_str[:ci] + ' ' + folder_str[ci+1:]
                if folder_str.find(brack_close) != -1:
                    folder_str = folder_str.replace(brack_close, ' ')
        else:
            pass
    for asign in bracket_sign:
        while folder_str.count(asign) > 1:
            asplit = folder_str.split(asign)
            folder_str = '%s %s' % (asplit[0],asplit[-1]) if len(asplit) > 2 else folder_str
    accelements = [werd for werd in re.split('_| ', folder_str) if len(werd) > 0]
    
    while len(spacer.join(accelements)) > 50:
        accelements = accelements[:-1]
    returnname = spacer.join(accelements)
    for ex_ch in special_chars:
        if ex_ch in returnname: returnname = returnname.replace(ex_ch, spacer)
    return returnname.strip(spacer)
