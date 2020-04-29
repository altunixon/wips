#!/usr/bin/env python
# -*- coding: utf-8 -*-

from shutil         import move
from natsort        import natsorted, ns
from os             import path, walk, sep, makedirs, rename, listdir, rmdir
from helpers.misc   import print_log, input_with_timeout, input_with_timeout_sane, input_with_timeout_windows

dir_illegal_ends = [' ','.','\\', ' \\', sep, ' %s' % sep, '.%s' % sep]
dir_illegal_starts = [' ','.','\'', '"',':', '.%s' % sep, '..%s' % sep]
        
def MkDirP(path_dir, **options):
    #dir_tree = StrPathSane(dir_path)
    path_old = options.pop('old', None)
    path_mkd = options.pop('mkd', True)
    strict_mode = options.pop('meltdown', False)
    try:
        if path_old is None:
            if not path.exists(path_dir):
                makedirs(path_dir)
        else:
            if not path.exists(path_old):
                if path_mkd:
                    makedirs(path_dir)
                else:
                    pass
            else:
                rename(path_old, path_dir)
        return True
    except Exception as excp:
        if not strict_mode:
            return False
        else:
            print ('Module: mkdir -p "%s" Error:\n' % path_dir)
            raise excp
    
def Move2Level(dir_root, cwd_path, **kargs):
    check_inandistype = lambda w, x, y, z: w[x] \
        if x in w.keys() \
        and isinstance(w[x], y) \
        else z
    move_level = check_inandistype(kargs, 'level', int, 0)
    move_safety= check_inandistype(kargs, 'safety', bool, True)
    cwd_files  = check_inandistype(kargs, 'files', list, listdir(cwd_path))
    cwd_tree = [p for p in cwd_path.replace(
        dir_root.rstrip(sep), '').rstrip(sep).split(sep) \
        if len(p.strip()) > 0]
    #ddepths = cpath.rstrip(dirsep).count(dirsep) - droot.rstrip(dirsep).count(dirsep)
    if move_level > 0:
        if len(cwd_tree) > move_level:
            move2_dir = path.join(dir_root, cwd_tree[move_level-1])
        else:
            move2_dir = cwd_path.rstrip(sep)
    else:
        move2_dir = dir_root.rstrip(sep)
    #print(mroot)
    if move2_dir == cwd_path.rstrip(sep):
        print_log('warn', 'MOVE_FILE - SKIP - CWD="%s"=ROOT', cwd_path)
    else:
        for afile in cwd_files:
            mv_from = path.join(cwd_path, afile)
            mv_to = path.join(move2_dir, afile)
            if not path.isfile(mv_to) or not move_safety:
                move(mv_from, mv_to)
            else:
                print_log('warn', 'MOVE_FILE - SKIP - File exists at "%s".', mv_to)
                if move_safety:
                    print_log('warn', 'MOVE_FILE - HALT - For safety reasons, stop all moving operations on "%s".', cwd_path)
                    return
                else:
                    pass
                
def RemoveEmptyFolders(dir_path, **kargs):
    dowait = kargs['wait'] if 'wait' in list(kargs.keys()) \
                           and isinstance(kargs['wait'], bool) \
                           else False
    assert path.isdir(dir_path)
    # remove empty subfolders
    files = listdir(dir_path)
    if len(files) > 0:
        for f in files:
            fullpath = path.join(dir_path, f)
            if path.isdir(fullpath):
                RemoveEmptyFolders(fullpath)
    # if folder empty, delete it
    files = listdir(dir_path)
    if len(files) == 0:
        print_log('warn', 'REMOVE_DIR - "%s".', dir_path)
        if not dowait:
            rmdir(dir_path)
        else:
            if input_with_timeout('Remove Empty Directory "%s"? (y/n):> ' % dir_path, 10, 'y').lower() == 'y':
                rmdir(dir_path)
    
