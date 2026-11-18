import asyncio
from datetime import datetime, timedelta, timezone

from telethon import events
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

VERSION = "1.0.0"
CATEGORY = "utilities"

active_scans = {}
scan_results = {}


def init(client_instance):
    add_handler(
        "replyall",
        [
            ".ra - Scan last 9 days",
            ".ra all - Select all",
            ".ra 1,2,3 - Select numbered messages",
            ".sra - Stop scan",
        ],
        "ReplyAll Scanner"
    )


async def register_commands():

    @CipherElite.on(events.NewMessage(pattern=r"^\.ra$"))
    @rishabh()
    async def scan(event):
        chat_id = event.chat_id

        if chat_id in active_scans:
            return

        active_scans[chat_id] = True
        cutoff = datetime.now(timezone.utc) - timedelta(days=9)

        selected = []
        bot_cache = {}
        me = await event.client.get_me()

        try:
            async for msg in event.client.iter_messages(chat_id):
                if not active_scans.get(chat_id):
                    return

                if msg.date < cutoff:
                    break

                uid = msg.sender_id

                if not uid or uid == me.id:
                    continue

                if uid not in bot_cache:
                    sender = await msg.get_sender()
                    bot_cache[uid] = (
                        sender is None or getattr(sender, "bot", False)
                    )

                if bot_cache[uid]:
                    continue

                if any(x["user_id"] == uid for x in selected):
                    continue

                selected.append({
                    "user_id": uid,
                    "message_id": msg.id,
                    "text": msg.text or "[Media]"
                })

            scan_results[chat_id] = selected

            sent = await event.reply(
                f"✅ Scan Complete\n👥 Members Scanned: {len(selected)}"
            )
            await asyncio.sleep(5)
            await sent.delete()

        finally:
            active_scans.pop(chat_id, None)

    @CipherElite.on(events.NewMessage(pattern=r"^\.ra (.+)$"))
    @rishabh()
    async def select(event):
        chat_id = event.chat_id
        data = scan_results.get(chat_id, [])

        if not data:
            return

        arg = event.pattern_match.group(1).strip()
        parts = arg.split(maxsplit=1)
        choice = parts[0]

        if choice.lower() == "all":
            indexes = range(len(data))
        else:
            try:
                indexes = [
                    int(x.strip()) - 1
                    for x in choice.split(",")
                ]
            except ValueError:
                return

        chosen = [
            data[i] for i in indexes
            if 0 <= i < len(data)
        ]

        if not chosen:
            return

        preview = "\n".join(
            f"{i + 1}. {item['text'][:60]}"
            for i, item in enumerate(chosen)
        )

        await event.reply(
            f"📋 Selected: {len(chosen)}\n\n{preview}\n\n"
            "Manual approval required."
        )

    @CipherElite.on(events.NewMessage(pattern=r"^\.sra$"))
    @rishabh()
    async def stop(event):
        active_scans[event.chat_id] = False
