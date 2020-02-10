from datetime import datetime
import os, sqlite3, time, re, random, linecache
import logging
import requests
import time
from bot.main import attu
from bot.config import conf as conf


class Plugin():
    def __init__(self):
        ''' initialise and register the plugin ''' 
        self._help = 'This plugin "disallows" reposts from happenig.'            # Plugin help definition
        self._trigger = r'(?P<url>https?://[^\s]+)'                                 # Plugin trigger
        logging.info('Plugin loaded: {}'.format(__name__))
        # Lets update trigger mechanism
        from bot.trigger import trigger
        trigger.update({self._trigger: self.repost}) 
    

    def checklink(self, url):
        ignore = r"(https:\/\/scontent.xx.fbcdn.net|https:\/\/cdn.fbsbx.com).*$"
        if re.match(url, ignore, re.IGNORECASE) is not True:
            return url
        #data=None, thread=None, ttype=None, name=None, author=None, nickname=None, msg=None
        # who, channel, url, mentionstring
    def repost(self, data=None, thread=None, ttype=None, name=None, author=None, nickname=None, msg=None):
        url = msg['delta']['body']
        who = name
        channel = ttype
        t = time.localtime()
        dato = time.strftime("%Y/%m/%d %H:%M:%S", t)
        try:
            conn = sqlite3.connect('bot/database.sql')
        except:
            print('unable to connect to sqlite3.sql')
        try:
            url = re.search(r"(?P<url>https?://[^\s]+)", url).group("url")
        except Exception as r:
            return('Exception:\n{}'.format(r))
        if self.checklink(url) == None:
            return('second checkpoint')
        c = conn.cursor()
        exist = c.execute('SELECT who,channel,link,dato FROM repost WHERE link = "{}" AND channel ="{}" ORDER BY dato LIMIT 1'.format(url, channel))
        result = exist.fetchone()
        print(result)
        if result is None: #This will add the link to the database.
            c = conn.cursor()
            #tupl = who, channel, url, dato
            sql = 'INSERT INTO repost values (\'{}\',\'{}\',\'{}\',\'{}\')'.format(who, channel, url, dato)
            print(sql)
            c.execute(sql)
            conn.commit()
            logging.info('reposter: Adding {} from {} in {} to database'.format(url, who, channel))
            conn.close()
        elif result[1] == channel:
                conn.close()
                print('reposter: Found a previously shared link!')
                if str(who) != str(result[0]):
                    return 'Ro no litt ned <@{}>, den {} vart den linken delt av {}'.format(author, result[3],result[0])
                else:
                    return '<@{}>! Du har delt den linken tidligere ro no litt ned! ({})'.format(author, result[3])
        return None

    def __del__(self):
        
        del self
        logging.info('Plugin unloaded: {}'.format(__name__))