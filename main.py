import discord
from discord.ext import commands, tasks
import discord.errors
from datetime import time, date
from time import time as t
import sqlite3
from qsconstants import TOKEN, AUTOROLE_CID, NOTIF_CID, LOG_CID, DATABASE, SCHEMAS, status, CHANGELOG
from keepalive import keep_alive
from random import randint, random
import pkg_resources
pkg_resources.require("googletrans==3.1.0a0")
import googletrans

###   BOT START   ###
translator = googletrans.Translator()
bot = commands.Bot(command_prefix='/', intents=discord.Intents.all(), help_command=None)
@bot.event
async def on_ready():
    bot_tasks = [change_status, events, dragon, parade_hunting_ball, pirates]
    for task in bot_tasks:
        task.start()
    print("up and running...")


###   FUNCTIONS   ###
def run_SQL(command, select):
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

def custom_command(channel, m_id, request):
    response, passed = run_SQL(f"SELECT request, response, image, paymin, paymax, cooldown, lastused, negresponse, bad FROM bot WHERE request = '{request}';", True)
    if passed and not response:
        response, passed = run_SQL(f"SELECT response, image FROM commands WHERE request = '{request}';", True)
        if passed and not response:
            await channel.send(f"i could not find that command ({request})")
        elif passed:
            if response[0][1] == 'T':
                await channel.send(file=discord.File(response[0][0]))
            else:
                await channel.send(response[0][0])
    elif passed:
        r_cmd, r_res, r_img, r_pmin, r_pmax, r_cd, r_lu, r_nr, r_bad = response[0]
        response, passed = run_SQL(f"SELECT money FROM members WHERE uid = '{m_id}';", True)
        if passed and not response:
            return await channel.send("you have not joined the ducknasty yet (/initiate)")
        elif passed:
            usetime = t()
            if usetime < r_cd + r_lu:
                await channel.send(r_nr)
            else:
                payout = randint(r_pmin, r_pmax) if r_bad == 'F' else -randint(r_pmin, r_pmax)
                response, passed = run_SQL(f"UPDATE members SET money = {int(response[0][0]) + payout} WHERE uid = '{m_id}';", False)
                if passed:
                    response, passed = run_SQL(f"UPDATE bot SET lastused = {usetime} WHERE request = '{r_cmd}';", False)
                    if passed:
                        if r_img == "T":
                            await channel.send(file=discord.File(r_res))
                        else:
                            await channel.send(r_res)
                        txt = f"Thank you! Here's a {payout} coin tip ^>^" if r_bad == 'F' else f"Hey! Here's a {payout * -1} coin fine t(-<-t)"
                        await channel.send(txt)
    if not passed:
        await channel.send(str(response))

def passover(guild, m_id, member):
    channel = await guild.fetch_channel(LOG_CID)
    response, passed = run_SQL(f"SELECT money, daily FROM members WHERE uid = '{m_id}';", True)
    if response and passed:
        if str(date.today()) != str(response[0][1]):
            response, passed = run_SQL(f"UPDATE members SET money = {int(response[0][0]) + 50}, daily = '{date.today()}' WHERE uid = '{m_id}';", False)
            if not passed:
                await channel.send(str(response))
            await channel.send(f"{member} claimed 50 daily coins")
    elif not passed:
        await channel.send(str(response))


###   COMMANDS   ###
@bot.command(name="snc", description="set channel as target for notifications", hidden=True)
async def snc(ctx):
    await ctx.send('set notification channel')

@bot.command(name="echo", description="echoes your message back to you")
async def echo(ctx, *, arg):
    await ctx.send(arg)

@bot.command(name="sql", description="admin command", hidden=True)
async def sql(ctx, *, arg):
    if not await bot.is_owner(ctx.author):
        await ctx.send("you do not have permission to use this command")
        return
    select = False
    if arg.split()[0].upper() == "SELECT":
        select = True
    response, passed = run_SQL(arg, select)
    if passed and not select:
        response = "SQL executed"
    await ctx.send(response)

