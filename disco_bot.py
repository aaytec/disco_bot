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
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
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


class state(Enum):
    SERVER_STANDBY = 0,
    VC_STANDBY = 1,
    VC_PLAYING = 2

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

            if(ctx.guild.id not in self.guild_state_map):
                self.guild_state_map[ctx.guild.id] = state.SERVER_STANDBY;

            guild_state = self.guild_state_map[ctx.guild.id]
            
            if(guild_state == state.SERVER_STANDBY):
                if(ctx.author.voice):
                    print('joining channel...')
                    channel = ctx.author.voice.channel
                    vc = await channel.connect()
                    print('successfully joined channel!')
                    vc.stop()
                    self.guild_state_map[ctx.guild.id] = state.VC_STANDBY;
                else:
                    await ctx.channel.send('Join a voice channel first!')

            elif(guild_state == state.VC_STANDBY):
                await ctx.channel.send('I am already part of a voice channel. Use !leave and then !join in the channel you want me to be in')

            elif(guild_state == state.VC_PLAYING):
                await ctx.channel.send('I am current playing a song. Please stop it or use !leave')
                

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

            song_file = f'{ctx.guild.id}-song.mp3'
            song_there = os.path.isfile(song_file)
            ydl_opts_guild = deepcopy(ydl_opts)
            ydl_opts_guild['outtmpl'] = song_file

            try:
                if song_there:
                    print(f'file {song_file} already exisits, removing')
                    os.remove(song_file)
            except PermissionError:
                return
            
            try:
                video_id = yt_search(song)['id']
                with youtube_dl.YoutubeDL(ydl_opts_guild) as ydl:
                    url = f'https://www.youtube.com/watch?v={video_id}'
                    print(f'downloading {url}')
                    ydl.download([url])

                vc.play(discord.FFmpegPCMAudio(song_file))
            except Exception:
                await ctx.channel.send('Could not find song!')

        
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
