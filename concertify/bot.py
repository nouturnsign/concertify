from grabber import Grabber as _Grabber
import utils as _utils

import os
from dotenv import load_dotenv
from fuzzysearch import find_near_matches as _find_near_matches
import discord
from discord.ext import commands

bot = commands.Bot(command_prefix=">")
load_dotenv()
DISCORD_TOKEN = os.environ['DISCORD_TOKEN']

@bot.command()
async def play(ctx):
    songfile = os.path.isfile("song.mp3")
##    try:
##      put something here later
##        if song_there:
##            os.remove("song.mp3")
##    except PermissionError:
##        await ctx.send("wait for this shit to finish or use a stop command to pussy out :)")
    
    vc = discord.utils.get(ctx.guild.voice_channels, name = 'General')
    await vc.connect()
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    voice.play(discord.FFmpegOpusAudio("song.mp3"))
    
@bot.command()
async def dc(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice:
        if voice.is_connected():
            await voice.disconnect()
        else:
            await ctx.send('the bot already isnt connected to the voice channel, u retard')
    else:
        await ctx.send('the bot already isnt connected to the voice channel, u retard')

@bot.command()
async def pause(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
    else:
        await ctx.send("it's already paused bruh")

@bot.command()
async def resume(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
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
    assert grabber.download(track_url) == info
    audio_generator = grabber.audio_generator(lrc_json, info)
    
    vc = discord.utils.get(ctx.guild.voice_channels, name = 'General')
    await vc.connect()
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    
    next(audio_generator).export(MP3_LOC, 'mp3')
    if voice.is_playing():
        voice.stop()
    voice.play(discord.FFmpegOpusAudio(MP3_LOC))
    
    history = ['Concert over!']
    
    for line in lrc_json['lyrics']['lines']:
        
        correct = _utils.simplify(line['words'])
        if correct == '':
            continue
        
        msg = await bot.wait_for("message")
        while len(_find_near_matches(correct, (line := _utils.simplify(msg.content)), max_l_dist=_utils.MAX_TYPOS)) == 0:
            await ctx.send(msg.author.mention + " " + msg.content + " is incorrect!\n" + correct)
            msg = await bot.wait_for("message")
        history.append(msg.author.mention + " " + msg.content)

        next(audio_generator).export(MP3_LOC, 'mp3')
        if voice.is_playing():
            voice.stop()
        voice.play(discord.FFmpegOpusAudio(MP3_LOC))
        
    await ctx.send('\n'.join(history))

grabber = _Grabber()
bot.run(DISCORD_TOKEN)
