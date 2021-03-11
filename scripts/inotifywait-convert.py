#!/usr/bin/env python3

# inotifywait -m -r -o /tmp/watch.txt -e move --format '%:e:%w%f' --daemon "$1"
import re, argparse
from argparse import RawTextHelpFormatter
from os import path, getcwd, sep

def lst2chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def event_splitter(event_line):
    if ':ISDIR:' in event_line:
        return tuple(event_line.split(':', 2))
    else:
        event_act, event_obj = event_line.split(':', 1)
        return tuple(event_act, None, event_obj)

def chunker_inpair(watched_lines):
    for x in range(0, len(watched_lines), 2):
        print (x, watched_lines[x:x+2])
        watch_before, watch_after = watched_lines[x:x+2]
        event_before, type_before, path_before = event_splitter(watch_before)
        event_after, type_after, path_after = event_splitter(watch_after)
        name_before = path.basename(path.normpath(path_before))
        name_after = path.basename(path.normpath(path_after))
        name_match = match_percentage(name_after, name_before)
        action_bash = '[ -d "{before}" ] && mv --no-clobber -v "{before}" "{after}"'.format(before=path_before, after=path_after)
        if name_match >= 60:
            print ('[VALID] Matched %s%%: MOVED_FROM "%s" MOVED_TO "%s"' % (name_match, name_before, name_after))
            yield action_bash
        else:
            print ('[WARN_] Conflict? matched %s%%: MOVED_FROM "%s" MOVED_TO "%s"' % (name_match, name_before, name_after))
            yield ('# %s' % action_bash)

def chunker_inline(watched_lines):
    action_lines = []
    path_before = path_after = action_previous  = None
    for wline in watched_lines:
        watched_event, watched_type, watched_path = event_splitter(wline)
        if watched_event == 'MOVED_FROM' and action_previous is None:
            path_before = watched_path
            action_previous = watched_event
        elif watched_event == 'MOVED_TO' and action_previous == 'MOVED_FROM':
            path_after = watched_path
            action_previous = None
        else:
            print ('[SKIP_] Conflict Action: [%s/%s] MOVED_FROM[%s] MOVED_TO[%s]' % (action_previous, watched_event, path_before, path_after))
            path_before = path_after = action_previous = None
        if path_before is not None and path_after is not None:
            name_before = path.basename(path.normpath(path_before))
            name_after = path.basename(path.normpath(path_after))
            name_match = match_percentage(name_after, name_before)
            action_bash = '[ -d "{before}" ] && mv --no-clobber -v "{before}" "{after}"'.format(before=path_before, after=path_after)
            if name_match >= 70:
                print ('[VALID] Matched %s%%: MOVED_FROM "%s" MOVED_TO "%s"' % (name_match, name_before, name_after))
                action_lines.append(action_bash)
            else:
                print ('[WARN_] Conflict? matched %s%%: MOVED_FROM "%s" MOVED_TO "%s"' % (name_match, path_before, path_after))
                action_lines.append('# %s' % action_bash)
            path_before = path_after = action_previous = None
        else:
            pass
    return action_lines

def match_percentage(string_1, string_2): # JANKY AF
    set_1 = set([x for x in string_1])
    set_2 = set([y for y in string_2])
    if len(string_2) > len(string_1):
        needles, haystack = set_1, set_2
    else:
        needles, haystack = set_2, set_1
    m = 0
    for n in needles:
        if n in haystack:
            m += 1
    if m > 0:
        return int((m * 100) / len(haystack))
    else:
        return 0

if __name__ == "__main__":
    args_parser = argparse.ArgumentParser(
        description='Download URL',
        argument_default=argparse.SUPPRESS,
        formatter_class=RawTextHelpFormatter)
    args_parser.add_argument(
        '-i', '--in-file', dest='watch_file', nargs='?', default=None,
        help='inotifywait file')
    args_parser.add_argument(
        '-o', '--out-file', dest='act_file', nargs='?',
        default=path.join(getcwd(), 'downloads'),
        help='Output file')
    args_parser.add_argument(
        '--all', dest='event_all', action='store_true',
        help='Match ALL events, not just ISDIR (Currently ONLY support ISDIR)')
    args_parser.set_defaults(event_all=False)
    args_parser.add_argument(
        '--pair', dest='match_pair', action='store_true',
        help='Match algorithim, use pairing instead of line by line (less accurate? maybe?)')
    args_parser.set_defaults(match_pair=False)
    args_parser.add_argument(
        '--map', dest='path_map', nargs='?', default=None,
        help='Replace path in inotify file with supplied path, format path_inotify|path_replace')
    # Parse Console Args
    console_args = args_parser.parse_args()
    if path.isfile(console_args.watch_file):
        print (console_args.watch_file)
        with open(console_args.watch_file, 'r') as wf:
            wls = wf.readlines()
        # print (len(wls))
        watched_lines = [line.rstrip('\n') for line in wls if >= 0 and line.find('MOVED_') >= 0]
        if console_args.match_pair:
            action_lines = chunker_inpair(watched_lines)
        else:
            action_lines = chunker_inline(watched_lines)
        if console_args.path_map is not None and '|' in console_args.path_map:
            path_orig, path_swap = console_args.path_map.split('|', 1)
        else:
            path_orig = path_swap = None
        if console_args.act_file is not None:
            with open(console_args.act_file, 'w+') as af:
                if path_swap is None:
                    af.writelines("%s\n" % act_cmd for act_cmd in action_lines)
                else:
                    af.writelines("%s\n" % act_cmd.replace(path_orig.strip(),
                                                           path_swap.strip()) for act_cmd in action_lines)
    else:
        print ('XXX')
        pass
else:
    pass
