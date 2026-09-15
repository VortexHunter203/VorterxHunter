import os
import asyncio
import aiohttp

from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from BrandrdXMusic import app


# ============================================================
# CONFIG
# ============================================================

GOFILE_UPLOAD_URL = "https://upload.gofile.io/uploadfile"

# Change this if you want a lower limit.
# Gofile itself does not require this exact 200 MB limit,
# but keeping a limit prevents huge Telegram downloads.
MAX_FILE_SIZE = 200 * 1024 * 1024  # 200 MB


# ============================================================
# FORMAT SIZE
# ============================================================

def format_size(size):
    if not size:
        return "0 B"

    if size < 1024:
        return f"{size} B"

    if size < 1024 * 1024:
        return f"{size / 1024:.2f} KB"

    if size < 1024 * 1024 * 1024:
        return f"{size / (1024 * 1024):.2f} MB"

    return f"{size / (1024 * 1024 * 1024):.2f} GB"


# ============================================================
# GOFILE UPLOADER
# ============================================================

async def upload_file(file_path):

    if not file_path:
        return False, "Fɪʟᴇ ᴘᴀᴛʜ ɪs ᴇᴍᴘᴛʏ."

    if not os.path.exists(file_path):
        return False, "Fɪʟᴇ ᴅᴏᴇs ɴᴏᴛ ᴇxɪsᴛ."

    file_size = os.path.getsize(file_path)

    if file_size <= 0:
        return False, "Fɪʟᴇ ɪs ᴇᴍᴘᴛʏ."

    if file_size > MAX_FILE_SIZE:
        return False, (
            f"Fɪʟᴇ ɪs ᴛᴏᴏ ʟᴀʀɢᴇ.\n"
            f"Sɪᴢᴇ: <code>{format_size(file_size)}</code>\n"
            f"Mᴀxɪᴍᴜᴍ: <code>{format_size(MAX_FILE_SIZE)}</code>"
        )

    timeout = aiohttp.ClientTimeout(
        total=1800,
        connect=60,
        sock_connect=60,
        sock_read=1800,
    )

    headers = {
        "User-Agent": (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/140.0 Safari/537.36"
        )
    }

    try:

        async with aiohttp.ClientSession(
            timeout=timeout,
            headers=headers,
        ) as session:

            with open(file_path, "rb") as file:

                form = aiohttp.FormData()

                form.add_field(
                    "file",
                    file,
                    filename=os.path.basename(file_path),
                    content_type="application/octet-stream",
                )

                async with session.post(
                    GOFILE_UPLOAD_URL,
                    data=form,
                ) as response:

                    response_text = await response.text()

                    print(
                        f"Gofile HTTP Status: {response.status}"
                    )

                    print(
                        f"Gofile Response: "
                        f"{response_text[:2000]}"
                    )

                    if response.status != 200:

                        return False, (
                            f"Gᴏғɪʟᴇ Eʀʀᴏʀ: "
                            f"<code>{response.status}</code>\n\n"
                            f"<code>{response_text[:1000]}</code>"
                        )

                    # Try JSON response
                    try:
                        data = await response.json(
                            content_type=None
                        )

                    except Exception:

                        return False, (
                            "Gᴏғɪʟᴇ ʀᴇᴛᴜʀɴᴇᴅ ᴀɴ "
                            "ɪɴᴠᴀʟɪᴅ ʀᴇsᴘᴏɴsᴇ.\n\n"
                            f"<code>{response_text[:1000]}</code>"
                        )

                    if not isinstance(data, dict):

                        return False, (
                            "Gᴏғɪʟᴇ ʀᴇᴛᴜʀɴᴇᴅ ᴀɴ "
                            "ᴜɴᴋɴᴏᴡɴ ʀᴇsᴘᴏɴsᴇ."
                        )

                    print(f"Gofile JSON: {data}")

                    # ------------------------------------------------
                    # Gofile normally returns:
                    #
                    # {
                    #   "status": "ok",
                    #   "data": {
                    #       "downloadPage": "...",
                    #       "guestToken": "...",
                    #       "parentFolder": "...",
                    #       ...
                    #   }
                    # }
                    # ------------------------------------------------

                    status = data.get("status")

                    if status != "ok":

                        message = (
                            data.get("message")
                            or data.get("error")
                            or str(data)
                        )

                        return False, (
                            "Gᴏғɪʟᴇ Uᴘʟᴏᴀᴅ Fᴀɪʟᴇᴅ.\n\n"
                            f"<code>{str(message)[:1000]}</code>"
                        )

                    result = data.get("data")

                    if not isinstance(result, dict):

                        return False, (
                            "Gᴏғɪʟᴇ ᴅɪᴅ ɴᴏᴛ ʀᴇᴛᴜʀɴ "
                            "ᴠᴀʟɪᴅ ғɪʟᴇ ᴅᴀᴛᴀ."
                        )

                    # Download page
                    download_page = (
                        result.get("downloadPage")
                        or result.get("downloadpage")
                        or result.get("link")
                    )

                    # Some Gofile responses may provide a direct link.
                    direct_link = (
                        result.get("directLink")
                        or result.get("directlink")
                        or result.get("downloadUrl")
                        or result.get("downloadURL")
                    )

                    final_url = (
                        direct_link
                        or download_page
                    )

                    if not final_url:

                        return False, (
                            "Gᴏғɪʟᴇ ᴜᴘʟᴏᴀᴅᴇᴅ ᴛʜᴇ ғɪʟᴇ "
                            "ʙᴜᴛ ɴᴏ ᴅᴏᴡɴʟᴏᴀᴅ ʟɪɴᴋ ᴡᴀs ғᴏᴜɴᴅ.\n\n"
                            f"<code>{str(result)[:1500]}</code>"
                        )

                    return True, final_url

    except asyncio.TimeoutError:

        return False, (
            "Gᴏғɪʟᴇ ᴜᴘʟᴏᴀᴅ ᴛɪᴍᴇᴅ ᴏᴜᴛ.\n\n"
            "Pʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ."
        )

    except aiohttp.ClientError as e:

        print(
            f"Gofile Client Error: {type(e).__name__}: {e}"
        )

        return False, (
            "Fᴀɪʟᴇᴅ ᴛᴏ ᴄᴏɴɴᴇᴄᴛ ᴛᴏ Gᴏғɪʟᴇ.\n\n"
            f"<code>{str(e)[:1000]}</code>"
        )

    except Exception as e:

        print(
            f"Gofile Upload Error: "
            f"{type(e).__name__}: {e}"
        )

        return False, (
            "Gᴏғɪʟᴇ Uᴘʟᴏᴀᴅ Eʀʀᴏʀ.\n\n"
            f"<code>{str(e)[:1000]}</code>"
        )


