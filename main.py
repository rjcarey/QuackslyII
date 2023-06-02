import discord
from discord.ext import commands, tasks
import discord.errors
from itertools import cycle
from flask import Flask
from threading import Thread
import os
from datetime import datetime, time

TOKEN = os.environ['DISCORD_TOKEN']
app = Flask('')


@app.route('/')
def main():
    t = str(datetime.now()).split('.')[0]
    with open('log.txt', 'a') as f:
        f.write(f"pinged at {t}\n")
    return "Your Bot Is Ready"


def run():
    app.run(host="0.0.0.0", port=8000)


def keep_alive():
    server = Thread(target=run)
    server.start()


bot = commands.Bot(command_prefix='/', intents=discord.Intents.all())
status = cycle(["with his disciples", "duck sim 2K22", "god", "duck, duck, goose", "the battle of polytopia", "with sacred scripture", "in holy water", "with rubber ducks", "king's choice", "with his latest sacrifices"])


@bot.event
async def on_ready():
    bot_tasks = [change_status, events, dragon, parade, hunting, pirates]
    for task in bot_tasks:
        task.start()
    print("up and running...")


@bot.command(name="snc", description="set channel as target for notifications")
async def snc(ctx):
    await ctx.send('set notification channel')


@bot.command(name="echo", description="echoes your message back to you")
async def echo(ctx, *, arg):
    await ctx.send(arg)


@bot.command(name="rr", description="add an emote reaction to a message to give role")
async def rr(ctx, *args):
    pass


@bot.command(name="test", description="temporary test functions")
async def test(ctx, arg: int):
    for channel in ctx.guild.channels:
        try:
            print(channel.name)
            msg = await channel.fetch_message(arg)
            await ctx.send(msg.content)
            return
        except discord.errors.NotFound:
            pass
        except AttributeError:
            pass
    await ctx.send("message not found")


@tasks.loop(seconds=60)
async def change_status():
    await bot.change_presence(activity=discord.Game(next(status)))


@tasks.loop(time=time(hour=8))
async def events():
    await bot.get_channel(1114176258469810237).send('events start')


@tasks.loop(time=time(hour=9))
async def dragon():
    await bot.get_channel(1114176258469810237).send('dragon island start')


@tasks.loop(time=time(hour=10))
async def parade():
    await bot.get_channel(1114176258469810237).send('parade start')


@tasks.loop(time=time(hour=10))
async def hunting():
    await bot.get_channel(1114176258469810237).send('hunting start')


@tasks.loop(time=time(hour=18))
async def pirates():
    await bot.get_channel(1114176258469810237).send('pirates start')

keep_alive()
bot.run(TOKEN)
