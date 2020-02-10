#!/usr/bin/python3
''' Plugin used to announce new additions from Plex (via tautulli) to announce channel '''
import logging
import bot.api
import logging
import sqlite3
from bot.config import conf as conf
#from bot.main import sql
class Plugin():
    def __init__(self):
        ''' initialise and register the plugin ''' 
        self._help = 'This command is used to altering the access level of a particular user.'            # Plugin help definition
        self._trigger = '!raise'                                 # Plugin trigger
        logging.info('Plugin loaded: {}'.format(__name__))
        from bot.trigger import trigger
        trigger.update({self._trigger: self.main})
   
    
    def main(self, *data, message=None, thread=None, ttype=None, name=None, author=None, nickname=None, msg=None):
        '''Main function will deal with raising a users userlevel on request from administrator'''
        usage = 'Usage:\n{} <username> <level 0-10>'.format(self._trigger)
        data = data[0].split(' ')
        if data[0] == '-help':
            return(self._help + '\n' + usage)
        if len(data) != 2: 
            return(usage)
        query = u'SELECT level from users WHERE name = "{}"'.format(data[0])
        alter = u'UPDATE users SET level = "{}" WHERE name = "{}"'.format(data[1], data[0])
        if conf.client == 'discord':
            mentionstring = data[0]
            _data = data[0]
            _data = _data.replace('>', '').replace('<','').replace('!','').replace('@','')
            data[0] = _data
            query = u'SELECT level FROM users WHERE id = "{}"'.format(data[0])
            alter = u'UPDATE users SET level = "{}" WHERE id = "{}"'.format(data[1], data[0])
        # Now we can start accessing db:
        c = sqlite3.connect('bot/database.sql')
        conn = c.cursor()
        try:
            result = conn.execute(query)
            result = result.fetchone()
            result = result[0]
        except:
            c.close()
            return('That user doesnt exists in the database yet')
        conn.execute(alter)
        c.commit()
        c.close()
        logging.info('{} has altered {}\'s access level from {} to {}'.format(name, mentionstring,result, data[1]))
        return('{} has altered {}\'s access level from {} to {}'.format(name, mentionstring,result, data[1]))


    def __del__(self):
        del self
        logging.info('Plugin unloaded: {}'.format(__name__))