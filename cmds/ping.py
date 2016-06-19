import asyncio

name = 'ping'
description = 'Check if Shitsuji is awake.'
parameters = []
permissions = []


async def handler(*args):
    plainTextMsg, msg, client = args[:3]
    
    await client.send_message(msg.channel, 'Pong, my lord.')