@bot.command(name="rr", description="add an emote reaction to a message to give role", hidden=True)
async def rr(ctx, messageID, _, emote):
    channel = await ctx.guild.fetch_channel(AUTOROLE_CID)
    msg = await channel.fetch_message(messageID)
    response, passed = run_SQL(f"INSERT INTO reactionroles(m_id, emote, r_id) VALUES({messageID}, '{emote}', {ctx.message.role_mentions[0].id});", False)
    if not passed:
        await ctx.send(response)
        return
    await msg.add_reaction(emote)
    await ctx.send("reaction role added")

@bot.command(name="drr", description="delete a reaction role", hidden=True)
async def drr(ctx, messageID, emote):
    channel = await ctx.guild.fetch_channel(AUTOROLE_CID)
    msg = await channel.fetch_message(messageID)
    response, passed = run_SQL(f"DELETE FROM reactionroles WHERE m_id = {messageID} and emote = '{emote}';", False)
    if not passed:
        await ctx.send(response)
        return
    await msg.clear_reaction(emote)
    await ctx.send("reaction role deleted")

@bot.command(name="changelog", description="find out about Quacksly's latest changes")
async def changelog(ctx):
    ctx.send(CHANGELOG)

@bot.command(name="initiate", description="join the ducknasty or update info")
async def initiate(ctx):
    response, passed = run_SQL(f"SELECT * FROM members WHERE uid = '{ctx.author.id}';", True)
    if passed and not response:
        response, passed = run_SQL(f"INSERT INTO members VALUES ('{ctx.author.id}', '{ctx.author.name}', 100, '{date.today()}', 'T');", False)
        if passed:
            await ctx.send("welcome to the ducknasty")
    elif passed:
        if response[0][1] == ctx.author.name:
            await ctx.send("you have already been initialised")
        else:
            response, passed = run_SQL(f"UPDATE members SET username = '{ctx.author.name}' WHERE uid = '{ctx.author.id}';", False)
            if passed:
                await ctx.send("username updated")
    if not passed:
        await ctx.send(str(response))

@bot.command(name="?", description="list all possible commands")
async def commandList(ctx):
    cmdList = "commands:>"
    for command in bot.commands:
        if not command.hidden:
            cmdList += f"\n{command.name}"
    response, passed = run_SQL("SELECT request FROM commands;", True)
    if passed and response:
        for command in response:
            cmdList += f"\n{command[0]}"
        response, passed = run_SQL("SELECT request FROM bot;", True)
        if passed and response:
            for command in response:
                cmdList += f"\n{command[0]}"
    if passed:
        await ctx.send(cmdList)
    else:
        await ctx.send(str(response))

@bot.command(name="admincommands", description="display list of admin commands")
async def adminCommandList(ctx):
    cmdList = "commands:>"
    for command in bot.commands:
        if command.hidden:
            cmdList += f"\n{command.name}"
    await ctx.send(cmdList)

@bot.command(name="createtextcommand", description="create custom text-response commands")
async def createtextcommand(ctx, *, args):
    request = args.strip().split(' ', 1)
    command = request[0] if request[0][0] == "/" else "/" + request[0]
    response, passed = run_SQL(f'''INSERT INTO commands (request, response, creator, image) VALUES ('{command.lower()}', '{request[1]}', '{ctx.author.id}', 'F');''', False)
    if passed:
        await ctx.send(f"command created ({command.lower()})")
    else:
        await ctx.send(str(response))

@bot.command(name="createimagecommand", description="create custom text-response commands")
async def createimagecommand(ctx, *, args):
    request = args.strip().split()
    command = request[0] if request[0][0] == "/" else "/" + request[0]
    response, passed = run_SQL(f'''INSERT INTO commands (request, response, creator, image) VALUES ('{command.lower()}', '{request[1]}', '{ctx.author.id}', 'T');''', False)
    if passed:
        await ctx.send(f"command created ({command.lower()})")
    else:
        await ctx.send(str(response))

