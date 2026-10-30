from BrandrdXMusic import app
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ParseMode, ButtonStyle
from html import escape


@app.on_message(filters.command("id"))
async def ids(_, message):
    button = InlineKeyboardButton(
        " ᴄʟᴏsᴇ ",
        callback_data="close",
        style=ButtonStyle.DANGER
    )
    markup = InlineKeyboardMarkup([[button]])

    if message.reply_to_message:
        reply = message.reply_to_message

        if reply.from_user:
            text = (
                f"<b><blockquote>"
                f"👤 ᴜsᴇʀ ɴᴀᴍᴇ: "
                f"{escape(reply.from_user.first_name or 'User')}\n"
                f"🆔 ᴜsᴇʀ ɪᴅ: "
                f"<code>{reply.from_user.id}</code>\n\n"
                f"💬 ᴄʜᴀᴛ ɪᴅ: "
                f"<code>{message.chat.id}</code>"
                f"</blockquote></b>"
            )
        else:
            text = (
                f"<b><blockquote>"
                f"💬 ᴄʜᴀᴛ ɪᴅ: "
                f"<code>{message.chat.id}</code>\n"
                f"⚠️ ᴛʜɪs ᴍᴇssᴀɢᴇ ʜᴀs ɴᴏ ᴜsᴇʀ"
                f"</blockquote></b>"
            )

        await message.reply_text(
            text,
            reply_markup=markup,
            parse_mode=ParseMode.HTML
        )

    else:
        chat_name = escape(message.chat.title or "Private Chat")
        user_id = (
            f"<code>{message.from_user.id}</code>"
            if message.from_user
            else "Unavailable"
        )

        text = (
            f"<b><blockquote>"
            f"👥 ɢʀᴏᴜᴘ ɴᴀᴍᴇ: {chat_name}\n"
            f"🆔 ɢʀᴏᴜᴘ ɪᴅ: "
            f"<code>{message.chat.id}</code>\n\n"
            f"👤 ʏᴏᴜʀ ᴜsᴇʀ ɪᴅ: {user_id}"
            f"</blockquote></b>"
        )

        await message.reply_text(
            text,
            reply_markup=markup,
            parse_mode=ParseMode.HTML
        )
