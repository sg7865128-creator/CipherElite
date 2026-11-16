
from telethon import events
from telethon.errors import FloodWaitError
from plugins.bot import add_handler
from utils.decorators import rishabh

VERSION = "1.0"
CATEGORY = "utilities"


def init(client_instance):
    add_handler(
        "del",
        [".del"],
        "Delete your own messages from the current chat."
    )