@bot.command(name="joke", description="receive or add joke")
async def joke(ctx, *args):
    if not args:
        response, passed = run_SQL("SELECT joke FROM jokes;", True)
        if passed:
            if not response:
                await ctx.send("there are no jokes yet")
            elif len(response) == 1:
                await ctx.send(response[0][0])
            else:
                await ctx.send(response[randint(0, len(response) - 1)][0])
    else:
        args = ' '.join(args)
        response, passed = run_SQL(f"INSERT INTO jokes(joke) VALUES ('{args}');", False)
        if passed:
            await ctx.send("joke added")
    if not passed:
        await ctx.send(response)

@bot.command(name="compliment", description="receive or add compliment")
async def compliment(ctx, *args):
    if not args:
        response, passed = run_SQL("SELECT compliment FROM compliments;", True)
        if passed:
            if not response:
                await ctx.send("there are no compliments yet")
            elif len(response) == 1:
                await ctx.send(response[0][0])
            else:
                await ctx.send(response[randint(0, len(response) - 1)][0])
        else:
            await ctx.send(response)
    else:
        args = ' '.join(args)
        response, passed = run_SQL(f"INSERT INTO compliments(compliment) VALUES ('{args}');", False)
        if passed:
            await ctx.send("compliment added")
    if not passed:
        await ctx.send(response)

@bot.command(name="cf", description="coinflip command")
async def coinflip(ctx, *args):
    passed, response = True, ""
    if not args:
        response, passed = run_SQL("SELECT name, bet, choice FROM cf;", True)
        if passed and response:
            msg = "CURRENT BETS:>"
            for record in response:
                msg += f"\n{record[0]} for {record[1]} coins on {record[2]};"
            await ctx.send(msg)
        elif passed:
            await ctx.send("there are currently no bets")
    else:
        if args[0] == "join":
            response, passed = run_SQL(f"SELECT uid, username, money FROM members WHERE uid = '{ctx.author.id}';", True)
            if passed and not response:
                await ctx.send("you have not joined the ducknasty yet (/initiate)")
            elif passed:
                j_uid, j_un, j_money = response[0]
                response, passed = run_SQL(f"SELECT creator, bet, choice FROM cf WHERE name = '{args[1]}';", True)
                if passed and not response:
                    await ctx.send(f"game not found ({args[1]})")
                elif passed:
                    uid, bet, choice = response[0][0], int(response[0][1]), response[0][2]
                    if bet <= int(j_money):
                        response, passed = run_SQL(f"UPDATE members SET money = {int(j_money) - bet} WHERE uid = '{ctx.author.id}';", False)
                        if passed:
                            flip = ["heads", "head", "h"] if random() < 0.5 else ["tails", "tail", "t"]
                            winner = uid if choice in flip else ctx.author.id
                            response, passed = run_SQL(f"SELECT uid, username, money FROM members WHERE uid = '{winner}';", True)
                            if passed:
                                win, currentMoney, name = int(bet * 2), int(response[0][2]), response[0][1]
                                response, passed = run_SQL(f"UPDATE members SET money = {currentMoney + win} WHERE uid = '{winner}';", False)
                                if passed:
                                    response, passed = run_SQL(f"DELETE FROM cf WHERE name = '{args[1]}';", False)
                                    if passed:
                                        await ctx.send(f"{flip[0]}, {name} wins {win} coins")
                    else:
                        await ctx.send("you do not have enough coins for this bet")
        elif args[0] == "cancel":
            if len(args) != 2:
                await ctx.send("incorrect syntax: /cf cancel name")
            else:
                response, passed = run_SQL(f"SELECT bet FROM cf WHERE name = '{args[1]}' AND creator = '{ctx.author.id}';", True)
                if passed and not response:
                    await ctx.send("no game found")
                elif passed:
                    bet = int(response[0])
                    response, passed = run_SQL(f"SELECT money FROM members WHERE uid = '{ctx.author.id}';", True)
                    if passed:
                        response, passed = run_SQL(f"UPDATE members SET money = {int(response[0][0]) + bet} WHERE uid = '{ctx.author.id}';", False)
                        if passed:
                            response, passed = run_SQL(f"DELETE FROM cf WHERE name = '{args[1]}' AND creator = '{ctx.author.id}';", False)
                            if passed:
                                await ctx.send("bet canceled")
        elif len(args) == 3:
            response, passed = run_SQL(f"SELECT name FROM cf WHERE name = '{args[0]}';", True)
            if passed and not response:
                response, passed = run_SQL(f"SELECT money FROM members WHERE uid = '{ctx.author.id}';", True)
                if passed and not response:
                    await ctx.send("you have not joined the ducknasty yet (/initiate)")
                elif passed:
                    if args[2] in ["heads", "head", "h", "tails", "tail", "t"]:
                        if int(response[0][0]) >= int(args[1]) >= 0:
                            response, passed = run_SQL(f"UPDATE members SET money = {int(response[0][0]) - int(args[1])} WHERE uid = '{ctx.author.id}';", False)
                            if passed:
                                response, passed = run_SQL(f"INSERT INTO cf VALUES ('{args[0]}', '{ctx.author.id}', '{args[1]}','{args[2]}');", False)
                                if passed:
                                    await ctx.send(f"betting {args[1]} coins on {args[2]}, to join type /cf join {args[0]}")
                        else:
                            await ctx.send("you do not have enough coins for this bet")
                    else:
                        await ctx.send("flip choice invalid choose 'heads' or 'tails'")
            elif passed:
                await ctx.send(f"game name taken ({args[0]})")
    if not passed:
        await ctx.send(str(response))

