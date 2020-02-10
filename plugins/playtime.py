#!/usr/bin/python3 
import json
import logging
import bot.api
import requests
from bot.config import conf 


class Plugin():

    def __init__(self):
        self._help = 'Tveng gjennom et nytt søk av alle ting i ønskelista'
        self._trigger = '!playtime'                                        
        self._disallowed = ['256891721183383']                  
        logging.info('Plugin loaded: {}'.format(__name__))
        # update trigger mechanism
        from bot.trigger import trigger
        trigger.update({self._trigger: self.main}) 


    def get(self, route, **argv):
        url = conf.taut_location + '/api/v2?apikey=' + conf.taut_token + '&cmd='+ route
        http = requests.get(url, params=argv)
        r = json.loads(http.text)
        return r

    def main(self,  *data, message=None, thread=None, ttype=None, name=None, author=None, nickname=None, msg=None):
        play_time = 0
        if len(data) >= 2:
            return('Syntax:\n!playtime <brukernavn>\n!playtime')
        logging.info('Calculating playtime across all users..')
        if len(data) is 0:
            usernames = self.get('get_user_names')
            usernames = usernames['response']['data']
            for count in usernames:
                userid = count['user_id']
                if userid is not 0:
                    timedata = self.get('get_user_watch_time_stats', user_id=userid)
                    play_time += timedata['response']['data'][3]['total_time']
            hours = int(play_time) / 60 / 60
            return('Tima brukt på plex: {} (totalt over alle brukera)'.format(round(hours, 2)))
        else:
            logging.info('Calculating single user playtime..')
            user = data[0]
            usernames = self.get('get_user_names')
            usernames = usernames['response']['data']
            for count in usernames:
                if count['friendly_name'].upper() == user.upper():
                    timedata = self.get('get_user_watch_time_stats', user_id=count['user_id'])
                    play_time = timedata['response']['data'][3]['total_time']
            hours = int(play_time / 60 / 60)
            if hours is 0:
                return('Fant ikke {} på plex, eller brukeren har ikke nå data akkumulert.'.format(user))
            else:
                return('{} har brukt {} tima på Plex.'.format(user, round(hours, 2)))
        
    
    def __del__(self):
        logging.info('Plugin unloaded: {}'.format(__name__))
