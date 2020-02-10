#!/usr/bin/python3
# -*- coding: utf-8 -*-
''' Core bot '''
from fbchat import (Client, ThreadType, Message, EmojiSize, Sticker, TypingStatus, MessageReaction,
                    ThreadColor, Mention)
import time
import logging
import sys
from bot.api import *
import asyncio
import sqlite3
import datetime
import os
import re
from bot.config import conf as conf


me = medusa()
cp = couchpotato()
embed = None
def search(input, message=None, thread=None, ttype=None, name=None, author=None, nickname=None, msg=None):
    logging.info('Searching for {}'.format(input))
    results = {}
    search_result = {}
    results = cp.search(input)
    results.update(me.search(input))
    if len(results) == 0:
        return "\"{}\" hadd ingen treff på hverken tv eller film.".format(input)
    c = 0
    ccc = sqlite3.connect('bot/database.sql')
    db = ccc.cursor()
    db.execute("DELETE from latestsearch") # Remove previous search data
    for i in sorted(results.keys(), key=lambda x: results[x][2]):
        name = results[i][0]
        year = results[i][1]
        _type = results[i][2]
        status = results[i][3]
        imdbid = i
        if _type == 'series':
            f = 'S'
        else:
            f = 'F'
        if status == 'available':
            g = '➕'
        if status == 'error':
            g = '🚫'
        if status == 'exists':
            g = '✔'
        if status == 'wishlist':
            g = ':clock1230:'

        search_result[c] = str(c) + '. ' + g + ' ' + f + ' ' + name + ' [' + year + ']\n'
        db_exec = 'INSERT INTO latestsearch VALUES ("{}", "{}")'.format(c, i)
        db.execute(db_exec)
        c+=1
    print_dump = ''
    for i in search_result:
        print_dump += search_result[i]
    ccc.commit()
    ccc.close()
    logging.info('search complete.')
    from bot.discord_main import build_embed
    
    if build_embed(_type='search', title=input, results=c, json=results) is False:
        return print_dump

def test(input):
    return False

def sql(a, q):
    ''' sqlite queries'''
    return None



def irclog(name=None, message=None, group=None, msg=None, quote=None):
    ''' 
    Will emulate the irssi client logstyle\n
    20:30 < username> blahblah
    '''
    logdir = conf.bot_log
    name = name.replace(' ','') # 
    if quote:
        message = '>> "' + msg['delta']['repliedToMessage']['body'] + '" > ' + message
    message = message.encode('utf-8')
    ts = time.time() 
    timestamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M')
    date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d') 
    logfile = logdir + group + '/' + group + '.' + date + '.log' 
    dataentry = str(timestamp) + ' < ' + str(name) + '> ' + message.decode('utf-8') + '\n'
    if not os.path.exists(logdir + group):
        os.mkdir(logdir + group)
    with open(logfile,'a+', encoding='utf-8') as log:
        log.write(dataentry)
    log.close()

def attu(name=None, uid=None, level=None):
    '''
    10 = Superuser
    9 = admin
    5 = PlexAdmin
    0 = log interaction only.
    '''
    c = sqlite3.connect('bot/database.sql')
    query = "SELECT level FROM users WHERE id = '{}'".format(uid)
    db = c.cursor()
    q_res = db.execute(query)
    result = q_res.fetchone()
    if result is not None: # if we find a match, we return the userlevel of this user instead.
        return result[0]
    # if we dont find a result, lets add the user.
    query = "INSERT INTO users VALUES ('{}','{}','{}')".format(uid, name, level)
    db.execute(query)
    logging.info('DB: Added new known user: {}'.format(name))
    c.commit()
    c.close()

def plexbot():
    '''this function loads everything needed for the bot to run, stop this in main() to run plexbot standalone without facebook'''
    if conf.client == 'messenger':
        logging.info('Starting Plexbot.')
        try:
            import bot.messenger
            #import bot.trigger
        except ImportError:       
            logging.error('Couldnt import messenger lib. Shutting down.')
        loop = asyncio.get_event_loop()
        loop.run_until_complete(bot.messenger.main())
        loop.run_forever()
    elif conf.client == 'discord':
        import bot.discord_main

    import bot.trigger


def request(imdbid, message=None, thread=None, ttype=None, name=None, author=None, nickname=None, msg=None):
    regex = "tt[0-9]{1,19}"
    if not re.match(regex, imdbid, re.IGNORECASE):  #seems like we didnt get the regex
        try:
            imdbid = int(imdbid)
        except:
            return('Det der e ikke lov. Prøv igjen.')
        
        cc = sqlite3.connect('bot/database.sql')
        db = cc.cursor()
        query = "SELECT imdbid FROM latestsearch WHERE id = '{}'".format(imdbid)
        try:
            execute = db.execute(query)
            imdbid = execute.fetchone()[0]
        except TypeError as r:
            return "{} e ikke rett nummer. Prøv igjen.".format(imdbid)
        except Exception as r:
            return "Error fra SQL: {}".format(r)
        cc.close()
    if imdbid is None:
        return "Request må ha minst 1 argument"
    
    logging.info('Trying to request {}'.format(imdbid))
    ''' Sets up and processes the request and passes it over to the respective service '''
    data = omdb.imdbid(imdbid)
    if len(data) == 0:
        return False
    _type = data['type']
    if _type == 'series':
      return_data = me.request(imdbid, data)
    elif _type == 'movie' or 'documentary':
       return_data = cp.request(imdbid, data=data)
    
    from bot.discord_main import build_embed
    if build_embed(_type='request', imdbid=imdbid) is False:
        return return_data

def main():
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', datefmt='[%d/%m/%Y %I:%M:%S]', level=logging.INFO)
    plexbot()
    #loadplugins()
    
    
    
    
    