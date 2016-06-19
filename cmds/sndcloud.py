import soundcloud
import asyncio
import re
from env import soundcloud_cid

_scclient = soundcloud.Client(client_id=soundcloud_cid)
_currentQuery = []
_queue = []
_player = None
_commands = ['song named', 'song', 'track', 'next', 'skipall']

name = 'play'
description = 'In Testing.'
parameters = ['the command.']
permissions = ['serverop']


async def handler(*args):
    plainTextMsg, msg, client, vc = args[:4]
    global _player

    params = plainTextMsg.split()

    if len(params) > 2 and ' '.join(params[0:2]) == _commands[0]:
        message = await client.send_message(msg.channel, 'I will be off to check the music shop.')

        tracks = _scclient.get('/tracks', q=' '.join(params[1:]))
        _currentQuery.clear()

        songList = ''
        for cnt, track in enumerate(tracks):
            if track.streamable:
                songList += '\n{0}. {1.title} by {1.user[username]}'.format(
                    cnt, track)

                _currentQuery.append({
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

            enqueue(currentSong)
            if _player is not None and _player.is_playing():
                await client.send_message(msg.channel, 'Keeping {title} by {author} for later.'.format(**currentSong))
            else:
                await dequeueAndPlay(msg, client, vc)
        except:
            await client.send_message(msg.channel, 'I did not found that at the shop, young master.')
            pass

    elif len(params) > 1 and params[0] == _commands[2]:
        if _currentQuery:
            currentSong = _currentQuery[int(params[1])] if params[
                1].isdigit() else None

            enqueue(currentSong)
            if _player is not None and _player.is_playing():
                await client.send_message(msg.channel, 'Keeping {title} by {author} for later.'.format(**currentSong))
            else:
                await dequeueAndPlay(msg, client, vc)
        else:
            await client.send_message(msg.channel, 'I did not shop for music yet, young master.')
    elif len(params) == 1 and params[0] == _commands[3]:
        _player.stop()
    elif len(params) == 1 and params[0] == _commands[4]:
        _queue.clear()
        _player.stop()
    else:
        message = await client.send_message(msg.channel, 'I am sorry my liege, I did not quite catch that. Did you mean to play {0}?'.format(', '.join(_commands)))


def enqueue(song):
    _queue.append(song)


async def dequeueAndPlay(msg, client, vc):
    if _queue:
        currentSong = _queue.pop(0)
        global _player
        if _player is not None:
            del _player

        stream_url = _scclient.get(
            currentSong['stream'], allow_redirects=False)
        stream_url = 'http' + \
            re.sub(r'(?is)https', '', stream_url.location).strip()

        _player = vc.create_ffmpeg_player(stream_url, after=lambda: asyncio.ensure_future(
            dequeueAndPlay(msg, client, vc), loop=asyncio.get_event_loop()))
        _player.start()

        await client.send_message(msg.channel, 'Next comes {title} from {permalink}'.format(**currentSong))
    else:
        await client.send_message(msg.channel, 'We are out of songs my liege.')
