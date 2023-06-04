import discord
from discord.ext import commands, tasks
import discord.errors
from datetime import time
import sqlite3
from qsconstants import TOKEN, AUTOROLE_CID, NOTIF_CID, LOG_CID, DATABASE, SCHEMAS, status
from keepalive import keep_alive

###   BOT START   ###
bot = commands.Bot(command_prefix='/', intents=discord.Intents.all(), help_command=None)
@bot.event
async def on_ready():
    bot_tasks = [change_status, events, dragon, parade_hunting_ball, pirates]
    for task in bot_tasks:
        task.start()
    print("up and running...")


###   FUNCTIONS   ###
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


###   COMMANDS   ###
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

@bot.command(name="test", description="temporary test functions")
async def test(ctx, arg: int):
    channel = await ctx.guild.fetch_channel(AUTOROLE_CID)
    msg = await channel.fetch_message(arg)
    await ctx.send(msg.content)


###   LISTENERS   ###
@bot.event
async def on_raw_reaction_add(reaction):
    if reaction.channel_id == AUTOROLE_CID:
        response, passed = runSQL(f"SELECT r_id FROM reactionroles WHERE m_id = {reaction.message_id} AND emote = '{reaction.emoji}';", True)
        guild = bot.get_guild(reaction.guild_id)
        if passed:
            if response:
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
            if response:
                role = discord.utils.get(guild.roles, id=int(response[0][0]))
                member = discord.utils.get(guild.members, id=reaction.user_id)
                await member.remove_roles(role)
        else:
            channel = await guild.fetch_channel(LOG_CID)
            await channel.send(str(response))


###   LOOPS   ###
@tasks.loop(seconds=60)
async def change_status():
    await bot.change_presence(activity=discord.Game(next(status)))


###   ALARMS   ###
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


###   RUN K-A SERVER AND BOT   ###
keep_alive()
bot.run(TOKEN)
