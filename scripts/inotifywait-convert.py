#!/usr/bin/env python3

import argparse
from argparse import RawTextHelpFormatter

def lst_chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]
        
if __name__ == "__main__":
    args_parser = argparse.ArgumentParser(
        description='Download URL',
        argument_default=argparse.SUPPRESS, 
        formatter_class=RawTextHelpFormatter)
    args_parser.add_argument(
        dest='urls', nargs='*', default=None,
        help='an URL for the accumulator')
    args_parser.add_argument(
        '-i', '--in-file', dest='file', nargs='?', default=None, 
        help='inotifywait file')
    args_parser.add_argument(
        '-o', '--out-file', dest='saveto', nargs='?', 
        default=os.path.join(os.getcwd(), 'downloads'), 
        help='Output file')
    args_parser.add_argument(
        '--debug', dest='debug', action='store_true', 
        help='Debug mode more verbose, raise on error.')
    args_parser.set_defaults(debug=False)
    # Parse Console Args
    console_args = args_parser.parse_args()
else:
    pass
