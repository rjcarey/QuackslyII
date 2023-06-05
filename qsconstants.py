from os import environ
from itertools import cycle

AUTOROLE_CID = 1114176147752755411
NOTIF_CID = 1114176258469810237
LOG_CID = 1114571677574103190
TOKEN = environ['DISCORD_TOKEN']
DATABASE = 'data.db'

CHANGELOG = "QuackslyII 1.0: new and improved quacksly has moved to discord, and with his move comes much more functionality to be seen soon..."

status = cycle(["with his disciples", "duck sim 2K22", "god", "duck, duck, goose", "the battle of polytopia", "with sacred scripture", "in holy water", "with rubber ducks", "king's choice", "with his latest sacrifices"])

SCHEMAS = {
    "reactionroles": "CREATE TABLE reactionroles (m_id INTEGER NOT NULL, emote TEXT NOT NULL, r_id INTEGER NOT NULL, PRIMARY KEY (m_id, emote));",
    "members": "CREATE TABLE members (uid TEXT PRIMARY KEY NOT NULL UNIQUE, username TEXT NOT NULL UNIQUE, money INTEGER NOT NULL, daily TEXT, notifs TEXT, items TEXT);",
    "ball": "CREATE TABLE ball (username TEXT PRIMARY KEY NOT NULL UNIQUE, compliment INTEGER, insult INTEGER);",
    "commands": "CREATE TABLE commands (request	TEXT PRIMARY KEY NOT NULL UNIQUE, response TEXT NOT NULL, creator TEXT NOT NULL, image TEXT);",
    "jokes": "CREATE TABLE jokes (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, joke TEXT NOT NULL);",
    "compliments": "CREATE TABLE compliments (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE, compliment TEXT NOT NULL);",
    "cf": "CREATE TABLE cf (name TEXT PRIMARY KEY NOT NULL UNIQUE, creator TEXT NOT NULL, bet TEXT NOT NULL, choice TEXT NOT NULL);",
    "neg": "CREATE TABLE neg (kicker TEXT PRIMARY KEY NOT NULL UNIQUE, lastkicked TEXT NOT NULL);",
    "bot": "CREATE TABLE bot (request TEXT PRIMARY KEY NOT NULL UNIQUE, response TEXT, image TEXT, paymin INTEGER, paymax INTEGER, cooldown INTEGER, lastused INTEGER, negresponse TEXT, bad TEXT);",
    "shop": "CREATE TABLE shop (item TEXT PRIMARY KEY NOT NULL UNIQUE, description TEXT, price INTEGER);"
}
