import discord
import asyncio
import random
import os
import sys
from commands import handleCommand
from env import default_role
from env import lobby_ch_id
from env import token

vc = {}

if sys.platform == 'win32':
    os.environ['PATH'] += os.path.dirname(__file__) + os.pathsep + 'bin'
else:
    discord.opus.load_opus('/app/vendor/opus/lib/libopus.so.0')

client = discord.Client()

@client.event
async def on_ready():
    global vc

    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

    for server in client.servers:
        try:
            channel = discord.utils.get(server.channels, type=discord.ChannelType.voice)

            vc[server.id] = await client.join_voice_channel(channel)
        except:
            vc[server.id] = None

    await client.change_presence(game=discord.Game(name='ready for duty'))

@client.event
async def on_server_join(server):
    global vc
    
    try:
        channel = discord.utils.get(server.channels, type=discord.ChannelType.voice)

        vc[server.id] = await client.join_voice_channel(channel)
    except:
        vc[server.id] = None

@client.event
async def on_member_join(member):
    lobbyCh = discord.utils.get(member.server.channels, id=lobby_ch_id)

    try:
        if default_role:
            def_role = [discord.utils.get(member.server.roles, name=default_role)]

            await client.add_roles(member, *def_role)

        await client.send_message(lobbyCh, 'Welcome, young master {0.mention}. Enjoy your stay in Gensokyo. Please head over to #guide for a tour.'.format(member))
    except:
        await client.send_message(lobbyCh, 'Welcome, young master {0.mention}. I apologize I cannot offer you a proper welcome, please ask any of the other young masters.'.format(member))


@client.event
async def on_message(message):
    if client.user.mentioned_in(message):
        await handleCommand(message, client, vc[message.server.id])

client.run(token)
