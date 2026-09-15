from pyrogram import Client, filters
import requests
import random
from BrandrdXMusic import app

# Truth or Dare API URLs
truth_api_url = "https://api.truthordarebot.xyz/v1/truth"
dare_api_url = "https://api.truthordarebot.xyz/v1/dare"

@app.on_message(filters.command("truth"))
def get_truth(client, message):
    try:
        # 🎯 Make a GET request to the Truth API
        response = requests.get(truth_api_url)

        if response.status_code == 200:
            truth_question = response.json()["question"]

            message.reply_text(
                f"<b><blockquote>"
                f"🎯 Tʀᴜᴛʜ Qᴜᴇsᴛɪᴏɴ\n\n"
                f"💭 {truth_question}"
                f"</blockquote></b>",
            )

        else:
            message.reply_text(
                "<b><blockquote>"
                "⚠️ Fᴀɪʟᴇᴅ Tᴏ Fᴇᴛᴄʜ A Tʀᴜᴛʜ Qᴜᴇsᴛɪᴏɴ.\n\n"
                "🔄 Pʟᴇᴀsᴇ Tʀʏ Aɢᴀɪɴ Lᴀᴛᴇʀ."
                "</blockquote></b>",
            )

    except Exception as e:
        message.reply_text(
            "<b><blockquote>"
            "❌ Aɴ Eʀʀᴏʀ Oᴄᴄᴜʀʀᴇᴅ Wʜɪʟᴇ Fᴇᴛᴄʜɪɴɢ Tʀᴜᴛʜ.\n\n"
            "🔄 Pʟᴇᴀsᴇ Tʀʏ Aɢᴀɪɴ Lᴀᴛᴇʀ."
            "</blockquote></b>",
        )


@app.on_message(filters.command("dare"))
def get_dare(client, message):
    try:
        # 🔥 Make a GET request to the Dare API
        response = requests.get(dare_api_url)

        if response.status_code == 200:
            dare_question = response.json()["question"]

            message.reply_text(
                f"<b><blockquote>"
                f"🔥 Dᴀʀᴇ Qᴜᴇsᴛɪᴏɴ\n\n"
                f"🎯 {dare_question}"
                f"</blockquote></b>",
            )

        else:
            message.reply_text(
                "<b><blockquote>"
                "⚠️ Fᴀɪʟᴇᴅ Tᴏ Fᴇᴛᴄʜ A Dᴀʀᴇ Qᴜᴇsᴛɪᴏɴ.\n\n"
                "🔄 Pʟᴇᴀsᴇ Tʀʏ Aɢᴀɪɴ Lᴀᴛᴇʀ."
                "</blockquote></b>",
            )

    except Exception as e:
        message.reply_text(
            "<b><blockquote>"
            "❌ Aɴ Eʀʀᴏʀ Oᴄᴄᴜʀʀᴇᴅ Wʜɪʟᴇ Fᴇᴛᴄʜɪɴɢ Dᴀʀᴇ.\n\n"
            "🔄 Pʟᴇᴀsᴇ Tʀʏ Aɢᴀɪɴ Lᴀᴛᴇʀ."
            "</blockquote></b>",
        )
