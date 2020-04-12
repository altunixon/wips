#!/usr/bin/env python
# -*- coding: utf-8 -*-

from helpers.text_file import text_file
from helpers.misc import telltime
from copy import deepcopy
from collections import namedtuple
from configparser import ConfigParser
import os, sys, json

def config_ini(config_file, config_section=None, **default_dict):
    if config_file is not None \
    and os.path.isfile(config_file):
        try:
            config_ini = ConfigParser()
            config_ini.read(config_file)
            config_asdict = {}
            if config_section is None:
                for k in config_ini.sections():
                    config_asdict[k] = {}
                    for x, y in config_ini[k].items():
                        config_asdict[k][x] = y
            else:
                for k, v in default_dict.items():
                    config_asdict[k] = config_ini[config_section].pop(k, v)
            return config_asdict
        except Exception as excp:
            print (excp)
            return None
    else:
        return default_dict

def config_json(config_file, **configs_dict):
    if config_file is not None \
    and os.path.isfile(config_file):
        try:
            with open(config_file, 'r') as jf:
                configs_read = json.load(jf)
            configs_copy = deepcopy(configs_dict)
            for k, v in configs_copy.items():
                configs_copy[k] = configs_read.pop(k, v)
            return configs_copy
            # configs_ntuple = namedtuple('ConfigsNamed', list(configs_copy.kays()))
            # return configs_ntuple(**configs_copy)
        except Exception as excp:
            print (excp)
            return None
    else:
        return configs_dict

def config_compare(**configs):
    if 'defaults' in list(configs.keys()):
        if 'file' in list(configs.keys()):
            #print configs['file']
            file_configs = text_file(configs['file'])
            if file_configs.check:
                final_configs = {}
                filed_configs = file_configs.read_as_config()
                #print filed_configs
                for aconf_key in list(configs['defaults'].keys()):
                    if aconf_key not in list(filed_configs.keys()): final_configs[aconf_key] = configs['defaults'][aconf_key]
                    else: final_configs[aconf_key] = filed_configs[aconf_key]
            else:
                final_configs = configs['defaults']
        else:
            final_configs = configs['defaults']
    else:
        raise Exception(telltime() + 'ERROR - CONFIG - MISSING DEFAULT CONFIGS - SUPPLIED="%s"' % configs)
    return final_configs

def config_console(config_path=None):
    console_args = sys.argv
    cond_a = config_path is not None
    cond_b = os.path.isfile(config_path) if cond_a else False
    cond_c = (len(console_args) >= 2)
    if cond_a and cond_b and not cond_c:
        print(telltime() + 'INFO - CONFIG - ILLEGAL SUPPLIED CONSOLE ARG / USING DEFAULT - CONSOLE="%s", DEFAULT="%s"' % (console_args, config_path))
        config_file = config_path
    else:
        if cond_c:
            config_file = console_args[-1]
        else:
            config_file = input("Enter Configuration file location: ")
        if len(config_file) == 0 or not os.path.isfile(config_file):
            print(telltime() + 'WARN - CONFIG - SUPPLIED CONFIG AND DEFAULT FILE MISSING - SUPPLIED="%s", DEFAULT="%s"' % (config_file, config_path))
    return config_file


