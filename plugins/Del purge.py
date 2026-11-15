from telethon import events
from plugins.bot import add_handler
from utils.utils import CipherElite
from utils.decorators import rishabh

VERSION = "1.0.0"
CATEGORY = "moderation"

pending_purge = set()


def init(client_instance):
    commands = [
        ".purge - Scan your own group messages",
        ".purge confirm - Confirm deletion",
        ".purge cancel - Cancel deletion"
    ]
    description = "Delete your own messages from groups."
    add_handler("purge", commands, description)


async def register_commands():

    @CipherElite.on(events.NewMessage(
        pattern=r"\.purge(?:\s+(confirm|cancel))?$"
    ))
    @rishabh()
    async def purge(event):

        if not event.is_group:
            await event.reply("❌ Groups only!")
            return

        chat_id = event.chat_id
        action = event.pattern_match.group(1)

        if action == "cancel":
            pending_purge.discard(chat_id)
            await event.reply("❌ Purge cancelled.")
            return

        if action == "confirm":

            if chat_id not in pending_purge:
                await event.reply("❌ No pending purge request.")
                return

            pending_purge.discard(chat_id)

            await event.reply("🔄 Scanning your messages...")

            me = await event.client.get_me()
            message_ids = []

            async for msg in event.client.iter_messages(
                chat_id,
                from_user=me
            ):
                if msg.id != event.id:
                    message_ids.append(msg.id)

            if not message_ids:
                await event.reply("No messages found.")
                return

            deleted = 0

            for i in range(0, len(message_ids), 100):
                batch = message_ids[i:i + 100]

                await event.client.delete_messages(
                    chat_id,
                    batch
                )

                deleted += len(batch)

            await event.reply(
                f"✅ Successfully deleted {deleted} of your messages!"
            )

            return

        pending_purge.add(chat_id)

        await event.reply(
            "⚠️ **PURGE CONFIRMATION**\n\n"
            "This will delete your own messages "
            "from the available group history.\n\n"
            "Other members' messages will remain untouched.\n\n"
            "Type `.purge confirm` to proceed.\n"
            "Type `.purge cancel` to cancel."
        )
