import asyncio
from pyrogram import Client, filters
from pyrogram.errors import FloodWait


@Client.on_message(filters.command("dlt", prefixes=[".", "*"]) & filters.me)
async def dlt_all(client, message):
    cid = message.chat.id
    ids = []

    async for m in client.search_messages(cid, from_user="me"):
        ids.append(m.id)
        if len(ids) == 100:
            try:
                await client.delete_messages(cid, ids)
                ids.clear()
                await asyncio.sleep(1)
            except FloodWait as e:
                await asyncio.sleep(e.value)
            except Exception:
                ids.clear()

    if ids:
        try:
            await client.delete_messages(cid, ids)
        except Exception:
            pass
