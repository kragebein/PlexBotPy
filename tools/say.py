#!/usr/bin/python3
# -*- coding: utf-8 -*-
''' Prints data to the approriate user on facebook '''
import asyncio
import logging
import sys
import getopt
sys.path.append('..')
from bot.config import conf
from fbchat import Client, ThreadType, Message

who = sys.argv[1]
message = sys.argv[2]
logging.basicConfig(level=logging.INFO)

if who == 'group':
    thread_type = ThreadType.GROUP
    thread_id = 1044109508990745
else:
    thread_type = ThreadType.USER
    thread_id = who

client = Client()
async def main():
    client = Client()
    start = await client.start(conf.bot_user, conf.bot_password)
    logging.info('Printing {} to {}'.format(message, who))
    await client.send(Message(text=message), thread_id=thread_id, thread_type=thread_type)
client.loop.run_until_complete(main())