@bot.command(name="give", description="give coins to another user")
async def give(ctx, user: discord.Member, amount: int):
    response, passed = run_SQL(f"SELECT money FROM members WHERE uid = '{user.id}';", True)
    if passed and not response:
        await ctx.send("either they have not joined the ducknasty, or have since changed their username")
    elif passed:
        payee = response[0]
        response, passed = run_SQL(f"SELECT money FROM members WHERE uid = '{ctx.author.id}';", True)
        if passed and not response:
            await ctx.send("you have not joined the ducknasty yet (/initiate)")
        elif passed:
            payer = response[0]
            if amount <= 5:
                await ctx.send("you can give a minimum of 5 coins")
            elif amount > int(payer[0]):
                await ctx.send("you do not have enough coins to give this")
            else:
                response, passed = run_SQL(f"UPDATE members SET money = {int(payer[0]) - amount} WHERE uid = '{ctx.author.id}';", False)
                if passed:
                    response, passed = run_SQL(f"UPDATE members SET money = {int(payee[0]) + amount} WHERE uid = '{user.id}';", False)
                    if passed:
                        await ctx.send(f"{amount} coins transferred to {user.display_name}")
    if not passed:
        await ctx.send(str(response))

@bot.command(name="inject", description="add coins to user from void", hidden=True)
async def inject(ctx, user: discord.Member, amount: int):
    if not await bot.is_owner(ctx.author):
        await ctx.send("you do not have permission to use this command")
    response, passed = run_SQL(f"SELECT money FROM members WHERE uid = '{user.id}';", True)
    if passed and not response:
        await ctx.send("they have not joined the ducknasty (/initiate)")
    elif passed:
        response, passed = run_SQL(f"UPDATE members SET money = {int(response[0][0]) + amount} WHERE uid = '{user.id}';", False)
        if passed:
            await ctx.send(f"{amount} coins added to {user.display_name}")
    if not passed:
        await ctx.send(str(response))

