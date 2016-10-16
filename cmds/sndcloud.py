import soundcloud
import asyncio
import re
from env import soundcloud_cid

_scclient = soundcloud.Client(client_id=soundcloud_cid)
players = {}

class PlayerSettings:
    def __init__(self):
        self.currentQuery = []
        self.lastSong = None
        self.queue = []
        self.player = None

_commands = ['song named', 'song', 'track', 'next', 'skipall', 'this again']
_mainLoop = asyncio.get_event_loop()

name = 'play'
description = 'Send Shitsuji to get music from soundcloud'
parameters = ['either of ' + ', '.join(_commands)]
permissions = []


async def handler(*args):
    plainTextMsg, msg, client, vc = args[:4]
    global players

    if msg.server.id not in players:
        players[msg.server.id] = PlayerSettings()

    if vc is None:
        await client.send_message(msg.channel, 'We do not have a Vinyl Room, my Liege.')

        return

    params = plainTextMsg.split()

    if len(params) > 2 and ' '.join(params[0:2]) == _commands[0]:
        message = await client.send_message(msg.channel, 'I will be off to check the music shop.')

        tracks = _scclient.get('/tracks', q=' '.join(params[1:]))
        players[msg.server.id].currentQuery.clear()

        songList = ''
        for cnt, track in enumerate(tracks):
            if track.streamable:
                songList += '\n{0}. {1.title} by {1.user[username]}'.format(
                    cnt, track)

                players[msg.server.id].currentQuery.append({
                    'stream': track.stream_url,
                    'permalink': track.permalink_url,
                    'title': track.title,
                    'author': track.user['username']
                })

        await client.edit_message(message, 'Here is what I found at the shop my liege. {0}'.format(songList))
    elif len(params) > 1 and params[0] == _commands[1]:
        track_url = params[1]

        try:
            track = _scclient.get('/resolve', url=track_url)

            currentSong = {
                'stream': track.stream_url,
                'permalink': track.permalink_url,
                'title': track.title,
                'author': track.user['username']
            }

            enqueue(msg.server.id, currentSong)
            if players[msg.server.id].player is not None and players[msg.server.id].player.is_playing():
                await client.send_message(msg.channel, 'Keeping {title} by {author} for later.'.format(**currentSong))
            else:
                await dequeueAndPlay(msg, client, vc)
        except:
            await client.send_message(msg.channel, 'I did not found that at the shop, young master.')
            pass

    elif len(params) > 1 and params[0] == _commands[2]:
        if players[msg.server.id].currentQuery:
            currentSong = players[msg.server.id].currentQuery[int(params[1])] if params[
                1].isdigit() else None

            enqueue(msg.server.id, currentSong)
            if players[msg.server.id].player is not None and players[msg.server.id].player.is_playing():
                await client.send_message(msg.channel, 'Keeping {title} by {author} for later.'.format(**currentSong))
            else:
                await dequeueAndPlay(msg, client, vc)
        else:
            await client.send_message(msg.channel, 'I did not shop for music yet, young master.')
    elif len(params) == 1 and params[0] == _commands[3]:
        if players[msg.server.id].player is not None:
            players[msg.server.id].player.stop()
    elif len(params) == 1 and params[0] == _commands[4]:
        players[msg.server.id].queue.clear()
        if player is not None:
            players[msg.server.id].player.stop()
    elif len(params) == 2 and ' '.join(params[0:2]) == _commands[5]:
        enqueue(msg.server.id, players[msg.server.id].lastSong)
        if players[msg.server.id].player is not None and players[msg.server.id].player.is_playing():
            await client.send_message(msg.channel, 'Keeping {title} by {author} for later.'.format(**players[msg.server.id].lastSong))
        else:
            await dequeueAndPlay(msg, client, vc)
    else:
        message = await client.send_message(msg.channel, 'I am sorry my liege, I did not quite catch that. Did you mean to play {0}?'.format(', '.join(_commands)))


def enqueue(server_id, song):
    global players

    players[server_id].queue.append(song)

async def dequeueAndPlay(msg, client, vc):
    global players

    if players[msg.server.id].queue:
        players[msg.server.id].lastSong = players[msg.server.id].queue.pop(0)
        if players[msg.server.id].player is not None:
            del players[msg.server.id].player
        
        stream_url = _scclient.get(
            players[msg.server.id].lastSong['stream'], allow_redirects=False)
        stream_url = 'http' + \
            re.sub(r'(?is)https', '', stream_url.location).strip()

        players[msg.server.id].player = vc.create_ffmpeg_player(stream_url, after=lambda: asyncio.ensure_future(
            dequeueAndPlay(msg, client, vc), loop=_mainLoop))
        players[msg.server.id].player.start()

        await client.send_message(msg.channel, 'Next comes {title} from {permalink}'.format(**players[msg.server.id].lastSong))
    else:
        await client.send_message(msg.channel, 'We are out of songs my liege.')
