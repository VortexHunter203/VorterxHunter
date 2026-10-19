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
