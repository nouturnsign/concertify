from dotenv import load_dotenv
import discord
from discord.ext import commands
import os

bot = commands.Bot(command_prefix=">")
load_dotenv()
token = os.environ['DISCORD_TOKEN']

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
    voice.play(discord.FFmpegPCMAudio("song.mp3"))
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

bot.run(token)