#!/usr/bin/python3
# -*- coding: utf-8 -*-
''' Init '''
import os
import daemon
global me
me = os.path.dirname(os.path.realpath(__file__))
import logging
logging.basicConfig(level=logging.INFO)
from bot.main import main as run
if __name__ == "__main__":
     run()