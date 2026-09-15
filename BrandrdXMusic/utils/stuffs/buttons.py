from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram import Client, filters, enums 

class BUTTONS(object):
    MBUTTON = [
        [
            InlineKeyboardButton("🎵 𝖵ᴄ 𝖳ᴏᴏʟ", callback_data="mplus HELP_Vctool"),
            InlineKeyboardButton("📜 Hɪsᴛᴏʀʏ", callback_data="mplus HELP_History"),
            InlineKeyboardButton("🎬 Rᴇᴇʟ", callback_data="mplus HELP_Reel"),
        ],
        [
            InlineKeyboardButton("🏷️ Tᴀɢ-Aʟʟ", callback_data="mplus HELP_TagAll"),
            InlineKeyboardButton("ℹ️ Iɴꜰᴏ", callback_data="mplus HELP_Info"),
            InlineKeyboardButton("🧰 Exᴛʀᴀ", callback_data="mplus HELP_Extra"),
        ],
        [
            InlineKeyboardButton("💞 Cᴏᴜᴘʟᴇꜱ", callback_data="mplus HELP_Couples"),
            InlineKeyboardButton("🛡️ Aᴄᴛɪᴏɴ", callback_data="mplus HELP_Action"),
            InlineKeyboardButton("🔍 Sᴇᴀʀᴄʜ", callback_data="mplus HELP_Search"),
        ],
        [
            InlineKeyboardButton("🔤 Fᴏɴᴛ", callback_data="mplus HELP_Font"),
            InlineKeyboardButton("🤖 Bᴏᴛs", callback_data="mplus HELP_Bots"),
            InlineKeyboardButton("✈️ T-Gʀᴀᴘʜ", callback_data="mplus HELP_TG"),
        ],
        [
            InlineKeyboardButton("💻 Sᴏᴜʀᴄᴇ", callback_data="mplus HELP_Source"),
            InlineKeyboardButton("🎭 Tʀᴜᴛʜ-Dᴀʀᴇ", callback_data="mplus HELP_TD"),
            InlineKeyboardButton("🧠 Qᴜɪᴢ", callback_data="mplus HELP_Quiz"),
        ],
        [
            InlineKeyboardButton("🔊 Tᴛs", callback_data="mplus HELP_TTS"),
            InlineKeyboardButton("📻 Rᴀᴅɪᴏ", callback_data="mplus HELP_Radio"),
            InlineKeyboardButton("💬 Qᴜᴏᴛʟʏ", callback_data="mplus HELP_Q"),
        ],
        [
            InlineKeyboardButton("◁", callback_data="settings_back_helper"),
            InlineKeyboardButton("↻ ʙᴀᴄᴋ ↻", callback_data="mbot_cb"),
            InlineKeyboardButton("▷", callback_data="managebot123 settings_back_helper"),
        ],
    ]
