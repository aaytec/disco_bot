import os
import discord
import nacl
import youtube_dl
import requests

from discord import Game
from discord.ext import commands
from enum import Enum
from copy import deepcopy

ydl_opts = {
    'format': 'bestaudio/best',
    'extractaudio': True,
    'noplaylist': True,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

ffmpeg_opts = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

ydl_search_opts = {
    'format': 'bestaudio',
    'noplaylist':'True'
}

def yt_search(arg):
    with youtube_dl.YoutubeDL(ydl_search_opts) as ydl:
        try:
            requests.get(arg) 
        except Exception:
            video = ydl.extract_info(f"ytsearch:{arg}", download=False)['entries'][0]
        else:
            video = ydl.extract_info(arg, download=False)

    return video

class client:
    def __init__(self, auth_token):
        self.auth_token = auth_token
        self.bot = commands.Bot(command_prefix='!') #define command decorator
        self.guild_state_map = {}

        @self.bot.event
        async def on_ready():
            print(f'{self.bot.user.name} has connected to Discord!')
            # await bot.change_presence(game=Game(name="on standby ¬ !help"))


        @self.bot.command()
        async def join(ctx):
            if(ctx.author.voice):
                print('joining channel...')
                channel = ctx.author.voice.channel
                vc = await channel.connect()
                print('successfully joined channel!')
                vc.stop()
            else:
                await ctx.channel.send('Join a voice channel first!')
                        

        @self.bot.command()
        async def leave(ctx):
            await ctx.voice_client.disconnect()

        @self.bot.command()
        async def play(ctx, *, song: str):
            vc = ctx.voice_client
            if not vc:
                await ctx.channel.send('first use !join when in a voice channel')
                return

            if(vc.is_playing()):
                vc.stop();
            
            await ctx.channel.send(f'playing {song}')
            
            try:    
                song_info = yt_search(song)
                url = song_info['url']
                vc.play(discord.FFmpegPCMAudio(url, **ffmpeg_opts))
            except Exception:
                await ctx.channel.send('Could not find/play song!')

        
        @self.bot.command()
        async def pause(ctx):
            vc = ctx.voice_client
            if not vc:
                await ctx.send("Not in a voice channel. Use !join while in a voice channel")
                return

            if vc.is_playing():
                vc.pause()
            else:
                await ctx.send("Currently no audio is playing.")


        @self.bot.command()
        async def resume(ctx):
            vc = ctx.voice_client
            if not vc:
                await ctx.send("Not in a voice channel. Use !join while in a voice channel")
                return

            if vc.is_paused():
                vc.resume()
            else:
                await ctx.send("The audio is not paused.")


        @self.bot.command()
        async def stop(ctx):
            vc = ctx.voice_client
            if not vc:
                await ctx.send("Not in a voice channel. Use !join while in a voice channel")
                return
                
            vc.stop()


    def start(self):
        print('connecting...')
        self.bot.run(self.auth_token)
