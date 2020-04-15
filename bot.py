import discord, chalk
from discord.ext import commands
import time
import asyncio

from opus_loader import load_opus_lib

token = os.environ['DISCORD_TOKEN']
bot = commands.Bot(command_prefix = "!")

@bot.event
async def on_ready():
    print("Bot is ready!")

@bot.command()
async def q5(ctx):
    await ctx.send("@here QUEUE STARTING IN 5 MINUTES")

@bot.command()
async def q3(ctx):
    await ctx.send("@here QUEUE STARTING IN 3 MINUTES")

@bot.command()
async def q1(ctx):
    await ctx.send("@here QUEUE STARTING IN 1 MINUTES")

@bot.command()
async def ping(ctx):
    ping_ = bot.latency
    ping =  round(ping_ * 1000)
    await ctx.send(f"my ping is {ping}ms")

@bot.command()
async def startq(ctx):
    channel = discord.utils.get(ctx.guild.channels, name='queue')
    vc = await channel.connect()
    vc.play(discord.FFmpegPCMAudio("countdown.mp3"), after=lambda e: print('done', e))
    bot.run(token)

@bot.command(aliases=['paly', 'queue', 'que'])
async def play(ctx):
    guild = ctx.guild
    voice_client: discord.VoiceClient = discord.utils.get(bot.voice_clients, guild=guild)
    audio_source = discord.FFmpegPCMAudio('vuvuzela.mp3')
    if not voice_client.is_playing():
        voice_client.play(audio_source, after=None)