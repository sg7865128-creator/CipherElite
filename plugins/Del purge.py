from telethon import events
from plugins.bot import add_handler
from utils.utils import CipherElite
from utils.decorators import rishabh

VERSION = "1.0.0"
CATEGORY = "moderation"


def init(client_instance):
    commands = [
        ".purge - Delete your own messages"
    ]
    description = "Delete your own messages from a group."
    add_handler("purge", commands, description)


async def register_commands():

    @CipherElite.on(events.NewMessage(pattern=r"\.purge$"))
    @rishabh()
    async def purge(event):

        if not event.is_group:
            await event.reply("❌ This command only works in groups.")
            return

        await event.reply(
            "⚠️ Purge command detected!\n"
            "Only your own messages will be targeted."
        )