@bot.command(name="bank", description="check how many coins you have")
async def bank(ctx, user: discord.Member = None):
    if user:
        response, passed = run_SQL(f"SELECT money FROM members WHERE uid = '{user.id}';", True)
        if passed and not response:
            await ctx.send(f"{user.display_name} has not joined the ducknasty yet (/initiate)")
        elif passed:
            await ctx.send(f"{user.display_name} has {response[0][0]} coins")
    else:
        response, passed = run_SQL(f"SELECT money FROM members WHERE uid = '{ctx.author.id}';", True)
        if passed and not response:
            await ctx.send("you have not joined the ducknasty yet or have change your name since (/initiate)")
        elif passed:
            await ctx.send(f"you have {response[0][0]} coins")
    if not passed:
        await ctx.send(str(response))

@bot.command(name="shop", description="view items in the shop or buy an item")
async def shop(ctx, item=None):
    if not item:
        response, passed = run_SQL("SELECT item, description, price FROM shop;", True)
        if passed and not response:
            await ctx.send("nothing in the shop")
        elif passed:
            txt = "item | description | price :>"
            for row in response:
                txt += f"\n{row[0]} | {row[1]} | {row[2]} coins"
            txt += "\n/shop [item name] to buy item"
            await ctx.send(txt)
    else:
        response, passed = run_SQL(f"SELECT uid, money, items FROM members WHERE uid = '{ctx.author.id}';", True)
        if passed and not response:
            await ctx.send("you haven't joined the ducknasty (/initiate)")
        elif passed:
            uid, money, items = response[0]
            response, passed = run_SQL(f"SELECT item, price FROM shop WHERE item = '{item}';", True)
            if passed and not response:
                await ctx.send(f"couldn't find item ({item})")
            elif passed and item in items:
                await ctx.send(f"you already have that item ({item})")
            elif passed:
                item, price = response[0]
                if int(price) > int(money):
                    await ctx.send(f"can't afford item ({price} coins)")
                else:
                    items += ' ' + item
                    response, passed = run_SQL(f"UPDATE members SET money = {int(money) - int(price)}, items = '{items.strip()}' WHERE uid = '{ctx.author.id}';", False)
                    if passed:
                        await ctx.send(f"{item} bought")
    if not passed:
        await ctx.send(str(response))

@bot.command(name="additem", description="add item to shop", hidden=True)
def addItem(ctx, *, args):
    if not await bot.is_owner(ctx.author):
        await ctx.send("you do not have permission to use this command")
    args = args.strip().split(' ', 1)
    response, passed = run_SQL(f"INSERT INTO shop (item, description, price) VALUES ('{args[0]}', '{args[1].rsplit(' ', 1)[0]}', {args[1].rsplit(' ', 1)[1]});", False)
    if passed:
        await ctx.send("item stocked")
    else:
        await ctx.send(str(response))

@bot.command(name="list", description="view all record of a table", hidden=True)
async def listTable(ctx, table):
    response, passed = run_SQL(f"SELECT * FROM {table};", True)
    if not passed:
        await ctx.send(str(response))
    else:
        msg = f"{table} contains:>"
        for record in response:
            msg += f"\n{record}"
        await ctx.send(msg)

@bot.command(name="negkick", description="check recent kicks or add a new one")
async def negKick(ctx, *, player=None):
    if not player:
        response, passed = run_SQL("SELECT kicker, lastkicked FROM neg;", True)
        if passed and not response:
            await ctx.send("no records in table")
        elif passed:
            msg = "negotiation kicks :>"
            for record in response:
                msg += f"\n{record[0]} last kicked us on {str(record[1])}"
            await ctx.send(msg)
    else:
        player = player.replace(' ', '')
        response, passed = run_SQL(f"SELECT kicker FROM neg WHERE kicker = '{player}';", True)
        if passed and not response:
            response, passed = run_SQL(f"INSERT INTO neg (kicker, lastkicked) VALUES ('{player}', '{date.today()}');", False)
            if passed:
                response, passed = run_SQL(f"UPDATE neg SET lastkicked = '{date.today()}' WHERE kicker = '{player}';", False)
                if passed:
                    await ctx.send(f"updated {player}'s last kick to {date.today()}")
    if not passed:
        await ctx.send(str(response))

