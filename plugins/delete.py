from telethon import events
from telethon.errors import FloodWaitError
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

VERSION = "1.0.0"
CATEGORY = "utilities"


def init(client_instance):
    commands = [
        ".del - Delete your own messages from the current chat"
    ]
    description = "Delete your own messages from the current chat"
    add_handler("del", commands, description)


async def register_commands():
    pass
