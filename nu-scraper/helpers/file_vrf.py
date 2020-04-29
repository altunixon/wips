#!/usr/bin/env python
# -*- coding: utf-8 -*- 


import os, sys, time
from PIL        import Image
from zipfile    import ZipFile
from rarfile    import RarFile
from lzma       import LZMAFile
from helpers.misc import humanize_bytes, telltime, print_log, input_with_timeout
import filetype

#from wand.image import Image as WandImage

def match_size(file_path, compare_size, is_file=False):
    #print(file_path, compare_size, is_file)
    if is_file or os.path.isfile(file_path):
        file_size = os.path.getsize(file_path)
        if compare_size is None:
            print_log('warn', 'SIZE: Its Futile to compare anything with None, return True')
            return True
        else:
            if not str(compare_size).isdigit():
                print_log('warn', 'SIZE: "%s" Could not be compared, return True', compare_size)
                return True
            else:
                if int(file_size) == int(compare_size):
                    return True
                else:
                    return False
    else:
        return False

class FileVerifier():
    def __init__(self, path, **kargs):
        self.file_path = path
        self.file_path_base = os.path.dirname(path)
        self.remote_size = int(kargs.pop('remote', 0))
        self.human_size = humanize_bytes(self.remote_size)
        self.file_name  = os.path.basename(path)
        # self.file_noext = os.path.splitext(self.file_name)[0]
        # self.ignore_ext = kargs.pop('ignore', 'part')
        self.file_noext, raw_ext = os.path.splitext(self.file_name)
        self.file_ext = raw_ext.strip('.').lower() if len(raw_ext) > 0 else None
        self.type_arcs = set(['zip','rar'])
        self.type_imgs = set(['png','jpg','jpeg','gif','bmp','tiff','psd'])
        self.mime_types = {
            'image/gif'         : 'gif', 
            'image/jpeg'        : 'jpg', 
            'image/png'         : 'png', 
            'image/tiff'        : 'tiff', 
            'image/vnd.wap.wbmp': 'wbmp', 
            'image/x-icon'      : 'ico', 
            'image/x-jng'       : 'jng', 
            'image/x-ms-bmp'    : 'bmp', 
            'image/svg+xml'     : 'svg', 
            'image/webp'        : 'webp', 
            'application/zip'               : 'zip', 
            'application/x-rar-compressed'  : 'rar', 
            'application/x-7z-compressed'   : '7z'
        }
        self.magic_type = None
        self.input_timeout = kargs.pop('shtimeout', True)
        self.verbose = kargs.pop('verbose', True)
        self.debug = kargs.pop('debug', False)
        self._brint = print_log \
            if self.verbose or self.debug \
            else lambda *x: None

    def magic_file_identifier(self, **kargs):
        return_mime = kargs.pop('mime', False)
        file_kind   = filetype.guess(self.file_path)
        if file_kind is not None:
            if return_mime:
                return file_kind.mime
            else:
                return file_kind.extension.strip('.')
        else:
            return None

    def real_name(self):
        file_ext = self.magic_file_identifier()
        if '.%s' % file_ext in self.file_noext:
            true_file = '{file}.{ext}'.format(
                file = '-'.join(self.file_noext.split('.%s' % file_ext)), 
                ext  = file_ext
            )
        else:
            true_file = '{file}.{ext}'.format(
                file = self.file_noext, 
                ext  = file_ext
            )
        true_path = os.path.join(self.file_path_base, true_file)
        if self.file_path != true_path:
            os.rename(self.file_path, true_path)
        else:
            pass
        return True

    def file_delete(self, **options):
        file_type = options.pop('type', None)
        del_mode  = options.pop('mode', 'rm')
        def del_or_move(del_mode):
            if del_mode == 'rm':
                os.remove(self.file_path)
                #return 'deleted'
            else:
                broken_file = os.path.join(
                    self.file_path_base, 
                    '_broken-{name}.{ext}.dat'.format(
                        name = self.file_noext,
                        ext  = self.file_ext
                    )
                )
                os.rename(self.file_path, broken_file)
                #return 'renamed'
        # if self.verbose:
        if self.input_timeout:
            input_chosen = input_with_timeout('Remove "Corrupted" image? (y/n):> ', 10, 'y').lower()
            print_info = ['Auto (%s)' % input_chosen, del_mode.upper(), self.file_path]
        else:
            input_chosen = input('%s found corrupted delete? ( y/n ) > ' % file_type).lower()
            print_info = ['Manual (%s)' % input_chosen, del_mode.upper(), self.file_path]
        if input_chosen == 'y':
            del_or_move(del_mode)
            self._brint('error', 'VRF_X [{type:#^4s}] - %s, %s: "%s"'.format(type=file_type), *print_info)
            file_deleted = True
        else:
            del_or_move('mv')
            self._brint('error', 'VRF_X [{type:#^4s}] - %s, %s: "%s"'.format(type=file_type), *print_info)
            file_deleted = False
        # else:
        #     del_or_move(del_mode)
        #     file_deleted = True
        return file_deleted

    def size_verify(self, size_remote):
        if size_remote > 0:
            size_local = int(os.path.getsize(self.file_path))
            if size_local >= size_remote:
                match_size = True
            else:
                match_size = False
        else:
            match_size = False
        if match_size:
            self._brint ('ok', 'VRF_O [SIZE] - File: "%s", Size: [%s/%s] %s, Return: True', self.file_path, size_remote, size_local, self.human_size)
        else:
            self._brint ('err', 'VRF_O [SIZE] - File: "%s", Size: [%s/%s] %s, Return: False', self.file_path, size_remote, size_local, self.human_size)
        return match_size

    def image_verify(self, **options):
        auto_delete = options.pop('delete', False)
        mode_delete = options.pop('mode', 'rm')
        check_size  = int(options.pop('size', 0))
        check_type  = options.pop('type', None)
        if check_type is not None:
            img_type = check_type
        else:
            img_type = self.magic_file_identifier()
            self._brint ('debug', 'VRF_I [MAGI] - File: "%s", Type: [%s/%s] %s, Return: False', self.file_path, img_type, check_type)
            # time.sleep(31)
        # print ('PRE READ OPERATION')
        # # time.sleep(31)
        if img_type.strip('.') in self.type_imgs:
            try:
                # generates alot of access operation
                with Image.open(self.file_path) as img_file:
                    #img_file = Image.open(img_file)
                    #img_file = Image.open(self.file_path)
                    img_format = img_file.format.lower()
                    img_file.load()
                    #img_file.close()
                if self.verbose or self.debug:
                    self._brint('info', 'VRF_I [%s] - PATH: "%s", Size: %s, Status: Success', 
                        '{:#^4.4s}'.format(img_format.upper()), self.file_path, self.human_size)
                    # # time.sleep(31)
                else:
                    pass
                file_sanity = True
            except Exception as excp:
                #img_file.close()
                if str(excp) == '__exit__':
                    self._brint('warn', 'VRF_I [EXIT], IMG: "%s", Size: %s, Status: __exit__', self.file_path, self.human_size)
                    file_sanity = True
                else:
                    self._brint('err', 'VRF_I [FAIL] - IMG: "%s", Size: %s, Status: %s', self.file_path, self.human_size, excp)
                    if self.debug:
                        raise excp
                    else:
                        file_sanity = False
        else:
            file_sanity = False
        if not file_sanity and check_size > 0:
            file_sanity = True if self.size_verify(check_size) else False
        else:
            pass
        if not file_sanity:
            if auto_delete:
                self.file_delete(type = img_type, mode = mode_delete)
            else:
                pass
        else:
            pass
        return file_sanity

    def archive_verify(self, **options):
        auto_delete = options.pop('delete', False)
        mode_delete = options.pop('mode', 'rm')
        check_size  = int(options.pop('size', 0))
        check_type  = options.pop('type', None)
        if check_type is not None:
            arc_type = check_type.strip('.')
        else:
            self.magic_file_identifier()
        if arc_type == 'zip':
            try:
                with ZipFile(self.file_path) as zip_archive:
                    zip_stats = zip_archive.testzip()
                    self._brint('ok', 'VRF_A [ZIP#] - File: "%s", Size: %s, Status: %s', self.file_path, self.human_size, zip_stats)
                file_sanity = True
            except Exception as excp:
                self._brint('err', 'VRF_A [ZIP#] - File: "%s", Size: %s, Status: Failed', self.file_path, self.human_size)
                if self.debug:
                    raise excp
                else:
                    file_sanity = False
        elif arc_type == 'rar':
            try:
                with RarFile(self.file_path) as rar_archive:
                    rar_archive.testrar()
                    self._brint('ok', 'VRF_A [RAR#] - File: "%s", Size: %s, Status: %s', self.file_path, self.human_size, excp)
                file_sanity = True
            except Exception as excp:
                self._brint('err', 'VRF_A [RAR#] - File: "%s", Size: %s, Status: Failed', self.file_path, self.human_size)
                if self.debug:
                    raise excp
                else:
                    file_sanity = False
        else:
            file_sanity = False
        if not file_sanity and check_size > 0:
            file_sanity = True if self.size_verify(check_size) else False
        else:
            pass
        if not file_sanity:
            if auto_delete:
                self.file_delete(type = arc_type, mode = mode_delete)
            else:
                pass
        else:
            pass
        return file_sanity

    def verify(self, **vrf_opts):
        auto_delete = vrf_opts.pop('delete', False)
        mode_delete = vrf_opts.pop('mode', 'rm')
        mode_lazy = vrf_opts.pop('lazy', False)
        #print(auto_delete, vrf_opts)
        if os.path.isfile(self.file_path):
            # no access
            # if self.debug:
            #     self._brint('dbug',
            #         'Path: "{file}", Ext[{x}], TypeArch[{y}]'.format(file=self.file_path, x=self.file_ext, # y=self.file_noext)
            #     )
            #     # time.sleep(31)
            # else:
            #     pass
            # print ('\n', self.file_ext, self.file_noext); exit ()
            if self.file_ext is not None:
                file_type = self.file_ext
                cond_arc = any(
                    self.file_ext == arc_ext \
                    for arc_ext in self.type_arcs
                )
                cond_img = any(
                    self.file_ext == img_ext \
                    for img_ext in self.type_imgs
                )
            else:
                file_type   = self.magic_file_identifier()
                cond_arc    = True if file_type in self.type_arcs else False
                cond_img    = True if file_type in self.type_imgs else False

            if self.debug:
                self._brint('debug',
                    'Path: "{file}", TypeImg[{ci}], TypeArch[{ca}]'.format(
                        file=self.file_path, ci=cond_img, ca=cond_arc,)
                )
                # time.sleep(31)
            else:
                pass

            if cond_img: 
                verify_result = {
                    'verified': self.image_verify(
                        delete=auto_delete, 
                        mode=mode_delete, 
                        type=file_type, 
                        debug=self.verbose
                    ), 
                    'type': 'img'}
            elif cond_arc: 
                verify_result = {
                    'verified': self.archive_verify(
                        delete=auto_delete, 
                        mode=mode_delete, 
                        type=file_type, 
                        debug=self.verbose
                    ), 
                    'type': 'arc'}
            else:
                self._brint('warn', 'VRF_# [SKIP] - Miscellaneous: "%s", Size: %s, Type: %s', self.file_path, self.human_size, self.file_ext)
                verify_result = {'verified':  True, 'type': 'misc'}
                # if self.file_path.lower().endswith('.torrent'): 
                #     self._brint('warn', 'VRF_# [SKIP] - Torrent: "%s", Size: %s, Type: %s', self.file_path, self.human_size, self.file_ext)
                #     verify_result = {'verified':  True, 'type': 'torrent'}
                # else:
                #     if file_type is not None:
                #         if self.size_verify(self.remote_size):
                #             misc_stats = 'Size match'
                #             check_misc = True
                #         else:
                #             if auto_delete:
                #                 misc_stats = 'Size Mismatch (Deleted)'
                #                 check_misc = False
                #             else:
                #                 misc_stats = 'Size Mismatch (Keep)'
                #                 check_misc = True
                #         self._brint(
                #             'warn', 
                #             'VRF_O [NULL] - Unsupported: [%s], File: "%s", Size: %s, Status: %s {misc}'.format(
                #                 misc=misc_stats), 
                #             file_type, 
                #             self.file_path, 
                #             self.human_size, 
                #             self.remote_size
                #         )
                #         verify_result = {'verified': check_misc, 'type': file_type}
                #     else:
                #         self._brint('warn', 'VRF_O [ETC_] - File: "%s", Size: %s, Type: %s, Status: True (Default)', self.file_path, self.human_size, file_type)
                #         verify_result = {'verified': True, 'type': None}
        else:# 
            self._brint('error', 'VRF_X [PATH] - File: "%s" does not exist!', self.file_path)
            verify_result = {'verified': False, 'type': None}
        return verify_result
