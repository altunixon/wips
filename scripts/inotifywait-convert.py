#!/usr/bin/env python3

# inotifywait -m -r -o /tmp/watch.txt -e move --format '%:e:%w%f' --daemon "$1"
import re, argparse
from argparse import RawTextHelpFormatter
from os import path, getcwd

def lst2chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]
        
def match_percentage(string_1, string_2): # JANKY AF
    set_1 = set([x for x in string_1])
    set_2 = set([y for y in string_1])
    if len(string_2) > len(string_1):
        needles, haystack = set_1, set_2
    else:
        needles, haystack = set_2, set_1
    m = 0
    for n in needles:
        if n in haystack:
            m += 1
    return (m * 100) / len(haystack)
        
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
        default=os.path.join(os.getcwd(), 'downloads'), 
        help='Output file')
    args_parser.add_argument(
        '--all', dest='event_all', action='store_true', 
        help='Match ALL events, not just ISDIR (Currently ONLY support ISDIR)')
    args_parser.set_defaults(debug=False)
    # Parse Console Args
    console_args = args_parser.parse_args()
    action_lines = []
    path_before = path_after = None
    if path.isfile(console_args.watch_file):
        watched_lines = (line for line in open(console_args.watch_file, 'rt'))
        for wline in watched_lines:
            if re.search('ISDIR', wline, re.IGNORECASE):
                watched_event, watched_type, watched_path = wline.split(':', 2)
                if watched_event == 'MOVED_FROM' and action_before is None:
                    path_before = watched_path
                elif watched_event == 'MOVED_TO' and action_after is None:
                    path_after = watched_path
                else:
                    print ('[SKIP_] Conflict Action: [%s] MOVED_FROM[%s] MOVED_TO[%s]' % (wline, path_before, path_after))
                    path_before = path_after = None
                
                if path_before is not None and path_after is not None:
                    name_before = path.dirname(path_before)
                    name_after = path.dirname(path_after)
                    name_match = match_percentage(name_after, name_before)
                    action_bash = '[ test -d "{before}" ] && mv --no-clobber -v "{before}" "{after}"'.format(before=path_before, after=path_after)
                    if name_match >= 80:
                        print ('[VALID] Matched %s%%: MOVED_FROM[%s] MOVED_TO[%s]' % (name_match, name_before, name_after))
                        action_lines.append(action_bash)
                    else:
                        print ('[SKIP_] Conflict? Object Name: MOVED_FROM[%s] MOVED_TO[%s]' % (path_before, path_after))
                        action_lines.append('# %s' % action_bash)
                    path_before = path_after = None
                else:
                    pass
            else:
                print ('[SKIP_] NOTDIR Event: %s' % wline)
    else:
        pass
    if console_args.act_file is not None and not path.isfile(console_args.act_file):
        with open(console_args.act_file, 'wt+') as af:
            af.writelines("%s\n" % act_cmd for act_cmd in action_lines)
else:
    pass
