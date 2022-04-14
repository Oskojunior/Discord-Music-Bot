from webbrowser import get
import discord
from discord.ext import commands
from youtube_dl import YoutubeDL

music_queue = []
ydl_opts = {'format': 'bestaudio', 'noplaylist': 'True'}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}


class Counter:
    def __init__(self):
        self.count = 0
        self.outofindex = False

    def add_get(self):
        self.count += 1
        return self.count

    def get(self):
        return self.count

    def previous(self):
        self.count -= 2


fox = Counter()


def check_queue(ctx):
    if music_queue:
        if fox.count + 1 != len(music_queue):
            count = fox.add_get()
            voice = discord.utils.get(Player.music.voice_clients, guild=ctx.guild)
            url = music_queue[count]
            source = discord.FFmpegPCMAudio(url, **FFMPEG_OPTIONS)
            voice.play(source, after=lambda x=None: check_queue(ctx))
        elif not fox.outofindex:
            count = fox.get()
            voice = discord.utils.get(Player.music.voice_clients, guild=ctx.guild)
            url = music_queue[count]
            fox.outofindex = True
            source = discord.FFmpegPCMAudio(url, **FFMPEG_OPTIONS)
            voice.play(source, after=lambda x=None: check_queue(ctx))


def search(arg):
    with YoutubeDL(ydl_opts) as ydl:
        try:
            get(arg)
        except:
            video = ydl.extract_info(f"ytsearch:{arg}", download=False)['entries'][0]
        else:
            video = ydl.extract_info(arg, download=False)

    return video


class Player:
    music = commands.Bot(command_prefix=".")


@Player.music.command()
async def play(ctx, *args):
    voice = discord.utils.get(Player.music.voice_clients, guild=ctx.guild)
    video = search(args)
    url = video['formats'][0]['url']
    music_queue.append(url)
    if voice.is_playing():
        await ctx.send("Added to queue")
        fox.outofindex = False
    else:
        source = discord.FFmpegPCMAudio(url, **FFMPEG_OPTIONS)
        voice.play(source, after=lambda x=None: check_queue(ctx))
        fox.outofindex = True


@Player.music.command()
async def join(ctx):
    voiceChannel = discord.utils.get(ctx.guild.voice_channels, name='Ogólne')
    await voiceChannel.connect()


@Player.music.command()
async def leave(ctx):
    server = ctx.message.guild.voice_client
    await server.disconnect()


@Player.music.command()
async def pause(ctx):
    voice = discord.utils.get(Player.music.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
    else:
        await ctx.send("Currently no audio is playing.")


@Player.music.command()
async def resume(ctx):
    voice = discord.utils.get(Player.music.voice_clients, guild=ctx.guild)
    if voice.is_paused():
        voice.resume()
    else:
        await ctx.send("The audio is not paused.")


@Player.music.command()
async def stop(ctx):
    voice = discord.utils.get(Player.music.voice_clients, guild=ctx.guild)
    voice.stop()


@Player.music.command()
async def next(ctx):
    voice = discord.utils.get(Player.music.voice_clients, guild=ctx.guild)
    voice.stop()
    check_queue(ctx)


@Player.music.command()
async def previous(ctx):
    voice = discord.utils.get(Player.music.voice_clients, guild=ctx.guild)
    voice.stop()
    fox.previous()
    check_queue(ctx)


@Player.music.command()
async def clear(ctx):
    music_queue.clear()


@Player.music.command()
async def queue(ctx):
    await ctx.send(str(music_queue))


Player.music.run('token')
