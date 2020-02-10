#!/usr/bin/python3
''' Plugin used to announce new additions from Plex (via tautulli) to announce channel.
    This plugin cannot be added with !load, but must be included in the main loop so it
    can run in parallel and not block the other threads in the bot. 

    Add the below to the main class, where 'client' is the looping class.

    from plugins.announce import main as announcer
    loop = client.loop
    await loop.run_in_executor(None, announcer)
 '''
import logging
import bot.api
import time, os, stat, logging, atexit,datetime, traceback, json, omdb, tvdbsimple as tvdb
import discord
from discord import Webhook, RequestsWebhookAdapter
from bot.config import conf as conf
pipe = 'bot/announcepipe'
tvdb.KEYS.API_KEY = conf.ttdb_key

def announce(ratingkey):
    omdb.set_default('apikey', conf.omdb_key)
    year = datetime.datetime.today().year
    '''function returns viable data from tautulli'''
    taut = bot.api.Tautulli() # 
    metadata = taut.get('get_metadata', rating_key=ratingkey)
    _type = metadata['response']['data']['library_name']

    if _type == 'Series':
            episode_name = metadata['response']['data']['title']
            episode = metadata['response']['data']['media_index']
            season = metadata['response']['data']['parent_media_index']
            title = metadata['response']['data']['grandparent_title']
            rating = metadata['response']['data']['rating'] + '/10'
            release = metadata['response']['data']['originally_available_at']
            thetvdb = metadata['response']['data']['parent_guid'].split('//')[1].split('/')[0]
            plot = metadata['response']['data']['summary']
            from bot.api import ttdb
            imdbid = ttdb(thetvdb)
            omdbdata = omdb.imdbid('{}'.format(imdbid))
            url = 'https://www.imdb.com/title/{}/'.format(imdbid)
            if release is '':
                release = str(year) + '*'
            if rating is '' or rating == '/10':
                rating = '1.0/10*'
            embed = discord.Embed(title='New episode from {}'.format(title), url=url, colour=discord.Colour(0xf9c38b))
            embed.add_field(name='Episode name', value=episode_name, inline=False)
            embed.add_field(name='Season', value=season, inline=True)
            embed.add_field(name='Episode', value=episode, inline=True)
            embed.add_field(name='Release date', value=release, inline=True)
            embed.add_field(name='Rating', value=rating, inline=True)
            embed.add_field(name='Plot', value=plot, inline=False)
            try:
                embed.set_image(url=omdbdata['poster'])
            except:
                pass
            embed.set_footer(text='Plexbot.py', icon_url='https://zhf1943ap1t4f26r11i05c7l-wpengine.netdna-ssl.com/wp-content/uploads/2018/01/pmp-icon-1.png')

    elif _type == 'Films' or _type == '4k Movies' or _type == 'Norsk':
            title = metadata['response']['data']['title']
            release = metadata['response']['data']['originally_available_at']
            plot = metadata['response']['data']['summary']
            rating = metadata['response']['data']['rating'] + '/10'
            imdbid = metadata['response']['data']['guid'].split('//')[1].split('?')[0]
            omdbdata = omdb.imdbid('{}'.format(imdbid))
            if release is '':
                release = str(year) + '*'
            if rating is '' or rating == '/10':
                rating = '1.0/10*'
            url = 'https://www.imdb.com/title/{}/'.format(imdbid)

            embed = discord.Embed(title='New movie "{}" available'.format(title), url=url)
            embed.add_field(name='Original title', value=title)
            embed.add_field(name='Release date', value=release, inline=True)
            embed.add_field(name='Rating', value=rating, inline=True)
            embed.add_field(name='Plot', value=plot)
            try:
                embed.set_image(url=omdbdata['poster'])
            except:
                pass
            embed.set_footer(text='Plexbot.py', icon_url='https://zhf1943ap1t4f26r11i05c7l-wpengine.netdna-ssl.com/wp-content/uploads/2018/01/pmp-icon-1.png')

    else:
        logging.info('Added rating key {} in new library: {}'.format(ratingkey, _type))
        embed = discord.Embed(title='A new item was added')
        embed.add_field(name='Rating key', value=ratingkey)
        embed.add_field(name='Section', value=_type)
        embed.set_footer(text='Plexbot.py', icon_url='https://zhf1943ap1t4f26r11i05c7l-wpengine.netdna-ssl.com/wp-content/uploads/2018/01/pmp-icon-1.png')
    webhook = Webhook.partial(conf.discord_webhook, conf.discord_webtoken, adapter=RequestsWebhookAdapter())
    webhook.send('', embed=embed, username='Plexbot')

def cleanup():
    ''' cleanup leftover stuff '''
    print('Exit detected, removing pipe.')
    os.remove(pipe)
    return None

def looper():
    ''' looper always checks fifo pipe for new input '''
    while True:
        with open(pipe) as fifo:
            while True:
                data = fifo.read()
                if len(data) == 0:
                    break
                data = '{0}'.format(data)
                logging.info('Recevied {} through fifo.'.format(data))
                try:
                    announce(data)
                except Exception as r:
                    print('Got exception: {}'.format(r))
                    traceback.print_exc()
                    break
                    
def main():
    atexit.register(cleanup) # We need to clean up pipes on shutdown.
    tempdata = []
    if os.path.exists(pipe): 
        if stat.S_ISFIFO(os.stat(pipe).st_mode): 
            os.remove(pipe)
        else:   
            with open(pipe, 'r') as temp:
                tempdata = temp.readlines()
                temp.close()
                if len(tempdata) >= 0:
                    logging.info('Announcing shows that werent announced while the fifo pipe was down.')
                    for i in tempdata:
                        announce(i)
            os.remove(pipe)
    try:  
        os.mkfifo(pipe)
        logging.info('Announcer: fifo created. Bot will be announcing events.')
    except Exception as r:
        logging.info('Couldnt create fifo. Bot will not be announcing events. ({})'.format(r))
