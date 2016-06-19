import asyncio
from discord import Game

name = '.start'
description = 'Add a status to Shitsuji.'
parameters = ['what to do.']
permissions = ['serverop']


async def handler(*args):
    plainTextMsg, msg, client = args[:3]

    await client.send_message(msg.channel, 'As you wish, my Lord.')

    await client.change_status(game=Game(name=plainTextMsg))
