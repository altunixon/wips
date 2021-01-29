#!/usr/bin/env python3

from classes import config-file # PLACEHOLDER
# https://skpy.t.allofti.me/usage.html
from skpy import Skype
# Since password will be read from config file or cmdline arg
# from getpass import getpass

my_skuser = ""
my_skpass = ""
my_skype = Skype()
my_skype.conn
#> SkypeConnection(connected=False)
my_skype.conn.setUserPwd(my_skuser, my_skpass)
my_skype.getSkypeToken()
my_skype.conn
#> SkypeConnection(userId='fred.2', connected=True, guest=False)
for my_furendo in my_skype.contacts:
    my_x = my_furendo.id
    print (my_x)
    my_furendo[my_x]

my_room = my_skype.contacts[my_x].chat.id
my_chat = my_skype.chats[my_room]
my_chat.getMsgs()
my_chat.sendMsg("Hello.")
my_chat.sendMsg(SkypeMsg.bold("Bold!"), rich=True)

"""
>>> from skpy import SkypeEventLoop
>>> class MySkype(SkypeEventLoop):
...     def onEvent(self, event):
...         print(repr(event))
...
>>> MySkype(tokenFile=".tokens-fred.2", autoAck=True)
MySkype(userId='fred.2')
>>> sk = MySkype(tokenFile=".tokens-fred.2", autoAck=True)
>>> sk.loop()
SkypePresenceEvent(id=1000, ..., userId='joe.4', online=True)
SkypeEndpointEvent(id=1001, ..., userId='joe.4')
SkypePresenceEvent(id=1002, ..., userId='anna.7', online=True)
SkypeEndpointEvent(id=1003, ..., userId='anna.7')
SkypeEndpointEvent(id=1004, ..., userId='anna.7')
...
"""
