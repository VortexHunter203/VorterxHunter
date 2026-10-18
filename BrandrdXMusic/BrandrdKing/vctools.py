from pyrogram import Client, filters
from pyrogram.types import Message
from BrandrdXMusic import app
from pyrogram import *
import time
from pyrogram.types import *
from config import OWNER_ID
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.raw.functions.phone import CreateGroupCall, DiscardGroupCall
from pyrogram.raw.types import InputGroupCall
from BrandrdXMusic.utils.database import get_assistant
from telethon.tl.functions.phone import (
    CreateGroupCallRequest,
    DiscardGroupCallRequest,
    GetGroupCallRequest,
    InviteToGroupCallRequest,
)

# VC start time storage
vc_start_times = {}

# vc on
@app.on_message(filters.video_chat_started)
async def brah(_, msg):
    group_name = msg.chat.title or "Private Chat"
    chat_id = msg.chat.id

    # Save VC start time
    vc_start_times[chat_id] = time.time()

    await msg.reply(
        f"<b><blockquote>"
        f"ᴠɪᴅᴇᴏ ᴄʜᴀᴛ sᴛᴀʀᴛᴇᴅ\n\n"
        f"──────────\n"
        f"๏ sᴛᴀʀᴛᴇᴅ ʙʏ : {group_name}\n"
        f"๏ ᴄʜᴀᴛ ɪᴅ : <code>{chat_id}</code>\n"
        f"──────────\n"
        f"ᴊᴏɪɴ ᴛʜᴇ ᴠɪᴅᴇᴏ ᴄʜᴀᴛ ɴᴏᴡ!"
        f"</blockquote></b>"
    )


# vc off
@app.on_message(filters.video_chat_ended)
async def brah2(_, msg):
    group_name = msg.chat.title or "Private Chat"
    chat_id = msg.chat.id

    # Get VC start time
    start_time = vc_start_times.pop(chat_id, None)

    if start_time is not None:
        total_seconds = int(time.time() - start_time)

        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        if hours:
            duration_text = f"{hours}h {minutes}m {seconds}s"
        elif minutes:
            duration_text = f"{minutes}m {seconds}s"
        else:
            duration_text = f"{seconds}s"
    else:
        duration_text = "Unknown"

    await msg.reply(
        f"<b><blockquote>"
        f"ᴠɪᴅᴇᴏ ᴄʜᴀᴛ ᴇɴᴅᴇᴅ\n\n"
        f"──────────\n"
        f"๏ ɢʀᴏᴜᴘ : {group_name}\n"
        f"๏ ᴄʜᴀᴛ ɪᴅ : <code>{chat_id}</code>\n"
        f"๏ ᴅᴜʀᴀᴛɪᴏɴ : {duration_text}\n"
        f"──────────"
        f"</blockquote></b>"
    )
# ================================
# Invite Members on VC
# ================================

@app.on_message(filters.video_chat_members_invited)
async def brah3(client, message: Message):
    try:
        invited_users = []

        for user in message.video_chat_members_invited.users:
            try:
                invited_users.append(
                    f'<a href="tg://user?id={user.id}">{user.first_name}</a>'
                )
            except Exception:
                pass

        users_text = " • ".join(invited_users)

        group_name = message.chat.title or "Private Chat"
        chat_id = message.chat.id

        add_link = f"https://t.me/{client.me.username}?startgroup=true"

        reply_text = (
            f"<b><blockquote>"
            f"➜ {message.from_user.mention} ɪɴᴠɪᴛɪɴɢ: {users_text}: ᴛᴏ ᴛʜᴇ ᴠɪᴅᴇᴏ ᴄʜᴀᴛ\n\n"
            f"</blockquote></b>"
        )

        await message.reply(
            reply_text,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            " ᴊᴏɪɴ ᴠᴄ 🛜",
                            url=add_link
                        )
                    ]
                ]
            )
        )

    except Exception as e:
        print(f"VC Invite Error: {e}")
