import asyncio

from pyrogram import enums, filters
from pyrogram.errors import FloodWait

from BrandrdXMusic import app

@app.on_message(filters.command("bots") & filters.group)
async def bots(client, message):
    try:
        botList = []

        async for bot in app.get_chat_members(
            message.chat.id,
            filter=enums.ChatMembersFilter.BOTS
        ):
            botList.append(bot.user)

        lenBotList = len(botList)

        if not botList:
            await message.reply_text(
                "<b><blockquote>🤖 Is group mein koi bot nahi hai.</blockquote></b>",
            )
            return

        text3 = (
            f"<b>ʙᴏᴛ ʟɪsᴛ - {message.chat.title}</b>\n\n"
            f"<b>🤖 ʙᴏᴛs</b>\n"
        )

        while len(botList) > 1:
            bot = botList.pop(0)
            username = f"@{bot.username}" if bot.username else bot.first_name
            text3 += f"├ {username}\n"

        bot = botList.pop(0)
        username = f"@{bot.username}" if bot.username else bot.first_name
        text3 += f"└ {username}\n\n"

        text3 += (
            f"<b>ᴛᴏᴛᴀʟ ɴᴜᴍʙᴇʀ ᴏғ ʙᴏᴛs:</b> "
            f"<b>{lenBotList}</b>"
        )

        await app.send_message(
            message.chat.id,
            text3,
        )

    except FloodWait as e:
        await asyncio.sleep(e.value)
