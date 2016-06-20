import asyncio
import random
import re
from datetime import datetime
from command import Command
from env import excluded_ch_ids

def hasPermission(user, cmd):
    permissions = cmd.permissions

    if not permissions:
        return True

    for role in user.roles:
        if list(filter(lambda permission: role.name.lower() == permission.lower(), permissions)):
            return True

    return False


async def handleCommand(msg, client, vc):
    messageContent = re.sub(r'(?is)@Shitsuji', '',
                            msg.clean_content).strip()
    command = Command(messageContent)

    if command.name:
        params = re.sub(r'(?is)' + command.name, '', messageContent).strip()
        
        if not(hasPermission(msg.author, command)):
            await client.send_message(msg.channel, 'I cannot do that for you, young master.')
        elif len(params.split()) < len(command.parameters):
            await client.send_message(msg.channel, 'Please add more details to your request, my liege. I would need to know ' + ', '.join(command.parameters))
        else:
            print(datetime.utcnow().isoformat(' ') + ' ' +
                  msg.author.name + ' -> ' + command.name)
            await command.handler(params, msg, client, vc)

    elif messageContent is '':
        message = 'Yes, my liege? Fancy perhaps a list of things I could do for you? Here, have a pamphlet.\n\n'

        message += 'How to operate Shitsuji\n'
        message += '- <only the bot mention>: show this guide\n'
        message += '- <any text which is not a command>: talk with the bot\n'
        for command in Command.list():
            message += '- ' + command.name + \
                ': ' + command.description + '\n'

        await client.send_message(msg.channel, message)

    else:
        counter = 0
        stopAt = random.randint(0, 99)

        sentence = ''

        dtAfter = datetime(2016, 5, 18, 0, 0, 0, 0)

        channel = random.choice(list(filter(lambda channel: channel.id not in excluded_ch_ids, msg.server.channels)))

        try:
            lastSentence = ''
            async for log in client.logs_from(channel, limit=100, before=None, after=dtAfter):
                lastSentence = log.content
                if counter == stopAt:
                    sentence = lastSentence
                else:
                    counter += 1
            if not sentence:
                sentence = lastSentence
        except Exception as e:
            print(e)
            sentence = 'A prayer for Discord, who lost its memes today.'
            pass

        await client.send_message(msg.channel, sentence if sentence != '' else 'I am extremely sorry my Lord, but I couldn\'t find that meme')