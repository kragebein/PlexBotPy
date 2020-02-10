#!/usr/bin/python3
''' Trigger handler for PlexbotPy '''

import re
import json
import sys
from bot.main import search
from bot.main import request
from bot.main import test
from types import ModuleType
import bot.pluginloader
from bot.pluginloader import pluginss
import logging
global trigger
trigger = {} # This sets the global triggerlist that can be manipulated.
logging.basicConfig(level=logging.INFO)
data = ''
def blah(data):
    return data


def listplugins(thread=None, ttype=None, name=None, author=None, nickname=None, msg=None):
    data = []
    for i in trigger.keys():
        data.append(i)
    return data

# these are the core plugins for PlexBot. The list will be expanded by the plugins themselves.
trigger = { # Static triggers. 
        '!search': search, 
        '!request': request,
        '!echo': blah,
        '!list': listplugins,
        '!load': bot.pluginloader.loadplugins,
        '!reload': bot.pluginloader.reloadplugins,
        '!unload': bot.pluginloader.unloadplugins 
        }


def check(input, thread=None, ttype=None, name=None, author=None, nickname=None):
    '''check if incoming data is a trigger, will return True (with query data) if true.
    Returns False if data is not a trigger '''
    message = input['delta']['body']       
    query = message.split(' ')[0]
    data = str(message.split(' ', 1)[-1])
    for key, value in trigger.items():
        if re.search(key, query):
            logging.info('{} triggered {}'.format(name, query))
            if query == data:
                if isinstance(value, str):
                    return value()
                return value(thread=thread, ttype=ttype, name=name, author=author, nickname=nickname, msg=input)
            else:
                return value(data, thread=thread, ttype=ttype, name=name, author=author, nickname=nickname, msg=input)
    