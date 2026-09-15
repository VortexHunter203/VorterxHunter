import asyncio
import random
from pyrogram import Client, filters
from pyrogram.enums import ChatType
from pyrogram.enums import ChatType, ChatMemberStatus
from pyrogram.errors import UserNotParticipant
from pyrogram.types import ChatPermissions
from BrandrdXMusic import app
from BrandrdXMusic.utils.branded_ban import admin_filter

SPAM_CHATS = {}


@app.on_message(
    filters.command(["utag", "uall"], prefixes=["/", "@", ".", "#"]) & admin_filter
)
async def tag_all_users(_, message):
    global SPAM_CHATS

    chat_id = message.chat.id

    # ⚠️ Text required
    if len(message.text.split()) == 1:
        await message.reply_text(
            "<b><blockquote>"
            "💬 ɢɪᴠᴇ sᴏᴍᴇ ᴛᴇxᴛ ᴛᴏ ᴛᴀɢ ᴀʟʟ, ʟɪᴋᴇ » "
            "<code>@utag Hi Friends</code>"
            "</blockquote></b>",
        )
        return

    text = message.text.split(None, 1)[1]

    if text:
        await message.reply_text(
            "<b><blockquote>"
            "🚀 ᴜᴛᴀɢ [ᴜɴʟɪᴍɪᴛᴇᴅ ᴛᴀɢ] sᴛᴀʀᴛᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ! 🎉\n\n"
            "⏳ ᴛᴀɢɢɪɴɢ ᴡɪᴛʜ sʟᴇᴇᴘ ᴏғ 7 sᴇᴄ.\n\n"
            "🛑 ᴏғғ ᴛᴀɢɢɪɴɢ ʙʏ » <code>/stoputag</code>"
            "</blockquote></b>",
        )

    SPAM_CHATS[chat_id] = True
    f = True

    while f:

        if SPAM_CHATS.get(chat_id) == False:
            await message.reply_text(
                "<b><blockquote>"
                "🛑 ᴜɴʟɪᴍɪᴛᴇᴅ ᴛᴀɢɢɪɴɢ sᴜᴄᴄᴇssғᴜʟʟʏ sᴛᴏᴘᴘᴇᴅ."
                "</blockquote></b>",
            )
            break

        usernum = 0
        usertxt = ""

        try:
            async for m in app.get_chat_members(message.chat.id):

                if SPAM_CHATS.get(chat_id) == False:
                    break

                if m.user.is_bot:
                    continue

                usernum += 1

                # 👤 HTML clickable mention
                usertxt += (
                    f"\n⊚ <a href='tg://user?id={m.user.id}'>"
                    f"{m.user.first_name or 'User'}"
                    f"</a>\n"
                )

                if usernum == 5:

                    await app.send_message(
                        message.chat.id,
                        (
                            f"<b><blockquote>"
                            f"{text}\n"
                            f"{usertxt}\n\n"
                            f"|| ➥ ᴏғғ ᴛᴀɢɢɪɴɢ ʙʏ » "
                            f"<code>/stoputag</code> ||"
                            f"</blockquote></b>"
                        ),
                    )

                    usernum = 0
                    usertxt = ""

                    await asyncio.sleep(7)

        except Exception as e:
            print(e)


@app.on_message(
    filters.command(
        [
            "stoputag",
            "stopuall",
            "offutag",
            "offuall",
            "utagoff",
            "ualloff",
        ],
        prefixes=["/", ".", "@", "#"],
    )
    & admin_filter
)
async def stop_tagging(_, message):
    global SPAM_CHATS

    chat_id = message.chat.id

    if SPAM_CHATS.get(chat_id) == True:

        SPAM_CHATS[chat_id] = False

        return await message.reply_text(
            "<b><blockquote>"
            "⏳ ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ...\n\n"
            "🛑 sᴛᴏᴘᴘɪɴɢ ᴜɴʟɪᴍɪᴛᴇᴅ ᴛᴀɢɢɪɴɢ..."
            "</blockquote></b>",
        )

    else:

        await message.reply_text(
            "<b><blockquote>"
            "ℹ️ ᴜᴛᴀɢ ᴘʀᴏᴄᴇss ɪs ɴᴏᴛ ᴀᴄᴛɪᴠᴇ."
            "</blockquote></b>",
        )
