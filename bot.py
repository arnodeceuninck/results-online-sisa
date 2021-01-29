from config import discord_token
from discord.ext import commands
from main import main as results_online

bot = commands.Bot(command_prefix="-", description="Check wether results are online")


@bot.event
async def on_ready():
    print("Ready!")


@bot.command()
async def sisa(ctx):
    message = await ctx.message.reply("Checking Sisa... (this might take a while)")
    try:
        if results_online(check=False, post=False):
            await message.edit(content="De punten staan online")
        else:
            await message.edit(content="De punten staan nog niet online")
    except Exception as e:
        await message.edit("Error")
        raise e


@bot.command()
async def sping(ctx):
    await ctx.message.reply("pong")


bot.run(discord_token)
