from os import environ
from itertools import cycle

AUTOROLE_CID = 1114176147752755411
NOTIF_CID = 1114176258469810237
LOG_CID = 1114571677574103190
TOKEN = environ['DISCORD_TOKEN']
DATABASE = 'data.db'

status = cycle(["with his disciples", "duck sim 2K22", "god", "duck, duck, goose", "the battle of polytopia", "with sacred scripture", "in holy water", "with rubber ducks", "king's choice", "with his latest sacrifices"])

SCHEMAS = {
    "reactionroles": "CREATE TABLE reactionroles (m_id INT NOT NULL, emote TEXT NOT NULL, r_id INT NOT NULL, PRIMARY KEY (m_id, emote));"
}
