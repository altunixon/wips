#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ntplib
from time import time, ctime, mktime
from datetime import datetime


def trial_time_check(trial_time, ntp_server=None, ntp_version=3):
    trial_end_date = datetime.strptime(trial_time, "%Y-%m-%d")
    trial_end_epoch= mktime(trial_end_date.timetuple())
    ntp_client = ntplib.NTPClient()
    ntp_response = ntp_client.request(ntp_server, version=ntp_version) if \
                    ntp_server is not None else \
                    ntp_client.request('time1.google.com', version=3)
    current_time_epoch = ntp_response.tx_time
    if current_time_epoch >= trial_end_epoch:
        print(('Trial period has ended (valid until %s), please contact provider for more information.' % trial_time))
        exit()
    else:
        print((type(current_time_epoch), type(trial_end_epoch)))
