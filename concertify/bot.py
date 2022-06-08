from grabber import Grabber as _Grabber
import utils as _utils

import os as _os
from dotenv import load_dotenv as _load_dotenv
from fuzzysearch import find_near_matches as _find_near_matches
import discord as _discord
from discord.ext import commands as _commands

bot = _commands.Bot(command_prefix=">")
_load_dotenv()
DISCORD_TOKEN = _os.environ['DISCORD_TOKEN']

@bot.command()
async def demo(ctx):
    demo_path = _os.path.join(_os.getcwd(), "demo.mp3")
    assert _os.path.isfile(demo_path)
    vc = _discord.utils.get(ctx.guild.voice_channels, name='General')
    await vc.connect()
    voice = _discord.utils.get(bot.voice_clients, guild=ctx.guild)
    voice.play(_discord.FFmpegOpusAudio(demo_path))
    
@bot.command()
async def dc(ctx):
    voice = _discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice is not None:
        if voice.is_connected():
            await voice.disconnect()
        else:
            await ctx.send('The bot isnt connected to the voice channel')
    else:
        await ctx.send('The bot already isnt connected to the voice channel')

@bot.command()
async def pause(ctx):
    voice = _discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
    else:
        await ctx.send("it's already paused bruh")

@bot.command()
async def resume(ctx):
    voice = _discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_paused():
        voice.resume()
    else:
        await ctx.send("it's already resumed... are u deaf")
        
@bot.command()
async def token(ctx, token: str):
    grabber.set_token(token)
    await ctx.send("Set token; this better work...")
    
@bot.command()
async def clear(ctx):
    grabber.clear_cache()
    await ctx.send("Cleared the cache.")
    
@bot.command()
async def concert(ctx, track_url: str):
    
    # TODO: add command to change download link?
    MP3_LOC = grabber.PATH + '.mp3'
    
    status_code, lrc_json, info = grabber.get_lrc_json(track_url)
    assert status_code == 200
    # assert grabber.download(track_url) == info
    grabber.download(track_url)
    audio_generator = grabber.audio_generator(lrc_json, info)
    
    vc = _discord.utils.get(ctx.guild.voice_channels, name='General')
    await vc.connect()
    voice = _discord.utils.get(bot.voice_clients, guild=ctx.guild)
    
    next(audio_generator).export(MP3_LOC, 'mp3')
    if voice.is_playing():
        voice.stop()
    voice.play(_discord.FFmpegOpusAudio(MP3_LOC))
    
    history = ['Concert over!']
    
    for line in lrc_json['lyrics']['lines']:
        
        correct = _utils.simplify(line['words'])
        if correct == '':
            continue
        
        msg = await bot.wait_for("message")
        while len(_find_near_matches(correct, (guess := _utils.simplify(msg.content)), max_l_dist=_utils.MAX_TYPOS)) == 0:
            await ctx.send(f"{msg.author.mention} {msg.content} is incorrect!")
            msg = await bot.wait_for("message")
        history.append(msg.author.mention + " " + msg.content)

        next(audio_generator).export(MP3_LOC, 'mp3')
        if voice.is_playing():
            voice.stop()
        voice.play(_discord.FFmpegOpusAudio(MP3_LOC))
        
    await ctx.send('\n'.join(history))

grabber = _Grabber()
bot.run(DISCORD_TOKEN)
