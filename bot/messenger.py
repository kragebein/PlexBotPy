#/usr/bin/python3

from fbchat import (Client, ThreadType, Message, EmojiSize, Sticker, TypingStatus, MessageReaction,
                    ThreadColor, Mention)
import asyncio
from bot.config import conf
import logging
import bot.main
from bot.trigger import check
from bot.trigger import trigger
import os
import re
import datetime
import time
import json
import sqlite3
import traceback

logging.basicConfig(level=logging.DEBUG)

def get_attachment(msg):
    '''
    Figures out what type of attachment is being sendt, returns relevant data from that attachment if found 
    '''
    datalist = []
    datatype = '(???)Unknown data recevied'
    try: 
        if msg['attachments']:
            data = msg['attachments']
    except:
        return datatype
    logging.info('Attachment recevied')
    for i in data:
        for x in range(0, len(data)):
            datatype = '(Attachment)Unknown attachment recevied.'
            try: # Try looking for attachments with __typename
                if data[x]['mercury']['blob_attachment']['__typename']:
                    _type = data[x]['mercury']['blob_attachment']['__typename']
                if _type == 'MessageAnimatedImage':
                    picture_uri = data[x]['mercury']['blob_attachment']['animated_image']['uri']
                    datalist.append(picture_uri)
                    datatype = '(GIF)'
                    logging.debug('Attachement: GIF')
                if _type == 'MessageImage':
                    picture_uri = data[x]['mercury']['blob_attachment']['large_preview']['uri']
                    datalist.append(picture_uri)
                    datatype = '(PICTURE)'
                    logging.debug('Attachement: PICTURE')
                if _type == 'MessageVideo':
                    picture_uri = data[x]['mercury']['blob_attachment']['playable_url']
                    datalist.append(picture_uri)
                    datatype = '(VIDEO)'
                    logging.debug('Attachement: VIDEO')
                if _type =='MessageAudio':
                    picture_uri = data[x]['mercury']['blob_attachment']['playable_url']
                    datalist.append(picture_uri)
                    datatype = '(AUDIOCLIP)'
                    logging.debug('Attachement: VIDEO')
                #if _type == 'MessageFile':

                return datatype + (str(datalist))  
            except:
                pass
            try: # try looking for stickers
                if data[x]['mercury']['sticker_attachment']:
                    picture_url = data[x]['mercury']['sticker_attachment']['sprite_image']['uri']
                    datalist.append(picture_url)
                    datatype = '(STICKER)'
                    logging.debug('Attachement: Sticker')
                    return datatype + str(datalist)
            except:
                pass
            try: #Different sticker type
                if data[x]['mercury']['sticker_attachment']:
                    datatype = '(STICKER)unkown'
                    picture_url = data[x]['mercury']['sticker_attachment']['url']
                    datatype = '(STICKER)'
                    datalist.append(picture_url)
                    logging.debug('Attachment: STICKER')
                    return datatype + str(datalist)
            except:
                pass
            try: # Look for Location Sharing
                if data[x]['mercury']['extensible_attachment']['story_attachment']['target']['coordinate']:
                    datatype = '(Shared location)'
                    longitude = data[x]['mercury']['extensible_attachment']['story_attachment']['target']['coordinate']['longitude']
                    datalist.append('Longitude: {}'.format(longitude))
                    latitude = data[x]['mercury']['extensible_attachment']['story_attachment']['target']['coordinate']['latitude']
                    datalist.append('Latitude: {}'.format(latitude))
                    logging.debug('Attachment: LocationSharing')
                    return datatype +str(datalist)
            except:
                pass
    return(datatype)

class PlexBot(Client):
                    
    async def on_message(self, mid=None, author_id=None, message_object=None, thread_id=None,
                         thread_type=ThreadType.USER, at=None, metadata=None, msg=None):
        '''
        Process the incoming messages
        '''
        
        trigger_exec = {"what": '0x1', "wat": '0x1', "what?": "0x1", "woo": '0x2', "woho": '0x2', "wooh": "0x2", "woho!": "0x2"}
        await self.mark_as_delivered(thread_id, message_object.uid)
        await self.mark_as_read(thread_id)
        if author_id != self.uid:
            username = await self.fetch_user_info(author_id)
            user_data = username[author_id]
            nickname = user_data.nickname
            get_name = (await client.fetch_thread_info(thread_id))[thread_id]
            thread_name = get_name.name.replace('\'','')
            name = user_data.name
            bot.main.attu(uid=author_id, name=name, level=0) 
            if thread_id == '256891721183383':
                thread_name = '#gruppa'
            if thread_id == '1044109508990745':
                thread_name = '#plexchat'
            quote = False
            try:
                if msg['delta']['payload']: #We found a payload, this needs conversion.
                    bytesstring = bytes(msg['delta']['payload']).decode('utf8')
                    payload = json.loads(bytesstring)['deltas'][0]['deltaMessageReply']
                    msg['delta'].update(payload['message']) #Add this newly discovered string
                    msg['delta'].update({'repliedToMessage':payload['repliedToMessage'] })
                    quote = True
                    # quotewho = self.fetch_user_info[msg['delta']['repliedToMessage']] #TODO
            except:
                pass
            message_id = msg['delta']['messageMetadata']['messageId']
            try:
                #Message recevied
                if msg['delta']['body']:
                    message = msg['delta']['body']
            except:
                #Image recevied
                if msg['delta']['attachments']:
                    message = get_attachment(msg['delta'])
 
            bot.main.irclog(name=name, message=message, group=thread_name, msg=msg, quote=quote) # log incoming event to file.
            if message == '(???)Unknown data recevied':
                logging.info('Data recevied was not known, not parsing.')
                return False
            query = message.split(' ')[0]
            execute = ''
            if query.lower() in trigger_exec:
                try:
                    execute = trigger_exec[query]
                except:
                    pass
            if execute == '0x1':
                await self.send_local_files(['pictures/0x1.jpg'],thread_id=thread_id,thread_type=thread_type)
                return False
            if execute == '0x2':
                await self.send_local_files(['pictures/0x2.jpg'],thread_id=thread_id,thread_type=thread_type)
                return False
            if query in trigger:
                await self.react_to_message(message_id, MessageReaction.LOVE)
                try:    
                    data = check(msg, thread=thread_id, ttype=thread_type, name=name, author=author_id, nickname=nickname)
                    if data:
                        if '#' in thread_name:
                            logging.info('Replied in group: {}'.format(thread_name))
                        else:
                            logging.info('Replied privately to {}'.format(thread_name))

                        await self.send(Message(text=data), thread_id=thread_id, thread_type=thread_type)
                except Exception as e: 
                    await self.send(Message(text=e), thread_id=thread_id, thread_type=thread_type)
                    traceback.print_exc()
                    await self.react_to_message(message_id, MessageReaction.SAD)
                    pass
    
send = Client()
def say(data):
    logging.info('Saying {}'.format(data))
    client.start(conf.bot_user, conf.bot_password)
    client.send(Message(text=data), thread_id=100039637672981, thread_type=ThreadType.USER)
    client.logout()

loop = asyncio.get_event_loop()
client = PlexBot(loop=loop)
async def main():
    await client.start(conf.bot_user, conf.bot_password)
    client.listen()
    # we need to update the session cookie for say.py
    cookie = client.get_session()
    with open('.cookie', 'w') as kapsel:
        kapsel.write(str(cookie))
        kapsel.close()