@bot.command(name="ball", description="check or update ball habits")
async def ball(ctx, *args):
    response, passed = run_SQL(f"SELECT compliment, insult FROM ball WHERE username = '{args[0].lower()}';", True)
    if passed and len(args) == 1:
        if not response:
            await ctx.send(f"no record for {args[0].lower()}")
        else:
            await ctx.send(f"{args[0].lower()}'s record: {response[0][0]} compliments and {response[0][1]} insults")
    elif passed and len(args) == 3:
        if not response:
            response, passed = run_SQL(f"INSERT INTO ball (username, compliment, insult) VALUES ('{args[0].lower()}', {args[1]}, {args[2]});", False)
        else:
            response, passed = run_SQL(f"UPDATE ball SET compliment = {int(args[1]) + int(response[0][0])}, insult = {int(args[2]) + int(response[0][1])} WHERE username = '{args[0].lower()}';", False)
        if passed:
            await ctx.send(f"added {args[1]} compliment/s and {args[2]} insult/s to {args[0].lower()}")
    elif passed:
        await ctx.send("incorrect syntax; /ball [name] or /ball [name] [num compliments] [num insults]")
    if not passed:
        await ctx.send(str(response))

@bot.command(name="imagetest", description="test if an image link works")
async def imageTest(ctx, image):
    await ctx.send(file=discord.File(image))

@bot.command(name="reboot", description="reboot database table", hidden=True)
async def reboot(ctx, table):
    if not await bot.is_owner(ctx.author):
        await ctx.send("you do not have permission to use this command")
    response, passed = run_SQL(f"SELECT * FROM {table};", True)
    if passed:
        await ctx.send(str(response))
    response, passed = run_SQL(f"DROP TABLE IF EXISTS {table};", False)
    if not passed:
        await ctx.send(str(response))
    response, passed = run_SQL(SCHEMAS[table], False)
    if passed:
        await ctx.send(f"{table} table reset")
    else:
        await ctx.send(str(response))

@bot.command(name="reload", description="reload data into database table", hidden=True)
async def reload(ctx, *, args):
    if not await bot.is_owner(ctx.author):
        await ctx.send("you do not have permission to use this command")
    args = args.strip().split(" ", 1)
    response, passed = run_SQL(f'''INSERT INTO {args[0]} VALUES {args[1].strip('[]')};''', False)
    if not passed:
        await ctx.send(str(response))
    else:
        await ctx.send(f"values loaded into {args[0]}")


###   LISTENERS   ###
@bot.event
async def on_raw_reaction_add(reaction):
    if reaction.channel_id == AUTOROLE_CID:
        response, passed = run_SQL(f"SELECT r_id FROM reactionroles WHERE m_id = {reaction.message_id} AND emote = '{reaction.emoji}';", True)
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
        response, passed = run_SQL(f"SELECT r_id FROM reactionroles WHERE m_id = {reaction.message_id} AND emote = '{reaction.emoji}';", True)
        guild = bot.get_guild(reaction.guild_id)
        if passed:
            if response:
                role = discord.utils.get(guild.roles, id=int(response[0][0]))
                member = discord.utils.get(guild.members, id=reaction.user_id)
                await member.remove_roles(role)
        else:
            channel = await guild.fetch_channel(LOG_CID)
            await channel.send(str(response))

@bot.event
async def on_message(msg):
    if msg.content[0] == '/':
        if msg.content[1:3] in googletrans.LANGUAGES.keys():
            txt = f"{msg.author.name}: {translator.translate(msg.content[3:], dest=msg.content[1:3]).text}"
            await msg.channel.send(txt)
        else:
            custom_command(msg.channel, msg.author.id, msg.content)
    else:
        passover(msg.guild, msg.author.id, msg.author.name)


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
