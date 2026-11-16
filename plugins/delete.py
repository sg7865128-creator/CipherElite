import asyncio
from telethon import events
from telethon.errors import FloodWaitError

from utils.utils import CipherElite
from utils.decorators import is_owner_or_sudo
from plugins.bot import add_handler


VERSION = "1.0.0"
CATEGORY = "utilities"


def init(client_instance):
    commands = [
        ".del - Delete your own messages from current chat"
    ]

    description = "Delete your own messages from the current chat"
    add_handler("del", commands, description)


async def register_commands():

    @CipherElite.on(events.NewMessage(
    pattern=r"^\.del$"
))
    async def delete_messages(event):

        # Owner and Sudo authorization
        if not await is_owner_or_sudo(event):
            return

        chat_id = event.chat_id
        sender_id = event.sender_id

        deleted_count = 0
        failed_count = 0
        batch = []

        async def delete_batch(message_ids):

            nonlocal deleted_count, failed_count

            try:
                await event.client.delete_messages(
                    chat_id,
                    message_ids
                )

                deleted_count += len(message_ids)

            except FloodWaitError as error:

                await asyncio.sleep(error.seconds)

                try:
                    await event.client.delete_messages(
                        chat_id,
                        message_ids
                    )

                    deleted_count += len(message_ids)

                except Exception as e:
                    failed_count += len(message_ids)
                    print(f"Del retry error: {e}")

            except Exception:

                # Try messages individually if batch fails
                for message_id in message_ids:

                    try:
                        await event.client.delete_messages(
                            chat_id,
                            message_id
                        )

                        deleted_count += 1

                    except FloodWaitError as error:

                        await asyncio.sleep(error.seconds)

                        try:
                            await event.client.delete_messages(
                                chat_id,
                                message_id
                            )

                            deleted_count += 1

                        except Exception as e:
                            failed_count += 1
                            print(f"Del error: {e}")

                    except Exception as e:
                        failed_count += 1
                        print(f"Del error: {e}")

        try:

            # Scan current chat history
            async for message in event.client.iter_messages(chat_id):

                # Only messages sent by command user
                if message.sender_id != sender_id:
                    continue

                batch.append(message.id)

                # Delete in batches
                if len(batch) >= 100:

                    await delete_batch(batch)
                    batch = []

            # Delete remaining messages
            if batch:
                await delete_batch(batch)

            print(
                f"Del completed | Chat: {chat_id} | "
                f"User: {sender_id} | "
                f"Deleted: {deleted_count} | "
                f"Failed: {failed_count}"
            )

        except Exception as e:
            print(f"Del plugin error: {e}")
