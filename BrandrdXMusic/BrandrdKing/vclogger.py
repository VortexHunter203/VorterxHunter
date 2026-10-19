import asyncio
import logging

from pyrogram import enums, filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from pytgcalls.types import (
    JoinedGroupCallParticipant,
    LeftGroupCallParticipant,
    Update,
)

from BrandrdXMusic import app
from BrandrdXMusic.utils.database import (
    is_vclogger_on,
    vclogger_on,
    vclogger_off,
)

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.WARNING)


# VC LOGGER ENABLE / DISABLE COMMAND

@app.on_message(filters.command("vclogger") & filters.group)
async def vclogger_command(client, message):
    chat_id = message.chat.id

    try:
        member = await client.get_chat_member(
            chat_id, message.from_user.id
        )

        if member.status not in (
            ChatMemberStatus.OWNER,
            ChatMemberStatus.ADMINISTRATOR,
        ):
            return await message.reply_text(
                "<b>❌ Only Admins Can Manage VC Logger.</b>",
                parse_mode=enums.ParseMode.HTML,
            )

        if len(message.command) < 2:
            status = await is_vclogger_on(chat_id)

            return await message.reply_text(
                "<b><blockquote>"
                "🎧 VC LOGGER SETTINGS\n\n"
                f"Status : {'ENABLED ✅' if status else 'DISABLED ❌'}\n\n"
                "➤ /vclogger on\n"
                "➤ /vclogger off"
                "</blockquote></b>",
                parse_mode=enums.ParseMode.HTML,
            )

        action = message.command[1].lower()

        if action in ("on", "enable"):
            await vclogger_on(chat_id)

            return await message.reply_text(
                "<b><blockquote>"
                "✅ VC LOGGER ENABLED\n\n"
                "Voice Chat Join/Leave Logging Is Now Active."
                "</blockquote></b>",
                parse_mode=enums.ParseMode.HTML,
            )

        elif action in ("off", "disable"):
            await vclogger_off(chat_id)

            return await message.reply_text(
                "<b><blockquote>"
                "❌ VC LOGGER DISABLED\n\n"
                "Voice Chat Join/Leave Logging Is Now Stopped."
                "</blockquote></b>",
                parse_mode=enums.ParseMode.HTML,
            )

        return await message.reply_text(
            "<b>Usage: /vclogger on | off</b>",
            parse_mode=enums.ParseMode.HTML,
        )

    except Exception:
        LOG.exception("[VC Logger] Command failed")


# USER MENTION

async def vclogger_mention(user_id: int):
    try:
        user = await app.get_users(user_id)
        return user.mention
    except Exception:
        return f"<a href='tg://user?id={user_id}'>ᴜsᴇʀ</a>"


# AUTO DELETE AFTER 5 SECONDS

async def _vc_delete_later(message):
    try:
        await asyncio.sleep(5)
        await message.delete()
    except asyncio.CancelledError:
        raise
    except Exception:
        pass


# JOIN VC BUTTON

async def _vc_join_keyboard(chat_id):
    try:
        chat = await app.get_chat(chat_id)
        username = getattr(chat, "username", None)

        if username:
            vc_url = f"https://t.me/{username}?voicechat"

        elif str(chat_id).startswith("-100"):
            vc_url = f"https://t.me/c/{str(chat_id)[4:]}?voicechat"

        else:
            return None

        return InlineKeyboardMarkup(
            [[InlineKeyboardButton("🎧 Join To VC", url=vc_url)]]
        )

    except Exception:
        return None


# VC JOIN / LEFT LOGGER

async def participants_change_handler(_, update: Update):
    try:
        if not isinstance(
            update,
            (JoinedGroupCallParticipant, LeftGroupCallParticipant),
        ):
            return

        chat_id = getattr(update, "chat_id", None)
        participant = getattr(update, "participant", None)

        if chat_id is None or participant is None:
            return

        user_id = getattr(participant, "user_id", None)

        if user_id is None:
            return

        if not await is_vclogger_on(chat_id):
            return

        tag = (
            "#JᴏɪɴᴇᴅVᴄ"
            if isinstance(update, JoinedGroupCallParticipant)
            else "#LᴇғᴛVᴄ"
        )

        role = "MEMBER"

        try:
            member = await app.get_chat_member(chat_id, user_id)

            if member.status == ChatMemberStatus.OWNER:
                role = "OWNER"

            elif member.status == ChatMemberStatus.ADMINISTRATOR:
                role = "ADMIN"

        except Exception:
            pass

        mention = await vclogger_mention(user_id)

        text = (
            f"<b><blockquote>{tag}\n\n"
            f"➤ Usᴇʀ - {mention}\n"
            f"➤ Usᴇʀɪᴅ - <code>{user_id}</code>\n"
            f"➤ Rᴏʟᴇ - {role}"
            "</blockquote></b>"
        )

        keyboard = await _vc_join_keyboard(chat_id)

        sent_message = await app.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.HTML,
            disable_web_page_preview=True,
        )

        asyncio.create_task(_vc_delete_later(sent_message))

        return sent_message

    except asyncio.CancelledError:
        raise

    except Exception:
        LOG.exception("[VC Logger] Participant handler failed")
        return None


# REGISTER LOGGER WITH ALL 5 ASSISTANTS

def register_vclogger(call):
    assistants = [
        call.one,
        call.two,
        call.three,
        call.four,
        call.five,
    ]

    for assistant in assistants:
        assistant.on_participants_change()(
            participants_change_handler
        )
