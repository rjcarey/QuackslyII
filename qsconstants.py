from os import environ
from itertools import cycle

AUTOROLE_CID = 1114176147752755411
NOTIF_CID = 1114176258469810237
LOG_CID = 1114571677574103190
TOKEN = environ['DISCORD_TOKEN']
DATABASE = 'data.db'

CHANGELOG = "QuackslyII 1.1: reformatting under the hood"

status = cycle(["with his disciples", "duck sim 2K22", "god", "duck, duck, goose", "the battle of polytopia", "with sacred scripture", "in holy water", "with rubber ducks", "king's choice", "with his latest sacrifices"])

SCHEMAS = {
    "reactionroles": "CREATE TABLE reactionroles (msg_id INTEGER NOT NULL, emote TEXT NOT NULL, r_id INTEGER NOT NULL, PRIMARY KEY (m_id, emote));",
    "members": "CREATE TABLE members (m_id INTEGER PRIMARY KEY NOT NULL UNIQUE, money INTEGER NOT NULL, daily TEXT, items TEXT);",
    "ball": "CREATE TABLE ball (username TEXT PRIMARY KEY NOT NULL UNIQUE, compliment INTEGER, insult INTEGER);",
    "commands": "CREATE TABLE commands (request	TEXT PRIMARY KEY NOT NULL UNIQUE, response TEXT NOT NULL, creator_id INTEGER NOT NULL, image TEXT);",
    "jokes": "CREATE TABLE jokes (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, joke TEXT NOT NULL);",
    "compliments": "CREATE TABLE compliments (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE, compliment TEXT NOT NULL);",
    "cf": "CREATE TABLE cf (name TEXT PRIMARY KEY NOT NULL UNIQUE, creator_id INTEGER NOT NULL, bet TEXT NOT NULL, choice TEXT NOT NULL);",
    "neg": "CREATE TABLE neg (kicker TEXT PRIMARY KEY NOT NULL UNIQUE, lastkicked TEXT NOT NULL);",
    "bot": "CREATE TABLE bot (request TEXT PRIMARY KEY NOT NULL UNIQUE, response TEXT, image TEXT, paymin INTEGER, paymax INTEGER, cooldown INTEGER, lastused INTEGER, negresponse TEXT, bad TEXT);",
    "shop": "CREATE TABLE shop (item TEXT PRIMARY KEY NOT NULL UNIQUE, description TEXT, price INTEGER);",
    "typos": "CREATE TABLE typos (intent TEXT PRIMARY KEY NOT NULL, typo TEXT NOT NULL);"
}
