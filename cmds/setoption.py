import asyncio
from discord import ChannelType
from discord import utils

async def setVoiceChannel(*args):
    client, msg, params, vc = args[:4]
    
    if len(params) > 1:
        channel = utils.get(msg.server.channels, id=params[
                            1], type=ChannelType.voice)

        if vc is None:
            try:
                vc = await client.join_voice_channel(channel)
            except:
                vc = None
                await client.send_message(msg.channel, 'I could not find that Vinyl Room my Liege.')

        else:
            await vc.move_to(channel)
            await client.send_message(msg.channel, 'Moving the Vinyl Room my Liege.')
    else:
        await client.send_message(msg.channel, 'Please tell me the location of the Vinyl Room I should move to, my Liege.')

_commands = {
    'vc': setVoiceChannel
}

name = 'set'
description = 'Set an option to Shitsuji.'
parameters = ['an option. Either of ' +
              ', '.join(['%s' % key for key in _commands.keys()])]
permissions = ['serverop']

async def handler(*args):
    plainTextMsg, msg, client, vc = args[:4]

    params = plainTextMsg.split()

    if params[0] in _commands:
        await _commands[params[0]](client, msg, params, vc)
