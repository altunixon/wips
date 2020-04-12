#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from time import time
from collections import defaultdict

class text_cache():
    def __init__(self, **cache_opts):
        #self.dump_path = os.path.join(os.getcwd(), 'text_cache') if \
        #                'dump' not in cache_opts.keys() else \
        #                cache_opts['dump']
        # Expiration Default = Never, accepted value = Seconds (int)
        self.expiration = int(cache_opts.pop('expire', 900))
        self.debug = int(cache_opts.pop('debug', False))
        #self.type       = cache_opts.pop('type', 'list')
        self.store      = {}

    def k(self):
        return set(self.store.keys())

    def append(self, text_file, text_line):
        if text_file in self.store:
            self.store[text_file]['lines'].append(text_line)
        else:
            self.read(text_file, retval=False)
            self.store[text_file]['lines'].append(text_line)

    def insert(self, text_file, text_lines):
        if text_file in self.store:
            self.store[text_file]['lines'] = text_lines
        else:
            self.read(text_file, retval=False)
            self.store[text_file]['lines'] = text_lines

    def update_parse(self, text_file):
        current_lines = []
        for file_line in self.read_file(text_file):
            comment_marker = None
            for ck, cs in self.store[text_file]['comments'].items():
                if file_line.strip() in cs:
                    comment_marker = ck
                    break
                else:
                    comment_marker = None
            if comment_marker is not None:
                current_lines.append(
                    '%s %s' % (comment_marker, file_line)
                )
            else:
                current_lines.append(file_line)
        return current_lines

    def update(self, text_file, **options):
        update_force = options.pop('force', False)
        if text_file not in self.store.keys():
            self.read(text_file, comment = True, retval = False)
        else:
            current_time = int(time())
            if update_force or self.expiration == 0:
                self.store[text_file]['create'] = current_time
                self.store[text_file]['lines'] = self.update_parse(text_file)
            else:
                if current_time - self.store[text_file]['create'] \
                > self.expiration:
                    if self.debug:
                        print ('Read: Update "%s"@n%s' % (text_file, current_time))
                    self.store[text_file]['create'] = current_time
                    self.store[text_file]['lines'] = self.update_parse(text_file)
                else:
                    if self.debug:
                        print ('Read: Update Skip "%s"@[m%s - c%s = %s < x%s]' % (
                            text_file, current_time, 
                            self.store[text_file]['create'], 
                            current_time - self.store[text_file]['create'], 
                            self.expiration)
                            )
                    pass

    def upsert(self, text_file, upsert_lines, **options):
        include_comment = options.pop('comment', None)
        if text_file in self.store:
            for uline in upsert_lines:
                if uline not in self.store[text_file]['lines']:
                    if include_comment is None:
                        self.store[text_file]['lines'].append(uline)
                    else:
                        if '{c}{t}'.format(c=include_comment, t=uline) \
                        not in self.store[text_file]['lines']:
                            self.store[text_file]['lines'].append(uline)
                        else:
                            pass
                else:
                    pass
        else:
            self.insert(text_file, upsert_lines)

    def read(self, text_file, **options):
        return_list = options.pop('retval', True)
        return_asis = options.pop('comment', True)
        current_time = int(time())
        if text_file not in self.store.keys():
            self.store[text_file] = {
                'lines': [], 
                'create': current_time, 
                'comments': defaultdict(set)
            }
            if self.debug:
                print ('Read: New "%s"@%s' % (text_file, current_time))
            self.store[text_file]['lines'] = self.read_file(text_file)
        else:
            if self.debug:
                print ('Read: Skip "%s"@%s' % (text_file, 'null'))
            pass
        if return_list:
            if return_asis:
                return self.store[text_file]['lines']
            else:
                return [
                    l.strip() \
                    for l in self.store[text_file]['lines'] \
                        if not l.strip().startswith('#') \
                        and len(l.strip()) > 0
                ]
        else:
            return None

    def comment(self, text_file, text_line, **options):
        text_comment = options.pop('comment', None)
        # self.read(text_file, retval=False) # update mode, return None
        for i, item in enumerate(self.store[text_file]['lines']):
            if text_line.strip() == item.strip():
                comment_string = '#' \
                    if text_comment is None \
                    or len(text_comment) == 0 \
                    else text_comment
                self.store[text_file]['comments'][comment_string].add(
                    text_line.strip())
                self.store[text_file]['lines'][i] = '%s %s' % (comment_string, text_line.strip())
                if self.debug:
                    print ('Commented: "%s %s"' % (text_comment, text_line))
            else:
                pass
        self.store[text_file]['modify'] = int(time())

    def check_dump(self, text_file, **options):
        # mode_update = options.pop('update', False)
        if text_file in self.store.keys():
            # if mode_update:
            #     pass
            # else:
            #     pass
            if self.expiration > 0:
                check_time = int(time())
                if check_time - self.store[text_file]['create'] > self.expiration:
                    if self.debug:
                        print ('Check Dump: Write "%s"@n%s' % (text_file, check_time))
                    self.update(text_file)
                    self.dump(text_file)
                    self.store[text_file]['create'] = check_time
                else:
                    if self.debug:
                        print ('Check Dump: Skip "%s"@[n%s - c%s = %s < %s]' % (text_file, check_time, self.store[text_file]['create'], check_time - self.store[text_file]['create'], self.expiration))
                    pass
            else:
                if self.debug:
                    print ('Check Dump: Skip, "%s"@%s dump on Close' % (text_file, self.store[text_file]['create']))
                pass
        else:
            pass

    def read_file(self, text_file, **options):
        strip_trail = options.pop('strip', False)
        if os.path.isfile(text_file):
            with open(text_file, 'r') as text_fh:
                text_lines = text_fh.read().splitlines(False)
            if not strip_trail:
                return text_lines
            else:
                return [l.strip() for l in text_lines]
        else:
            return []
            
    def dump(self, text_file, **options):
        # self.update(text_file, force = True)
        with open(text_file, 'w+') as dump_fd:
            dump_fd.write('\n'.join(self.store[text_file]['lines']))
        dump_time = int(time())
        self.store[text_file]['create'] = dump_time

    def delete(self, text_file):
        if text_file in self.store.keys():
            return self.store.pop(text_file)['lines']
        else:
            return []
    
    def close(self):
        for text_file in self.store.keys():
            #print(text_file)
            if self.debug:
                print ('Close: "%s"' % text_file)
            if len(self.store[text_file]['lines']) > 0:
                self.dump(text_file)
            else:
                pass

    def discard(self):
        pass
