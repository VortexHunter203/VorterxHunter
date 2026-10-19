import os
import sys
import asyncio
import tempfile
import shutil
import logging
from urllib.parse import urlparse
from html import escape

from pyrogram import filters
from BrandrdXMusic import app

logger = logging.getLogger(__name__)


@app.on_message(filters.command(["ig", "instagram", "reel"]))
async def download_instagram_video(client, message):
    if len(message.command) < 2:
        await message.reply_text(
            "<blockquote>"
            "<b>⚠️ Pʟᴇᴀsᴇ Pʀᴏᴠɪᴅᴇ Aɴ Iɴsᴛᴀɢʀᴀᴍ Rᴇᴇʟ URL</b>\n\n"
            "Uѕᴀɢᴇ: <code>/ig https://www.instagram.com/reel/...</code>"
            "</blockquote>",
        )
        return

    url = message.command[1].strip()
    parsed = urlparse(url)
    if parsed.scheme not in ("https", "http") or (parsed.hostname or "").lower() not in (
        "instagram.com", "www.instagram.com", "m.instagram.com", "instagr.am", "www.instagr.am"
    ):
        await message.reply_text(
            "<blockquote>"
            "<b>❌ Iɴᴠᴀʟɪᴅ Iɴsᴛᴀɢʀᴀᴍ URL</b>\n\n"
            "Pʟᴇᴀsᴇ sᴇɴᴅ ᴀ ᴠᴀʟɪᴅ Iɴsᴛᴀɢʀᴀᴍ URL."
            "</blockquote>",
        )
        return

    processing = await message.reply_text(
        "<blockquote>"
        "<b>⏳ Pʀᴏᴄᴇssɪɴɢ Iɴsᴛᴀɢʀᴀᴍ...</b>\n\n"
        "Pʟᴇᴀsᴇ Wᴀɪᴛ..."
        "</blockquote>",
    )

    temp_dir = tempfile.mkdtemp(prefix="instagram_")
    output_template = os.path.join(temp_dir, "%(id)s.%(ext)s")
    process = None

    try:
        await processing.edit_text(
            "<blockquote>"
            "<b>⬇️ Dᴏᴡɴʟᴏᴀᴅɪɴɢ Iɴsᴛᴀɢʀᴀᴍ Vɪᴅᴇᴏ...</b>\n\n"
            "Pʟᴇᴀsᴇ Wᴀɪᴛ..."
            "</blockquote>",
        )

        process = await asyncio.create_subprocess_exec(
            sys.executable, "-m", "yt_dlp",
            "--no-playlist",
            "--no-warnings",
            "--no-progress",
            "--restrict-filenames",
            "--socket-timeout", "30",
            "--retries", "3",
            "--fragment-retries", "3",
            "-f", "bv*+ba/b",
            "--merge-output-format", "mp4",
            "-o", output_template,
            url,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=300)
        except asyncio.TimeoutError:
            process.kill()
            await process.communicate()
            await processing.edit_text(
                "<blockquote><b>❌ Dᴏᴡɴʟᴏᴀᴅ Tɪᴍᴇᴏᴜᴛ</b>\n\n"
                "Iɴsᴛᴀɢʀᴀᴍ ᴅɪᴅ ɴᴏᴛ ʀᴇsᴘᴏɴᴅ ɪɴ ᴛɪᴍᴇ. Pʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ."
                "</blockquote>",
            )
            return

        error_output = stderr.decode("utf-8", errors="replace")
        output_text = stdout.decode("utf-8", errors="replace")

        if process.returncode != 0:
            logger.error("Instagram yt-dlp failed (code %s): %s %s", process.returncode,
                         error_output[-3000:], output_text[-1000:])
            error_lower = (error_output + output_text).lower()
            if any(term in error_lower for term in ("login required", "login to", "sign in", "cookies")):
                title = "❌ Lᴏɢɪɴ Rᴇǫᴜɪʀᴇᴅ"
                detail = "Tʜɪs Iɴsᴛᴀɢʀᴀᴍ Cᴏɴᴛᴇɴᴛ Rᴇǫᴜɪʀᴇs Lᴏɢɪɴ."
            elif "private" in error_lower:
                title = "❌ Pʀɪᴠᴀᴛᴇ Cᴏɴᴛᴇɴᴛ"
                detail = "Pʀɪᴠᴀᴛᴇ Iɴsᴛᴀɢʀᴀᴍ Cᴏɴᴛᴇɴᴛ Cᴀɴɴᴏᴛ Bᴇ Dᴏᴡɴʟᴏᴀᴅᴇᴅ."
            elif any(term in error_lower for term in ("not found", "404", "unavailable", "does not exist")):
                title = "❌ Vɪᴅᴇᴏ Nᴏᴛ Fᴏᴜɴᴅ"
                detail = "Tʜᴇ Iɴsᴛᴀɢʀᴀᴍ Vɪᴅᴇᴏ Cᴏᴜʟᴅ Nᴏᴛ Bᴇ Fᴏᴜɴᴅ."
            else:
                title = "❌ Fᴀɪʟᴇᴅ Tᴏ Dᴏᴡɴʟᴏᴀᴅ"
                detail = "Tʜᴇ Iɴsᴛᴀɢʀᴀᴍ Vɪᴅᴇᴏ Cᴏᴜʟᴅ Nᴏᴛ Bᴇ Dᴏᴡɴʟᴏᴀᴅᴇᴅ."
            # Keep the actual error visible for debugging; escape HTML first.
            last_error = next((line.strip() for line in reversed(error_output.splitlines()) if "ERROR:" in line), "")
            if last_error:
                detail += "\n\n<b>Rᴇᴀsᴏɴ:</b> <code>" + escape(last_error[:500]) + "</code>"
            await processing.edit_text("<blockquote><b>" + title + "</b>\n\n" + detail + "</blockquote>")
            return

        files = [os.path.join(temp_dir, name) for name in os.listdir(temp_dir)
                 if os.path.isfile(os.path.join(temp_dir, name)) and
                 name.lower().endswith((".mp4", ".mkv", ".webm", ".mov"))]
        if not files:
            await processing.edit_text(
                "<blockquote><b>❌ Vɪᴅᴇᴏ Fɪʟᴇ Nᴏᴛ Fᴏᴜɴᴅ</b>\n\n"
                "Tʜᴇ Dᴏᴡɴʟᴏᴀᴅ Fᴀɪʟᴇ Cᴏᴜʟᴅ Nᴏᴛ Bᴇ Fᴏᴜɴᴅ."
                "</blockquote>",
            )
            return

        downloaded_file = max(files, key=os.path.getsize)
        file_size = os.path.getsize(downloaded_file)
        if file_size == 0:
            await processing.edit_text(
                "<blockquote><b>❌ Eᴍᴘᴛʏ Vɪᴅᴇᴏ Fɪʟᴇ</b>\n\n"
                "Tʜᴇ Dᴏᴡɴʟᴏᴀᴅᴇᴅ Fɪʟᴇ Wᴀs Eᴍᴘᴛʏ."
                "</blockquote>",
            )
            return

        await processing.edit_text(
            "<blockquote><b>📤 Uᴘʟᴏᴀᴅɪɴɢ Tᴏ Tᴇʟᴇɢʀᴀᴍ...</b>\n\n"
            "Pʟᴇᴀsᴇ Wᴀɪᴛ...</blockquote>",
        )
        await client.send_video(
            chat_id=message.chat.id,
            video=downloaded_file,
            caption=(
                "<blockquote><b>🎬 Iɴsᴛᴀɢʀᴀᴍ Vɪᴅᴇᴏ</b>\n\n"
                "Dᴏᴡɴʟᴏᴀᴅᴇᴅ Bʏ <b><a href='https://t.me/Systumm_music_bot'>Bʀᴀɴᴅʀᴅ Mᴜsɪᴄ</a></b>"
                "</blockquote>"
            ),
            supports_streaming=downloaded_file.lower().endswith(".mp4"),
        )
        await processing.delete()

    except FileNotFoundError:
        logger.exception("Instagram downloader executable not found")
        await processing.edit_text(
            "<blockquote><b>❌ yt-dlp Nᴏᴛ Fᴏᴜɴᴅ</b>\n\n"
            "Pʟᴇᴀsᴇ Aᴅᴅ <code>yt-dlp</code> Tᴏ Yᴏᴜʀ requirements.txt."
            "</blockquote>",
        )
    except Exception as e:
        logger.exception("Instagram Downloader Error")
        try:
            await processing.edit_text(
                "<blockquote><b>❌ Sᴏᴍᴇᴛʜɪɴɢ Wᴇɴᴛ Wʀᴏɴɢ</b>\n\n"
                "<code>" + escape(str(e)[:500]) + "</code></blockquote>",
            )
        except Exception:
            pass
    finally:
        if process is not None and process.returncode is None:
            process.kill()
            await process.communicate()
        shutil.rmtree(temp_dir, ignore_errors=True)
