import asyncio
import sqlite3
from datetime import datetime, timedelta, timezone

from telethon import events
from utils.utils import CipherElite
from utils.decorators import rishabh
from plugins.bot import add_handler

VERSION = "1.0.0"
CATEGORY = "utilities"

DB_PATH = "replyall.db"

active_scans = {}


def init(client_instance):
    commands = [
        ".ra - Scan members' messages from last 9 days",
        ".sra - Stop active scan"
    ]
    add_handler(
        "replyall",
        commands,
        "ReplyAll Member Message Scanner"
    )


def database():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS processed (
            chat_id INTEGER,
            user_id INTEGER,
            message_id INTEGER,
            PRIMARY KEY (chat_id, message_id)
        )
    """)
    conn.commit()
    return conn


async def scan_chat(event, stop_event):
    chat_id = event.chat_id
    cutoff = datetime.now(timezone.utc) - timedelta(days=9)

    selected = {}
    conn = database()

    try:
        async for msg in event.client.iter_messages(chat_id):

            if stop_event.is_set():
                break

            if not msg.date:
                continue

            if msg.date.replace(tzinfo=timezone.utc) < cutoff:
                break

            if not msg.sender_id:
                continue

            if msg.sender_id == event.sender_id:
                continue

            if msg.sender_id in selected:
                continue

            exists = conn.execute(
                """
                SELECT 1 FROM processed
                WHERE chat_id=? AND message_id=?
                """,
                (chat_id, msg.id)
            ).fetchone()

            if exists:
                continue

            selected[msg.sender_id] = msg

            conn.execute(
                "INSERT OR IGNORE INTO processed VALUES (?, ?, ?)",
                (chat_id, msg.sender_id, msg.id)
            )
            conn.commit()

            await asyncio.sleep(0.15)

    finally:
        conn.close()

    return selected


async def register_commands():

    @CipherElite.on(events.NewMessage(pattern=r"^\.ra$"))
    @rishabh()
    async def replyall_scan(event):

        chat_id = event.chat_id

        if chat_id in active_scans:
            await event.reply("⚠️ Scan already running!")
            return

        stop_event = asyncio.Event()
        active_scans[chat_id] = stop_event

        status = await event.reply(
            "🔍 **ReplyAll Scanner Started**\n"
            "📅 History: Last 9 days\n"
            "⏳ Scanning messages..."
        )

        try:
            selected = await scan_chat(event, stop_event)

            if stop_event.is_set():
                await status.edit("🛑 Scan stopped.")
                return

            if not selected:
                await status.edit(
                    "❌ No eligible messages found."
                )
                return

            lines = [
                "🎯 **ReplyAll Scan Complete**",
                f"👥 Members found: `{len(selected)}`",
                "",
                "**Eligible members:**"
            ]

            for index, (user_id, msg) in enumerate(
                selected.items(), 1
            ):
                lines.append(
                    f"{index}. User ID: `{user_id}`"
                    f" | Message ID: `{msg.id}`"
                )

            lines.append("")
            lines.append("💾 Records saved successfully.")

            output = "\n".join(lines)

            if len(output) > 4000:
                output = output[:3900] + "\n\n...List truncated."

            await status.edit(output)

        except Exception as e:
            await status.edit(
                f"❌ Scanner error: `{str(e)[:200]}`"
            )

        finally:
            active_scans.pop(chat_id, None)

    @CipherElite.on(events.NewMessage(pattern=r"^\.sra$"))
    @rishabh()
    async def stop_replyall(event):

        chat_id = event.chat_id

        stop_event = active_scans.get(chat_id)

        if not stop_event:
            await event.reply("ℹ️ No active scan.")
            return

        stop_event.set()

        await event.reply("🛑 ReplyAll scan stopping...")
