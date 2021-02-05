from config import discord_token
from discord.ext import commands
from main import main as results_online, get_logged_time, get_last_message, get_average, get_onderscheiding
from threadWithRetrun import ThreadWithReturn

from threading import Thread
from time import sleep

bot = commands.Bot(command_prefix="-", description="Check wether results are online")


@bot.event
async def on_ready():
    print("Ready!")


@bot.command()
async def sisb(ctx, mode=None):
    if mode not in ("check", "test", "run", "avg"):
        return await ctx.message.reply(f"Parameter 'run', 'check' or 'test' must be provided.")

    if mode == "avg":
        message = await  ctx.message.reply("Loading average, this will take a long time...")
        avg = get_average()
        onderscheiding = get_onderscheiding(avg)
        return await message.edit(content=f"Je hebt {onderscheiding} met een gewogen gemiddelde van {avg} op 20")

    if mode == "check":
        return await ctx.message.reply(f"Last automatic check was at {get_logged_time()}")

    test = mode == "test"
    message = await ctx.message.reply("Checking Sisa... (this might take a while)")
    try:
        thread = ThreadWithReturn(target=results_online, kwargs=dict(manually=True, test=test))
        thread.start()
        while thread.is_alive():
            last_message = get_last_message()
            if message.content != last_message:
                await message.edit(content=last_message)
            sleep(2)
        text = thread.join()
        # text = results_online(manually=True, test=test)
        await message.edit(content=text)
    except Exception as e:
        await message.edit("Error")
        raise e


@bot.command()
async def sping(ctx):
    await ctx.message.reply("pong")


bot.run(discord_token)
