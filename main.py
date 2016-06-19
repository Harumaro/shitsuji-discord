import discord
import asyncio
import random
import os
import sys
from commands import handleCommand
from env import default_role
from env import server_id
from env import vc_id
from env import lobby_chat_id
from env import token
from env import vc

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

    server = discord.utils.get(client.servers, id=server_id)
    channel = discord.utils.get(server.channels, id=vc_id, type=discord.ChannelType.voice)

    vc = await client.join_voice_channel(channel)
    await client.change_status(game=discord.Game(name='unko'))


@client.event
async def on_member_join(member):
    try:
        if default_role:
            resident_role = [discord.utils.get(member.server.roles, name=default_role)]

            await client.add_roles(member, *resident_role)

            invite = None
            try:
                invites = await client.invites_from(member.server)

                if invites:
                    invite = random.choice(invites)
            except:
                pass

            shitpostingChan = invite.channel if invite else discord.utils.get(member.server.channels, id=lobby_chat_id)

        await client.send_message(shitpostingChan, 'Welcome, young master {0.mention}. Enjoy your stay in Gensokyo. Please head over to #guide for a tour.'.format(member))
    except:
        await client.send_message(shitpostingChan, 'Welcome, young master {0.mention}. I apologize I cannot offer you a proper welcome, please ask any of the other young masters.'.format(member))


@client.event
async def on_message(message):

    if client.user.mentioned_in(message):
        await handleCommand(message, client, vc)

client.run(token)
