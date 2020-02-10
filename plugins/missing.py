#!usr/bin/python3
''' This plugin allows for users to request episodes that havent been automatically downloaded
    usage: !missing tt<imdbid> season, episode. for example: tt728592 8 2 '''
import logging
import json
from bot.main import ttdb
from bot.main import attu
import omdb
import bot.api
import re

class Plugin():
    def __init__(self, message=None, thread=None, ttype=None, name=None, author=None, nickname=None, msg=None):
        self._help = 'Gjør et forced søk på imdbid <sesong> <episode>'            
        self._trigger = '!missing'                                 
        self._disallowed = ['256891721183383']      
        logging.info('Plugin loaded: {}'.format(__name__))
        from bot.trigger import trigger
        trigger.update({self._trigger: self.main}) 

    def main(self, *data, message=None, thread=None, ttype=None, name=None, author=None, nickname=None, msg=None):
        if thread in self._disallowed:
            return('Bruk plexchatten tell det her.')
        data = data[0].split()
        if len(data) is not 3:
            return('Syntax: !missing <imdbid> <sesong> <episode>\n🚫!missing mor di \n👍!missing tt12354 2 8')
        try:
            imdbid = data[0]
            season = int(data[1])
            episode = int(data[2])
        except:
            return('Syntax: !missing <imdbid> <sesong> <episode>\n🚫!missing {} {} {} \n👍!missing tt12354 2 8'.format(data[0], data[1], data[2]))
        me = bot.api.medusa()
        ttdbid = ttdb(imdbid)
        result = json.loads(me.get('episode', indexerid=ttdbid, season=season, episode=episode))
        title = omdb.imdbid(imdbid)
        title = title['title']
        api_result = result['result']
        if api_result == 'success':
            episode_name = title + ' - ' + result['data']['name']
            episode_status = result['data']['status']
            if re.match('(Downloaded|Archived)', episode_status):
                # This episode already exists, but we'll force download another version.
                setstatus = json.loads(me.get('episode.setstatus', status='wanted', indexerid=ttdbid, season=season, episode=episode, force=1))
                logging.info('Set status of {} to "wanted"\n{}'.format(imdbid,setstatus))
                if setstatus['result'] == 'success':
                    return('{} eksistert på systemet fra før av, men den bi henta ned i ny version.'.format(episode_name))
                elif setstatus['result'] == 'failure':
                    return('Error: {}'.format(setstatus)) # Need to print the entire message to debug.
                elif setstatus['result'] == 'error':
                    return('Error: {}'.format(setstatus))
                print(setstatus)
            if episode_status == 'Wanted':
                # This episode is already in wanted status, but we can force a direct search instead. #TODO: await this function
                search = json.loads(me.get('episode.search', indexerid=ttdbid, season=season, episode=episode))
                logging.info('Did a search for wanted episode of {}\n{}'.format(ttdbid, search))
                if search['result'] == 'success':
                    return('Gjor et nytt forsøk på å finn "{}", og fant en episode! Kommer fortløpende!'.format(episode_name))
                elif search['result'] == 'failure':
                    return('Gjor et nytt forsøk på å finn "{}", klart ikke å finn en episode i det hele tatt :('.format(episode_name))
                elif search['result'] == 'error':
                    return('Det skjedd nå feil under søket av episoden:\n{}'.format(search))
            if re.match('(Skipped|Ignored|Snatched)', episode_status):
                # This episode has been skipped, ignored or has already been snatched. We'll force a new search. 
                search = json.loads(me.get('episode.search', indexerid=ttdbid, season=season, episode=episode))
                logging.info('Forced a new search of skipped episode from {}\n{}'.format(ttdbid, search))
                if search['result'] == 'success':
                    return('OOps, episoden mangla, Fant {} med {} under søket, kommer på plex Asap. '.format(title, result['data']['name']))
                elif search['result'] == 'failure':
                    return('Gjor et nytt forsøk på å finn "{}", klart ikke å finn en episode i det hele tatt :('.format(episode_name))
                elif search['result'] == 'error':
                    return('Det skjedd nå feil under søket av episoden:\n{}'.format(search))
        elif api_result == 'error':
            # User is likely out of bounds. Episode/Season range doesnt match what we have on file.
            logging.info('Moom, {} is being an idiot again!'.format(name))
            # print(me.get('episode', indexerid=ttdbid, season=1, episode=1)) # debug
            return('Feil:\n{} {}x{} e ikke en gyldig kombinasjon av sesonga å episoda'.format(title, season, episode))
        elif api_result == 'failure':
            return('Serien fins ikke på plex enda, den må !requestes først.')
        



    def __del__(self):
        del self    # unload from cpython registry.
        logging.info('Plugin unloaded: {}'.format(__name__))

