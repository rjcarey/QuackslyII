import discord
from discord.ext import commands, tasks
import discord.errors
from itertools import cycle
from flask import Flask
from threading import Thread
import os
from datetime import datetime, time
import sqlite3

TOKEN = os.environ['DISCORD_TOKEN']
app = Flask('')
AUTOROLE_CID = 1114176147752755411
NOTIF_CID = 1114176258469810237
LOG_CID = 1114571677574103190
DATABASE = 'data.db'
SCHEMAS = {
    "reactionroles": "CREATE TABLE reactionroles (m_id INT NOT NULL, emote TEXT NOT NULL, r_id INT NOT NULL, PRIMARY KEY (m_id, emote));"
}

@app.route('/')
def main():
    t = str(datetime.now()).split('.')[0]
    with open('log.txt', 'a') as f:
        f.write(f"pinged at {t}\n")
    return "up and running..."

def run():
    app.run(host="0.0.0.0", port=8000)

def keep_alive():
    server = Thread(target=run)
    server.start()


bot = commands.Bot(command_prefix='/', intents=discord.Intents.all(), help_command=None)
status = cycle(["with his disciples", "duck sim 2K22", "god", "duck, duck, goose", "the battle of polytopia", "with sacred scripture", "in holy water", "with rubber ducks", "king's choice", "with his latest sacrifices"])


@bot.event
async def on_ready():
    bot_tasks = [change_status, events, dragon, parade_hunting_ball, pirates]
    for task in bot_tasks:
        task.start()
    print("up and running...")

@bot.command(name="snc", description="set channel as target for notifications")
async def snc(ctx):
    await ctx.send('set notification channel')

@bot.command(name="echo", description="echoes your message back to you")
async def echo(ctx, *, arg):
    await ctx.send(arg)

@bot.command(name="sql", description="admin command")
async def sql(ctx, *, arg):
    if not await bot.is_owner(ctx.author):
        await ctx.send("you do not have permission to use this command")
        return
    select = False
    if arg.split()[0].upper() == "SELECT":
        select = True
    response, passed = runSQL(arg, select)
    if passed and not select:
        response = "SQL executed"
    await ctx.send(response)

def runSQL(command, select):
    res, p, con, cur = False, True, None, None
    try:
        con = sqlite3.connect(DATABASE)
        cur = con.cursor()
        cur.execute(command)
        if select:
            res = cur.fetchall()
        else:
            con.commit()
    except sqlite3.Error as e:
        res = e
        p = False
    finally:
        if con:
            cur.close()
            con.close()
    return res, p

@bot.command(name="rr", description="add an emote reaction to a message to give role")
async def rr(ctx, messageID, _, emote):
    channel = await ctx.guild.fetch_channel(AUTOROLE_CID)
    msg = await channel.fetch_message(messageID)
    response, passed = runSQL(f"INSERT INTO reactionroles(m_id, emote, r_id) VALUES({messageID}, '{emote}', {ctx.message.role_mentions[0].id});", False)
    if not passed:
        await ctx.send(response)
        return
    await msg.add_reaction(emote)
    await ctx.send("reaction role added")

@bot.command(name="drr", description="delete a reaction role")
async def drr(ctx, messageID, emote):
    channel = await ctx.guild.fetch_channel(AUTOROLE_CID)
    msg = await channel.fetch_message(messageID)
    response, passed = runSQL(f"DELETE FROM reactionroles WHERE m_id = {messageID} and emote = '{emote}';", False)
    if not passed:
        await ctx.send(response)
        return
    await msg.clear_reaction(emote)
    await ctx.send("reaction role deleted")

@bot.event
async def on_raw_reaction_add(reaction):
    if reaction.channel_id == AUTOROLE_CID:
        response, passed = runSQL(f"SELECT r_id FROM reactionroles WHERE m_id = {reaction.message_id} AND emote = '{reaction.emoji}';", True)
        guild = bot.get_guild(reaction.guild_id)
        if passed:
            role = discord.utils.get(guild.roles, id=int(response[0][0]))
            member = discord.utils.get(guild.members, id=reaction.user_id)
            await member.add_roles(role)
        else:
            channel = await guild.fetch_channel(LOG_CID)
            await channel.send(str(response))

@bot.event
async def on_raw_reaction_remove(reaction):
    if reaction.channel_id == AUTOROLE_CID:
        response, passed = runSQL(f"SELECT r_id FROM reactionroles WHERE m_id = {reaction.message_id} AND emote = '{reaction.emoji}';", True)
        guild = bot.get_guild(reaction.guild_id)
        if passed:
            role = discord.utils.get(guild.roles, id=int(response[0][0]))
            member = discord.utils.get(guild.members, id=reaction.user_id)
            # member = reaction.member if reaction.event_type == 'REACTION_ADD' else member_from_reaction_remove(guild, reaction.message_id, reaction.emoji, role)
            await member.remove_roles(role)
        else:
            channel = await guild.fetch_channel(LOG_CID)
            await channel.send(str(response))

@bot.command(name="test", description="temporary test functions")
async def test(ctx, arg: int):
    channel = await ctx.guild.fetch_channel(AUTOROLE_CID)
    msg = await channel.fetch_message(arg)
    await ctx.send(msg.content)

@tasks.loop(seconds=60)
async def change_status():
    await bot.change_presence(activity=discord.Game(next(status)))

@tasks.loop(time=time(hour=8))
async def events():
    await bot.get_channel(NOTIF_CID).send("🔴🎭 hear ye, hear ye, events hath commenced 🎭🔴 <@&1114526611556012082>")

@tasks.loop(time=time(hour=9))
async def dragon():
    await bot.get_channel(NOTIF_CID).send("🔴🐲 rawr, beware, dragons have returned to their islands 🐲🔴 <@&1114526867895091301>")

@tasks.loop(time=time(hour=10))
async def parade_hunting_ball():
    await bot.get_channel(NOTIF_CID).send("🔴🎪 *ridiculous trumpet solos*, the parades have started, *marching band marches by* 🎪🔴 <@&1114527261077544960>")
    await bot.get_channel(NOTIF_CID).send("🔴🔫 grab your ghillie suits, hunting trips are departing 🔫🔴 <@&1114527669598568530>")
    await bot.get_channel(NOTIF_CID).send("🔴💃 don your dancing shoes, the ball has started 💃🔴 <@&1114554773048406047>")

@tasks.loop(time=time(hour=18))
async def pirates():
    await bot.get_channel(NOTIF_CID).send("🔴🏴‍☠️ Yarrr… there’re scallywags ashore ye land lubbers! 🏴‍☠️🔴 <@&1114525168904187934>")

keep_alive()
bot.run(TOKEN)
