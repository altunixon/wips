#!/usr/bin/env python
# -*- coding: utf-8 -*-

# https://stackoverflow.com/questions/3431825/generating-an-md5-checksum-of-a-file

import os, hashlib, zlib, time

def file_hash(file_path, **hash_options):
    hash_type   = hash_options.pop('type', 'crc')
    assert (os.path.isfile(file_path)), \
        'HASH MD5 - File "%s" does not exists.' % file_path
    if hash_type == 'md5':
        return file_md5(file_path, **hash_options)
    elif hash_type == 'crc' or hash_type == 'crc32':
        return file_crc32(file_path, **hash_options)
    else:
        print('Unknown Hash Type: "%s", Default to CRC32' % hash_type)
        return file_crc32(file_path, **hash_options)

def file_md5(file_path, **hash_options):
    hash_timeit = hash_options.pop('timeit', False)
    hash_chunk  = int(hash_options.pop('chunk', 4096))
    hash_digest = hash_options.pop('digest', 'md5')
    time_sec = None
    if hash_timeit: time_sec = time.time()
    hash_md5    = hashlib.md5()
    with open(file_path, "rb") as fab:
        for chunk in iter(lambda: fab.read(hash_chunk), b""):
            hash_md5.update(chunk)
    file_chksum = hash_md5.hexdigest() \
        if hash_digest != 'raw' \
        else hash_md5.digest()
    if hash_timeit:
        time_sec = time.time() - time_sec
        print('%s - "%s" (%s Seconds)' % (file_chksum, file_path, time_sec))
    else:
        pass
    return file_chksum

def file_crc32(file_path, **hash_options):
    hash_timeit = hash_options.pop('timeit', False)
    hash_chunk = int(hash_options.pop('chunk', 4096))
    file_chsum = 0
    time_sec = None
    if hash_timeit: time_sec = time.time()
    with open(file_path, "rb") as fab:
        for chunk in iter(lambda: fab.read(hash_chunk), b""):
            file_chsum = zlib.crc32(chunk, file_chsum)
    if hash_timeit:
        time_sec = time.time() - time_sec
        print('%s - %s (%s seconds)' % (hash_md5, file_path, time_sec))
    else:
        pass
    if file_chsum is not None:
        return "%X" % (file_chsum & 0xFFFFFFFF)
    else:
        return file_chsum

# http://notepad2.blogspot.com/2014/09/python-generates-crc32-and-adler32.html
#import zlib
#import sys
#import urllib2
#
#def __zlib_csum(url, func):
#    if isinstance(url, basestring if sys.version_info[0] < 3 else str):
#        url = urllib2.Request(url)
#    f = urllib2.urlopen(url)
#    csum = None
#    try:
#        chunk = f.read(1024)
#        if len(chunk)>0:
#            csum = func(chunk)
#            while True:
#                chunk = f.read(1024)
#                if len(chunk)>0:
#                    csum = func(chunk, csum)
#                else:
#                    break
#    finally:
#        f.close()
#    if csum is not None:
#        csum = csum & 0xffffffff
#    return csum
#    
#
#def crc32(url):
#    return __zlib_csum(url, zlib.crc32)
#
#def adler32(url):
#    return __zlib_csum(url, zlib.adler32)
#
#if __name__ == '__main__':
#    print(hex(crc32('file:/tmp/111.zip')))
#    print(hex(adler32('file:/tmp/111.zip')))