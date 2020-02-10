#!/usr/bin/python3
''' Will load plugins in plugins/-dir'''
import os
import sys
import re
import importlib
import logging
import traceback
import inspect
from plexbot import me
from importlib import import_module
from bot.main import attu
path = me + "/plugins/"
global pluginss
pluginss = {} #Keeps track of all loaded plugins.
def loadplugins(data=None, thread=None, ttype=None, name=None, author=None, nickname=None, msg=None):
    req_level = 9
    userlevel = attu(uid=author)
    if userlevel < req_level:
        return('Sorry, you dont have a high enough userlevel, needed: {}, you: {}'.format(req_level, userlevel))

    from bot.trigger import trigger
    if data is None:
        try: # load everything in the plugins folder.
            sys.path.insert(0, path)
            for f in os.listdir(path):
                fname, ext = os.path.splitext(f)
                if ext == '.py' and fname != 'announce':
                    mod = importlib.import_module('.' + fname, package='plugins')
                    pluginss[fname] = mod.Plugin()
                    trigger.update()
                sys.path.pop(0)
            pluginss.pop('__init__') #Dont need __init__ in our registry.
            pluginlist = []
            for i in pluginss.keys():
                pluginlist.append(i)
            return('Plugins loaded: {}'.format(pluginlist))
            del pluginlist
        except Exception as e:
            logging.info('Error while loading all plugins: {}'.format(e))
            return False
    else:
        # load this particular plugin.
        try:
            sys.path.insert(0, path)
            mod = importlib.import_module('.' + data, package='plugins')
            pluginss[data] = mod.Plugin()
            sys.path.pop(0)
            return('Plugin loaded: {}'.format(data))
        except Exception as e:
            logging.info('Error occured while loading single plugin: {}'.format(e))
            return 'Error occured while loading single plugin: {}'.format(e)

def unloadplugins(data=None, thread=None, ttype=None, name=None, author=None, nickname=None, msg=None):
    req_level = 9
    userlevel = attu(uid=author)
    if userlevel < req_level:
        return('Sorry, you dont have a high enough userlevel, needed: {}, you: {}'.format(req_level, userlevel))
    from bot.trigger import trigger
    query = data
    if query in pluginss.keys():
        switcheroo = pluginss[query]
        _this = 'plugins.' + query
        trigger.pop(switcheroo._trigger)
        del sys.modules[_this]  # unregister the plugin from python registry, this will allow for reloading.
        del pluginss[query]     # unregister it our registry
        sys.path.insert(0, path)
        sys.path.pop(0)
    else:
        return('{} is not loaded'.format(query))
def reloadplugins(data=None, thread=None, ttype=None, name=None, author=None, nickname=None, msg=None):
    logging.info('Reloading plugins')
    unloadplugins(data, author=author)
    loadplugins(data, author=author)
    



#loadplugins()