#!/usr/bin/env python
# -*- coding: utf-8 -*-

import  os, sys, time
import  logging
import  logging.handlers
from    logging.handlers import SysLogHandler
from    socket import getfqdn, gethostname
from    datetime import datetime

class log_printer():
    def __init__(self, log_provider=None, **options):
        log_json = options.pop('json', None)
        log_name = options.pop('name', None)
        self.debug = options.pop('debug', False)
        self.log_timeformat = options.pop('format', '%Y-%m-%d %H:%M:%S %z')
        if sys.platform.startswith('win'):
            self.log_uid    = os.environ.get('USERNAME')
            self.color      = False
        else:
            self.log_uid    = os.getlogin() #os.getuid()
            self.color      = options.pop('color', False)
        self.tee            = options.pop('tee', True)
        self.log_host       = gethostname() # getfqdn()
        self.log_name       = '%s_%s' % (log_name if log_name is not None else __file__, time.strftime('%Y-%m-%d'))
        #self.log_ln         = 0
        if log_provider is None:
            self.log_facility   = None
            self.log_container  = None
        else:
            try:
                if log_provider.startswith('file:'):
                    self.log_facility   = 'f'
                    self.log_container  = log_provider.split(':',1)[1].rsplit('.',1) if \
                        len(log_provider.rsplit('.',1)) > 0 else \
                        [log_provider.split(':',1)[1], 'log']
                elif log_provider.startswith('rsyslog:'):
                    # rsyslog:exhg:%(name)s[%(process)d]: %(levelname)s: %(message)s
                    self.log_facility   = 's'
                    rsys_name, rsys_format = log_provider.split(':',1)[1].split(':',1)
                    self.log_container     = logging.getLogger(rsys_name)
                    #self.log_container.setLevel(logging.INFO)
                    syslog_handler = SysLogHandler(address='/dev/log')
                    syslog_handler.setFormatter(logging.Formatter(rsys_format))
                    self.log_container.addHandler(syslog_handler)
                elif log_provider.startswith('elastic:'):
                    try:
                        from elasticsearch import Elasticsearch
                        self.log_facility   = 'e'
                        elastic_connect     = {'h':None, 'port':9200, 'u':None, 'p':None, 'name':None}
                        for s in log_provider.split(':',1)[1].split(','):
                            k, h                = s.split('=',1)
                            elastic_connect[k]  = h
                        self.log_name = '%s_%s' % (elastic_connect['name'], time.strftime('%Y-%m-%d')) if \
                                        elastic_connect['name'] is not None else \
                                        self.log_name
                        if  elastic_connect['h'] is not None:
                            self.log_container  = Elasticsearch(
                                elastic_connect['h'].split('|'),
                                port=int(elastic_connect['port']),
                                sniff_on_start=True,
                                sniff_on_connection_fail=True,
                                sniffer_timeout=90, 
                                max_retries=3
                                )
                            if self.log_container.ping():
                                if not self.log_container.indices.exists(self.log_name):
                                    elastic_body = { 
                                        "aliases": { }, 
                                        "mappings": { 
                                            "python": { 
                                                "properties": { }
                                                } 
                                            }, 
                                        "settings": { 
                                            "index": { 
                                                "number_of_shards": "1", 
                                                "number_of_replicas": "0", 
                                                "provided_name": self.log_name 
                                                } 
                                            } 
                                        }
                                    if log_json is not None and \
                                    isinstance(log_json, set):
                                        elastic_body["properties"] = self.elastic_format(log_json)
                                    else:
                                        elastic_body["properties"] = { 
                                            "@timestamp": {
                                                "type": "date"
                                                }, 
                                            "message": { 
                                                "type": "text", 
                                                "fields": { 
                                                    "keyword": { 
                                                        "type": "keyword", 
                                                        "ignore_above": 256 
                                                        } 
                                                    } 
                                                }, 
                                            "level": { 
                                                "type": "text", 
                                                "fields": { 
                                                    "keyword": { 
                                                        "type": "keyword", 
                                                        "ignore_above": 256 
                                                        } 
                                                    } 
                                                }
                                            }
                                    self.log_container.indices.create(
                                        self.log_name, 
                                        ignore=400, 
                                        body=elastic_body)
                            else:
                                self.log_container  = None
                        else:
                            self.log_container  = None
                    except Exception as excp:
                        if self.debug:
                            raise Exception(excp)
                        else:
                            print (excp)
                            self.log_container  = None
                elif log_provider.startswith('xmpp:'):
                    self.log_facility   = 'x'
                    jabber_connect      = {
                        'h': None, 'port': 5222, 
                        'u': None, 'p': None
                    }
                else:
                    self.log_facility = None
                    self.log_container = None
            except Exception as excp:
                if self.debug:
                    raise Exception(excp)
                else:
                    print (
                        '%s uid=%s %s: ERROR: %s: %s' % (
                            self.log_host, 
                            self.log_uid,
                            time.strftime(self.log_timeformat), 
                            log_provider, 
                            str(excp)
                        )
                    )
                    self.log_container = None
                
    def print_stdout(self, log_level, log_text):
        if self.color:
            if log_level == 'info':
                message_type= '\033[1;34mINFO\033[0m' # Blue
            elif log_level == 'ok' or log_level == 'success':
                message_type= '\033[1;32m_OK_\033[0m' # Green
            elif log_level == 'warn' or log_level == 'warning':
                message_type= '\033[1;33mWARN\033[0m' # Yellow
            elif log_level == 'error' or log_level == 'err':
                message_type= '\033[1;4;31mERR_\033[0m' # Red
            elif log_level == 'debug' or log_level == 'dbg':
                message_type = '\033[1;36mDBUG\033[0m' # Cyan
            else:
                message_type = '\033[1;35m%s\033[0m' % '{:_^4.4}'.format(
                    log_level.upper()) # Purple
        else:
            message_type = '{type:_^4.4}'.format(log_level.upper())
        print (
            '{time} [{type:_^4.4}]: {message}'.format(
                time = time.strftime(self.log_timeformat),
                type = message_type, 
                message = log_text
            )
        )

    def elastic_format(self, elastic_set):
        elastic_format_dict = { "@timestamp": { "type": "date" }, }
        for k in elastic_set:
            elastic_format_dict[k] = {
                "type": "text", 
                "fields": { 
                    "keyword": { 
                        "type": "keyword", 
                        "ignore_above": 256 
                        } 
                    } 
                }
        return elastic_format_dict


    def write(self, log_level, log_format, *log_inserts, **options):
        if len(log_inserts) == 0:
            log_message = log_format
        else:
            log_message = ', '.join([str(s) for s in log_inserts]) \
                if log_format is None \
                else log_format % log_inserts
        
        if self.log_container is None:
            self.print_stdout(log_level, log_message)
        else:
            if self.log_facility == 's':
                #log_line = log_message
                try:
                    if log_level == 'ok' or log_level == 'info':
                        self.log_container.setLevel(logging.INFO)
                        self.log_container.info(log_message)
                    elif log_level == 'warn' or log_level == 'warning':
                        self.log_container.setLevel(logging.WARNING)
                        self.log_container.warning(log_message)
                    elif log_level == 'error' or log_level == 'err':
                        self.log_container.setLevel(logging.ERROR)
                        self.log_container.error(log_message)
                    else:
                        self.log_container.setLevel(logging.DEBUG)
                        self.log_container.debug(log_message)
                except:
                    pass
                if self.tee:
                    self.print_stdout(log_level, log_message)
                else:
                    pass
            elif self.log_facility == 'e':
                #self.log_ln += 1
                log_json = {
                    '@timestamp': datetime.now().isoformat(), 
                    'level'     : log_level, 
                    'message'   : log_message}
                try:
                    self.log_container.index(
                        index=self.log_name, 
                        doc_type='python',
                        body=log_json
                    )
                except:
                    pass
                if self.tee:
                    self.print_stdout(log_level, log_message)
                else:
                    pass
            elif self.log_facility == 'f':
                log_line = '%s uid=%s %s: %s: %s' % \
                    (self.log_host, 
                    self.log_uid,
                    time.strftime(self.log_timeformat),
                    log_level.upper(), 
                    log_message)
                log_rotate  = '%s_%s.%s' % (
                    self.log_container[0], 
                    time.strftime('%Y-%m-%d'), 
                    self.log_container[1]
                )
                with open(log_rotate, 'a+') as log_file:
                    log_file.write(log_line)
                if self.tee:
                    self.print_stdout(log_level, log_message)
                else:
                    pass
            else:
                self.print_stdout(log_level, log_message)
        #return log_line