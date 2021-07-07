#!/usr/bin/env python3
# -*- coding:utf-8 -*-

################################################################################
# File:          run                                                          ##
# Project:       back                                                         ##
# File Created:  2021-06-24, 23:14:58                                         ##
# Author:        Brandon Gachenot (brandon1.gachenot@epitech.eu)              ##
# -----                                                                       ##
# Last Modified: 2021-06-25, 11:42:14                                         ##
################################################################################

import discord
import aioredis
import asyncio
import json
import sys
import os
import random
import time

REDIS_URL = os.getenv('REDIS_URL')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_LOGS = os.getenv('CHANNEL_LOGS')

r = aioredis.from_url("redis://{}".format(REDIS_URL))
client = discord.AutoShardedClient(command_prefix = '>', description="This is the back-end Bot")

@client.event
async def on_ready():
    print("Client started and ready to catch requests.", file=sys.stderr)

async def back_loop():
    while True:
        res = await r.blpop('queue')
        if res == {} or res[0].decode("UTF-8") != 'queue':
            continue
        data = json.loads(res[1])
        route = data['route']
        channel = data['channel_id']
        channel = await client.fetch_channel(channel)
        if route == "hello":
            user = data['author_id']
            user = await client.fetch_user(user)
            await channel.send('Hello {}! (From {})'.format(user.mention, os.uname()[1]))
        elif route == "add":
            params = json.loads(data['params'])
            nb_1 = params['nb_1']
            nb_2 = params['nb_2']
            await channel.send('{} + {} = {} (From {})'.format(nb_1, nb_2, nb_1 + nb_2, os.uname()[1]))

async def periodic(time: int):
    while True:
#        channel = await client.fetch_channel(857728851094536202)
#        await channel.send('Welcome from Asyncio Coroutine periodic function')
        await asyncio.sleep(time)

async def internal_exit():
    await r.close()

loop = asyncio.get_event_loop()
task = loop.create_task(client.start(DISCORD_TOKEN))
task = loop.create_task(back_loop())
task = loop.create_task(periodic(3600))
try:
    loop.run_until_complete(task)
except KeyboardInterrupt:
    print("Received CTRL+C. Exiting...", file=sys.stderr)
    asyncio.run(internal_exit())
