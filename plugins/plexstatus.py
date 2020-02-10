#!/usr/bin/python3 
# encoding: utf-8
''' 
Plugin that provides status from Plex Server.
Returns data in this format:
Siste lagt til: [F] Season 7 (~19 timer siden)
#2:🔥BendikNilsskog spiller av The Mandalorian - Chapter 5: The Gunslinger. (85%/100%) [h264/eac3/4492kbps(8.98%)/720]. Bruker Transcode via Android
'''
import logging
import sys
import json
import os
import requests
from bot.main import attu
from bot.config import conf as conf
import time


class Plugin():
    def __init__(self, message=None, thread=None, ttype=None, name=None, author=None, nickname=None, msg=None): #Plugin initialisation.
        ''' initialise and register the plugin ''' 
        self._help = 'Vis kem som spæll ka på plex.'            # Plugin help definition
        self._trigger = '!plex'                                 # Plugin trigger
        self._disallowed = ['256891721183383']      # Plugin allowed group chats [in, list, format]
        logging.info('Plugin loaded: {}'.format(__name__))
        # Lets update trigger mechanism
        from bot.trigger import trigger
        trigger.update({self._trigger: self.main}) 

    def get(self, where, **argv):
        url = conf.taut_location + '/api/v2?apikey=' + conf.taut_token + '&cmd='+ where
        http = requests.get(url, params=argv)
        r = json.loads(http.text)
        return r

    def main(self, *data, message=None, thread=None, ttype=None, name=None, author=None, nickname=None, msg=None):
        ''' main thread sources the data'''
        if thread in self._disallowed:
            return('Bruk den andre chatten.')
        activity = self.get('get_activity')     # get the current activity
        last_add = self.get('get_recently_added', count=1)  # get the last added item.
        since = int(time.time()) - int(last_add['response']['data']['recently_added'][0]['added_at'])
        since = int(since) / 60 / 60
        last_meta = self.get('get_metadata', rating_key=last_add['response']['data']['recently_added'][0]['rating_key'])
        last_title = last_meta['response']['data']['full_title']

        stream_count_total = activity['response']['data']['stream_count']
        bandwidth = activity['response']['data']['total_bandwidth']
        #transcodes = activity['response']['data']['stream_count_transcode']
        #directp = activity['response']['data']['stream_count_direct_play']
        #directs = activity['response']['data']['stream_count_direct_stream']
        if int(stream_count_total) == 0:
            streamers = 'Det e folketomt på plex. Ingen ser på nåkka.'
        else:
            count = 0
            streamers = ''
            for i in activity['response']['data']['sessions']:
                title = i['full_title']
                stream_perc = i['progress_percent']
                descicion = i['stream_video_decision']
                descicion = descicion.replace('copy','Direct Stream').replace('direct play', 'Direct Play').replace('transcode','Transcode')
                username = i['username']
                platform = i['platform']
                stream_codec = i['video_codec']
                stream_audio = i['audio_codec']
                stream_bitrate = i['bitrate']
                if descicion == 'Direct Play':
                    icon = '👍'
                elif descicion == 'Transcode':
                    icon = '🔥'
                elif descicion == 'Direct Stream':
                    icon = '👍'
                else:
                    icon = '?'
                # [$STREAM_CODEC/$STREAM_AUDIO/${STREAM_BIT}kbps($UTIL%)/${STREAM_RES}]
                stream_data = '[{}/{}/{}kbps]'.format(stream_codec, stream_audio, stream_bitrate)
                data = '#{}{} {} is playing {} ({}/100%) {}  {}/{}\n'.format(count, icon, username, title, stream_perc,stream_data, platform, descicion)

                streamers+=data
                count += 1

        last_add = 'Sist lagt til: {}, ({}t sia)'.format(last_title, str(since)[0:4])
        returnbuf = last_add + ' \n' + streamers
        return(returnbuf)
    #1:🔥SimenMyklebost spiller av The Lord of the Rings: The Fellowship of the Ring. (72%/100%) [h264/ac3/3774kbps(7.54%)/720]. Bruker Transcode via Playstation 4

    def __del__(self):  #Plugin deconstruction
        ''' clean up temprary files, lists, dicts and variables used by this plugin'''
        del self #Unload this plugin class from cpython registry.
        logging.info('Plugin unloaded: {}'.format(__name__))




