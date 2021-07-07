#!/usr/bin/env python3
# -*- coding:utf-8 -*-

################################################################################
# File:          run                                                          ##
# Project:       front                                                        ##
# File Created:  2021-06-24, 14:50:04                                         ##
# Author:        Brandon Gachenot (brandon1.gachenot@epitech.eu)              ##
# -----                                                                       ##
# Last Modified: 2021-06-25, 12:23:00                                         ##
################################################################################

import discord
import datetime
from discord.ext import commands
import asyncio
import aioredis
import os
import sys
import json

REDIS_URL = os.getenv('REDIS_URL')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_LOGS = os.getenv('CHANNEL_LOGS')
print("test: {}".format(os.getenv('DISCORD_TOKEN')), file=sys.stderr)
del os.environ['REDIS_URL']
del os.environ['DISCORD_TOKEN']
del os.environ['CHANNEL_LOGS']
print("test: {}".format(os.getenv('DISCORD_TOKEN')), file=sys.stderr)

r = aioredis.from_url("redis://{}".format(REDIS_URL))
bot = commands.AutoShardedBot(command_prefix='>', description="This is the front-end Bot")

@bot.command()
async def ping(ctx):
    await ctx.send('pong')

@bot.command()
async def hello(ctx):
    data = json.dumps({'route': "hello", 'channel_id': ctx.channel.id, 'author_id': ctx.author.id})
    await r.rpush("queue", data)

@bot.command()
async def add(ctx, nb_1: int, nb_2: int):
    params = json.dumps({'nb_1': nb_1, "nb_2": nb_2})
    data = json.dumps({'route': "add", 'channel_id': ctx.channel.id, 'author_id': ctx.author.id, 'params': params})
    await r.rpush("queue", data)

@bot.command()
async def info(ctx):
    embed = discord.Embed(title=f"{ctx.guild.name}", description="Lorem Ipsum asdasd", timestamp=datetime.datetime.utcnow(), color=discord.Color.blue())
    embed.add_field(name="Server created at", value=f"{ctx.guild.created_at}")
    embed.add_field(name="Server Owner", value=f"{ctx.guild.owner}")
    embed.add_field(name="Server Region", value=f"{ctx.guild.region}")
    embed.add_field(name="Server ID", value=f"{ctx.guild.id}")
    # embed.set_thumbnail(url=f"{ctx.guild.icon}")
    embed.set_thumbnail(url="https://pluralsight.imgix.net/paths/python-7be70baaac.png")

    await ctx.send(embed=embed)

# Events
@bot.event
async def on_ready():
    # await bot.change_presence(activity=discord.Streaming(name="Tutorials", url="http://www.twitch.tv/accountname"))
    print('Bot started and ready to catch requests.', file=sys.stderr)

# @bot.listen()
# async def on_message(message):
#     if message.author.id == self.user.id:
#         return
#     if "tutorial" in message.content.lower():
#         # in this case don't respond with the word "Tutorial" or you will call the on_message event recursively
#         await message.channel.send('This is that you want http://youtube.com/fazttech')
#         await bot.process_commands(message)

async def internal_exit():
    await r.close()

loop = asyncio.get_event_loop()
task = loop.create_task(bot.start(DISCORD_TOKEN))
try:
    loop.run_until_complete(task)
except KeyboardInterrupt:
    print("Received CTRL+C. Exiting...", file=sys.stderr)
    asyncio.run(internal_exit())
