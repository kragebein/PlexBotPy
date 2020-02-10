#!/usr/bin/python3
import discord
from discord import Webhook, RequestsWebhookAdapter
import json, traceback, omdb
import logging
import asyncio, concurrent.futures
from bot.config import conf as conf
from bot.trigger import check
from bot.trigger import trigger
import bot.main
import plugins.announce
servers = {}


def build_embed(_type=None, title=None, results=None, json=None, imdbid=None):
    try:
        from bot.api import ttdb
        omdb.set_default('apikey', conf.omdb_key)
        ''' Build embed data for return output '''
        url = 'https://www.imdb.com/title/{}/'.format(imdbid)
        if _type == 'search':
            embed = discord.Embed(title='{} Matches for your query "{}"'.format(results, title), colour=discord.Colour(0xf9c38b))
            embed.set_footer(text='Plexbot.py', icon_url='https://zhf1943ap1t4f26r11i05c7l-wpengine.netdna-ssl.com/wp-content/uploads/2018/01/pmp-icon-1.png')
            c = 0
            for i in sorted(json.keys(), key=lambda x: json[x][2]):
                name = json[i][0]
                year = json[i][1]
                _type = json[i][2]
                status = json[i][3]
                imdbid = i
                if _type == 'series':
                    f = 'Series'
                else:
                    f = 'Film'
                    
                if status == 'available':
                    status = 'Available for Request'
                    g = ':arrow_heading_down:'

                if status == 'error':
                    status = 'Unavailable'
                    g = '🚫'

                if status == 'exists':
                    status = 'On Plex'
                    g = ':clapper:'

                if status == 'wishlist':
                    status = 'In wishlist'
                    g = '🕕'

                embed.add_field(name='# {} ({}) > {}'.format(c, f, imdbid), value=name + ' ({})\nstatus:\n{} {}'.format(year, status, g))           
                c += 1
        elif _type == 'request':
            json = omdb.imdbid(imdbid, fullplot=True)
            title = json['title']
            year = json['year']
            released = json['released']
            rating = json['ratings'][0]['value']
            try:
                poster = json['poster']
                embed.set_image(url=poster)
            except:
                pass
            rtype = json['type']
            plot = json['plot']
            runtime = json['runtime']
            votes = json['imdb_votes']
            language = json['language']
            url = 'https://www.imdb.com/title/{}/'.format(imdbid)
            embed = discord.Embed(title='Coming soon to a theatre near you!', url=url)
            
            embed.set_footer(text='Plexbot.py', icon_url='https://zhf1943ap1t4f26r11i05c7l-wpengine.netdna-ssl.com/wp-content/uploads/2018/01/pmp-icon-1.png')
            embed.add_field(name='Title', value=title, inline=False)
            embed.add_field(name='Language', value=language)
            embed.add_field(name='Type', value=rtype)
            embed.add_field(name='Release date', value=released)
            embed.add_field(name='Rating', value=rating + '({} votes)'.format(votes))
            embed.add_field(name='Runtime', value=runtime)
            embed.add_field(name='Plot', value=plot, inline=False)
        
        webhook = Webhook.partial(conf.discord_webhook, conf.discord_webtoken, adapter=RequestsWebhookAdapter())
        webhook.send('', embed=embed, username='Plexbot')
    except:
        # if something fails here, main module will fall back to default output.
        return False
    return True
class Plexbot(discord.Client):

    async def on_ready(self):
        logging.info('Logged on as {}'.format(self.user))
        game = discord.Game('Awaiting orders')
        await client.change_presence(status=discord.Status.idle, activity=game)
        # print guild statistics:
        print('Currently serving: ')
        async for guild in client.fetch_guilds(limit=150):
            print('Guild: {} ({})'.format(guild, guild.id))
        loop = client.loop
        plugins.announce.main() 
        await loop.run_in_executor(None, plugins.announce.looper) # Run this in paralell and ship the client with it so it can write to chat.
        

    async def on_guild_channel_create(self, channel):
        if str(channel.name) == 'plex':
            await channel.send('This channel ID: {}\nAccepting input.'.format(channel.id))
        
    async def on_message(self, message):
        ok = '\N{THUMBS UP SIGN}'
        notok = '\N{THUMBS DOWN SIGN}'
        if message.author == self.user:
            return
        if message.content == 'test':
            await message.channel.send('Return data')
        thread_id = message.id
        ttype = str(message.channel)
        author = message.author.id
        nickname = message.author
        name = message.author
        msg = {'delta': {'body': message.content}}
        bot.main.attu(uid=author, name=name, level=0)
        if ttype == 'plex':
            data = check(msg, thread=thread_id, ttype=ttype, name=name, author=author, nickname=nickname)
            if data:
                await message.add_reaction(ok)

                if bot.main.embed is None:
                    await message.channel.send(data)
                    return

                elif bot.main.embed is not None:
                    await message.channel.send('', embed=bot.main.embed)
                    bot.main.embed = None
                    return

            elif data is False:
                await message.add_reaction(notok)

                    

client = Plexbot()
client.run(conf.discord_token)