def DictDirFile(dir_path, **kargs):
    accept_exts = kargs['ext'] if 'ext' in list(kargs.keys()) and isinstance(kargs['ext'], tuple) else ()
    lsempty_dir = kargs['lsempty'] if 'lsempty' in list(kargs.keys()) and isinstance(kargs['lsempty'], bool) else False
    exclude_strs= kargs['exclude'] if 'exclude' in list(kargs.keys()) and isinstance(kargs['exclude'], tuple) else ()
    depth_level = kargs['level'] if 'level' in list(kargs.keys()) and isinstance(kargs['level'], int) else 999
    root_level = dir_path.rstrip(sep).count(sep)
    return_dict = {}
    sorted_keys = []
    assert path.isdir(dir_path)
    for dirroot, dirbranch, dirfiles in walk(dir_path):
        if dirroot.count(sep) - root_level <= depth_level:
            acceptd_files = set([])
            sorted_files  = []
            for a_file in dirfiles:
                cond_mext = any(a_file.lower().endswith(ext) for ext in accept_exts) \
                            if len(accept_exts) > 0 else True
                cond_noex = all(useless not in a_file.lower() for useless in exclude_strs) \
                            if len(exclude_strs) > 0 else True
                if cond_mext and cond_noex:
                    if a_file not in acceptd_files:
                        acceptd_files.add(a_file)
                        sorted_files.append(a_file)
            
            #return_dict[path.normpath(dirroot)] = tuple(sorted_files)
            if len(sorted_files) > 0 or lsempty_dir:
                return_dict[path.normpath(dirroot)] = natsorted(sorted_files, alg=ns.IGNORECASE)
                sorted_keys.append(path.normpath(dirroot))
            else:
                pass
        else:
            pass
    #yield dirroot, dirbranch, dirfiles
    # read yield @https://stackoverflow.com/questions/231767/what-does-the-yield-keyword-do
    return {'dict': return_dict, 'sorted': sorted_keys}
    #return return_dict
    
def lsdir_iter(dir_path):
    directory_tree = {}
    def lsd(cwd_path):
        content_all = listdir(cwd_path)
        #print (content_all)
        content_dir = []
        content_file= []
        for p in content_all:
            content_path = path.join(cwd_path,  p)
            if path.isdir(content_path):
                content_dir.append(content_path)
            elif path.isfile(content_path):
                content_file.append(content_path)
            else:
                pass
        #print (content_dir, '\n', content_file)
        directory_tree[cwd_path] = content_file
        if len(content_dir) > 0:
            for child_dir in content_dir:
                lsd(child_dir)
        else:
            pass
    lsd(dir_path)
    return directory_tree
    
#def StrPathSane(dir_path, full_check=True):
    #s_platform = sys.platform
#    if sep in dir_path:
#        sanitized_path = path.normpath(
#            dir_path.replace('/', sep).strip() \
#                if sep not in dir_path \
#                else dir_path)
#    else:
#        sanitized_path = dir_path.strip()
#    if full_check:
#        folders = []
#        for folder in sanitized_path.split(sep):
#            if any(folder.startswith(illegal_start) \
#            for illegal_start in dir_illegal_starts):
#                #while any(folder.startswith(illegal_start) for illegal_start in dir_illegal_starts):
#                for illegal_start in dir_illegal_starts:
#                    folder = folder.split(illegal_start, 1)[-1]
#            else:
#                pass
#
#            if any(folder.endswith(illegal_end) \
#            for illegal_end in dir_illegal_ends):
#                #while any(folder.endswith(illegal_end) for illegal_end in dir_illegal_ends):
#                for illegal_end in  dir_illegal_ends:
#                    folder = folder.rsplit(illegal_end, 1)[0]
#            else:
#                pass
#
#            folders.append(folder)
#        sanitized_folders = (sep).join(folders)
#    else:
#        #while any(sanitized_path.endswith(illegal_end) for illegal_end in dir_illegal_ends):
#        for illegal_end in dir_illegal_ends:
#            if sanitized_path.endswith(illegal_end):
#                sanitized_path = sanitized_path.rsplit(illegal_end, 1)[0]
#    sanitized_folders = path.abspath(sanitized_path.strip()) \
#        if sep in dir_path \
#        else sanitized_path.strip()
#    return sanitized_folders
