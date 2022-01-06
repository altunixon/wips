#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys, json
import argparse
from argparse import RawTextHelpFormatter

if __name__ == '__main__':
    script_path = os.path.dirname(os.path.realpath(__file__))
    script_name = os.path.basename(__file__).rsplit('.', 1)[0]
    parser = argparse.ArgumentParser(description='Script Description',
        argument_default=argparse.SUPPRESS, formatter_class=RawTextHelpFormatter)
    parser.add_argument('-i', '--in', dest='file_in', nargs='?', default='manifest.txt',
        help='Manifest file, written in plain text, default=manifest.txt')
    parser.add_argument('-o', '--out', dest='file_out', nargs='?', default='manifest.json',
        help='Output JSON file, default=manifest.json')
    parser.add_argument('--no-clobber', dest='flag_clobber', action='store_false',
        help='Do not overwrite output json file if it already exists')
    parser.set_defaults(flag_clobber=True)
    parser.add_argument('-t', '--test', dest='flag_test', action='store_true',
        help='Test manifest.txt content before convert to json')
    parser.set_defaults(flag_test=False)
    # Compile arguments
    console_args = parser.parse_args()
    assert os.path.isfile(console_args.file_in), f'InputFile: "{console_args.file_in}" NotFound.'
    if not console_args.flag_clobber:
        assert not os.path.isfile(console_args.file_out), \
            f'OutputFile: "{console_args.file_out}" Exists, NoClobber.'



else:
    pass
