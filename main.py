import discord
from discord.ext import commands, tasks
from itertools import cycle
from flask import Flask
from threading import Thread
import os
from datetime import datetime, time

TOKEN = os.environ['DISCORD_TOKEN']
app = Flask('')
announce = time(hour=12, minute=4)


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
    change_status.start()
    print("up and running...")


@tasks.loop(seconds=60)
async def change_status():
    await bot.change_presence(activity=discord.Game(next(status)))


@tasks.loop(time=announce)
async def announcement():
    print('pass')


keep_alive()
bot.run(TOKEN)
