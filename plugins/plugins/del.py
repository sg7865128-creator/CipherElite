# =============================================================================
# CipherElite Userbot Plugin
#
# Plugin Name: del
# Description: Silently delete your own messages
# Author: CipherElite
# =============================================================================

import asyncio
from telethon import events
from telethon.errors import FloodWaitError

from plugins.bot import add_handler
from utils.utils import CipherElite
from utils.decorators import rishabh


VERSION = "1.0"
CATEGORY = "utilities"


def init(client_instance):
    """Register plugin in the Help Menu."""
    add_handler(
        "del",
        [".del"],
        "Silently delete all your own messages in the current chat."
    )


async def delete_own_messages(event):
    client = event.client
    chat = await event.get_input_chat()
    me = await client.get_me()

    message_ids = []

    # Collect all messages sent by the current account.
    async for message in client.iter_messages(chat):
        if message.sender_id == me.id:
            message_ids.append(message.id)

    # Delete in batches.
    deleted = 0

    for i in range(0, len(message_ids), 100):
        batch = message_ids[i:i + 100]

        while True:
            try:
                await client.delete_messages(
                    chat,
                    batch,
                    revoke=True
                )
                deleted += len(batch)
                break

            except FloodWaitError as e:
                await asyncio.sleep(e.seconds)

            except Exception as e:
                # Retry individually if a batch fails.
                for msg_id in batch:
                    try:
                        await client.delete_messages(
                            chat,
                            [msg_id],
                            revoke=True
                        )
                        deleted += 1

                    except FloodWaitError as wait:
                        await asyncio.sleep(wait.seconds)

                        try:
                            await client.delete_messages(
                                chat,
                                [msg_id],
                                revoke=True
                            )
                            deleted += 1
                        except Exception:
                            pass

                    except Exception:
                        pass

                break

    return deleted


async def register_commands():
    """Register Telethon command handler."""

    @CipherElite.on(events.NewMessage(pattern=r"^\.del$"))
    @rishabh
    async def del_command(event):
        try:
            await delete_own_messages(event)

        except Exception as e:
            # Keep the command silent.
            print(f"[DEL] Error: {e}")
