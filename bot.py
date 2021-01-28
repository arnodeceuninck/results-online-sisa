from config import discord_token
from discord.ext import commands
from main import main as results_online

bot = commands.Bot(command_prefix="-", description="Check wether results are online")


@bot.event
async def on_ready():
    print("Ready!")


@bot.command()
async def sisa(ctx):
    if results_online(check=False, post=False):
        await ctx.message.reply("De punten staan online")
    else:
        await ctx.message.reply("De punten staan nog niet online")


bot.run(discord_token)
