import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='$')

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.command()
async def greet(ctx):
    await ctx.send(":smiley: :wave: Hello, there!")

bot.run('NDYxODA1MDE2NTU0OTMwMTkx.DhYo9Q.k58KKLIrUZGkuwxodg7v-CLOGLs')