# ============================================================
# /TGM COMMAND
# ============================================================

@app.on_message(
    filters.command(
        ["tgm", "tgt", "telegraph", "tl"]
    )
)
async def get_link_group(client, message):

    media = message.reply_to_message

    # ========================================================
    # CHECK REPLY
    # ========================================================

    if not media:

        return await message.reply_text(
            "<blockquote>"
            "<b>❌ Rᴇᴘʟʏ Tᴏ A Mᴇᴅɪᴀ Fɪʟᴇ</b>\n\n"
            "Rᴇᴘʟʏ ᴛᴏ ᴀ ᴘʜᴏᴛᴏ, ᴠɪᴅᴇᴏ, "
            "ᴅᴏᴄᴜᴍᴇɴᴛ, ᴀᴜᴅɪᴏ ᴏʀ ᴀɴɪᴍᴀᴛɪᴏɴ "
            "ᴡɪᴛʜ <code>/tgm</code>."
            "</blockquote>",
        )

    # ========================================================
    # DETECT FILE
    # ========================================================

    file_size = 0

    if media.photo:

        file_size = media.photo.file_size or 0

    elif media.video:

        file_size = media.video.file_size or 0

    elif media.document:

        file_size = media.document.file_size or 0

    elif media.audio:

        file_size = media.audio.file_size or 0

    elif media.animation:

        file_size = media.animation.file_size or 0

    elif media.voice:

        file_size = media.voice.file_size or 0

    elif media.video_note:

        file_size = media.video_note.file_size or 0

    else:

        return await message.reply_text(
            "<blockquote>"
            "<b>❌ Uɴsᴜᴘᴘᴏʀᴛᴇᴅ Mᴇᴅɪᴀ</b>\n\n"
            "Pʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴘʜᴏᴛᴏ, ᴠɪᴅᴇᴏ, "
            "ᴅᴏᴄᴜᴍᴇɴᴛ, ᴀᴜᴅɪᴏ ᴏʀ ᴀɴɪᴍᴀᴛɪᴏɴ."
            "</blockquote>",
        )

    # ========================================================
    # SIZE CHECK
    # ========================================================

    if file_size > MAX_FILE_SIZE:

        return await message.reply_text(
            "<blockquote>"
            "<b>❌ Fɪʟᴇ Tᴏᴏ Lᴀʀɢᴇ</b>\n\n"
            f"<b>Fɪʟᴇ:</b> "
            f"<code>{format_size(file_size)}</code>\n"
            f"<b>Lɪᴍɪᴛ:</b> "
            f"<code>{format_size(MAX_FILE_SIZE)}</code>"
            "</blockquote>",
        )

    # ========================================================
    # STATUS
    # ========================================================

    status = await message.reply_text(
        "<blockquote>"
        "<b>📥 Dᴏᴡɴʟᴏᴀᴅɪɴɢ Fɪʟᴇ...</b>\n\n"
        "<i>Pʟᴇᴀsᴇ Wᴀɪᴛ...</i>"
        "</blockquote>",
    )

    local_path = None

    try:

        # ====================================================
        # DOWNLOAD FROM TELEGRAM
        # ====================================================

        last_update = 0

        async def progress(current, total):

            nonlocal last_update

            if not total:
                return

            now = asyncio.get_running_loop().time()

            if now - last_update < 2:
                return

            last_update = now

            percent = current * 100 / total

            try:

                await status.edit_text(
                    "<blockquote>"
                    "<b>📥 Dᴏᴡɴʟᴏᴀᴅɪɴɢ...</b>\n\n"
                    f"<b>Pʀᴏɢʀᴇss:</b> "
                    f"<code>{percent:.1f}%</code>\n"
                    f"<b>Sɪᴢᴇ:</b> "
                    f"<code>{format_size(current)} / "
                    f"{format_size(total)}</code>"
                    "</blockquote>",
                )

            except Exception:
                pass

        local_path = await media.download(
            progress=progress
        )

        if not local_path:
            raise Exception(
                "Telegram did not return a file path."
            )

        if not os.path.exists(local_path):
            raise Exception(
                "Downloaded file was not found."
            )

        # ====================================================
        # UPLOAD
        # ====================================================

        await status.edit_text(
            "<blockquote>"
            "<b>📤 Uᴘʟᴏᴀᴅɪɴɢ Tᴏ Gᴏғɪʟᴇ...</b>\n\n"
            f"<b>Fɪʟᴇ:</b> "
            f"<code>{format_size(os.path.getsize(local_path))}</code>\n\n"
            "<i>Dᴏ ɴᴏᴛ sᴇɴᴅ ᴀɴᴏᴛʜᴇʀ ᴄᴏᴍᴍᴀɴᴅ ᴜɴᴛɪʟ ᴜᴘʟᴏᴀᴅ ɪs ғɪɴɪsʜᴇᴅ.</i>"
            "</blockquote>",
        )

        success, result = await upload_file(
            local_path
        )

        # ====================================================
        # SUCCESS
        # ====================================================

        if success:

            upload_url = result.strip()

            keyboard = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "🔗 Oᴘᴇɴ Fɪʟᴇ",
                            url=upload_url,
                        )
                    ]
                ]
            )

            await status.edit_text(
                "<blockquote>"
                "<b>✅ Uᴘʟᴏᴀᴅ Sᴜᴄᴄᴇssғᴜʟ</b>\n\n"
                f"<b>📦 Fɪʟᴇ Sɪᴢᴇ:</b> "
                f"<code>{format_size(file_size)}</code>\n\n"
                f"<b>🔗 Lɪɴᴋ:</b>\n"
                f"<code>{upload_url}</code>\n\n"
                "<i>Cʀᴇᴀᴛᴇ Bʏ [Bʀᴀɴᴅʀᴅ Mᴜsɪᴄ](https://t.me/Systumm_music_bot?startgroup)</i>"
                "</blockquote>",
                reply_markup=keyboard,
                disable_web_page_preview=True,
            )

        # ====================================================
        # FAILURE
        # ====================================================

        else:

            await status.edit_text(
                "<blockquote>"
                "<b>❌ Uᴘʟᴏᴀᴅ Fᴀɪʟᴇᴅ</b>\n\n"
                f"<b>Rᴇᴀsᴏɴ:</b>\n"
                f"{result}"
                "</blockquote>",
            )

    except Exception as e:

        print(
            f"TGM ERROR: "
            f"{type(e).__name__}: {e}"
        )

        try:

            await status.edit_text(
                "<blockquote>"
                "<b>❌ Pʀᴏᴄᴇssɪɴɢ Eʀʀᴏʀ</b>\n\n"
                f"<b>Eʀʀᴏʀ:</b>\n"
                f"<code>{str(e)[:1500]}</code>"
                "</blockquote>",
            )

        except Exception:
            pass

    finally:

        # ====================================================
        # DELETE TEMP FILE
        # ====================================================

        if local_path:

            try:

                if os.path.exists(local_path):
                    os.remove(local_path)

            except Exception as e:

                print(
                    f"Cleanup Error: {e}"
                )


# ============================================================
# HELP
# ============================================================

__MODULE__ = "Tᴇʟᴇɢʀᴀᴘʜ"

__HELP__ = """
<b>📤 Fɪʟᴇ Uᴘʟᴏᴀᴅᴇʀ</b>

<blockquote>
<b>Cᴏᴍᴍᴀɴᴅs:</b>

• <code>/tgm</code>
• <code>/tgt</code>
• <code>/telegraph</code>
• <code>/tl</code>

<b>Uѕᴀɢᴇ:</b>

Rᴇᴘʟʏ ᴛᴏ ᴀɴʏ ᴏғ ᴛʜᴇsᴇ:

• Pʜᴏᴛᴏ
• Vɪᴅᴇᴏ
• Dᴏᴄᴜᴍᴇɴᴛ
• Aᴜᴅɪᴏ
• Aɴɪᴍᴀᴛɪᴏɴ
• Vᴏɪᴄᴇ
• Vɪᴅᴇᴏ Nᴏᴛᴇ

Tʜᴇɴ sᴇɴᴅ:

<code>/tgm</code>

<b>Uᴘʟᴏᴀᴅ Hᴏsᴛ:</b>
Gᴏғɪʟᴇ

<b>Bᴏᴛ Lɪᴍɪᴛ:</b>
<code>200 MB</code>
</blockquote>
"""
