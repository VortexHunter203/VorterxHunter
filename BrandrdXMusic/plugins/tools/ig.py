import os
import asyncio
import tempfile

from pyrogram import filters
from BrandrdXMusic import app


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

    if not (
        "instagram.com/" in url
        or "www.instagram.com/" in url
        or "instagr.am/" in url
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

    try:
        await processing.edit_text(
            "<blockquote>"
            "<b>⬇️ Dᴏᴡɴʟᴏᴀᴅɪɴɢ Iɴsᴛᴀɢʀᴀᴍ Vɪᴅᴇᴏ...</b>\n\n"
            "Pʟᴇᴀsᴇ Wᴀɪᴛ..."
            "</blockquote>",
        )

        process = await asyncio.create_subprocess_exec(
            "yt-dlp",
            "--no-playlist",
            "--no-warnings",
            "--restrict-filenames",
            "-f",
            "best[ext=mp4]/best",
            "-o",
            output_template,
            url,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await process.communicate()

        error_output = stderr.decode(
            "utf-8",
            errors="ignore",
        )

        if process.returncode != 0:
            print("Instagram yt-dlp error:")
            print(error_output[:4000])

            error_lower = error_output.lower()

            if (
                "login required" in error_lower
                or "login" in error_lower
            ):
                await processing.edit_text(
                    "<blockquote>"
                    "<b>❌ Lᴏɢɪɴ Rᴇǫᴜɪʀᴇᴅ</b>\n\n"
                    "Tʜɪs Iɴsᴛᴀɢʀᴀᴍ Cᴏɴᴛᴇɴᴛ Rᴇǫᴜɪʀᴇs Lᴏɢɪɴ."
                    "</blockquote>",
                )

            elif "private" in error_lower:
                await processing.edit_text(
                    "<blockquote>"
                    "<b>❌ Pʀɪᴠᴀᴛᴇ Cᴏɴᴛᴇɴᴛ</b>\n\n"
                    "Pʀɪᴠᴀᴛᴇ Iɴsᴛᴀɢʀᴀᴍ Cᴏɴᴛᴇɴᴛ Cᴀɴɴᴏᴛ Bᴇ Dᴏᴡɴʟᴏᴀᴅᴇᴅ."
                    "</blockquote>",
                )

            elif "not found" in error_lower:
                await processing.edit_text(
                    "<blockquote>"
                    "<b>❌ Vɪᴅᴇᴏ Nᴏᴛ Fᴏᴜɴᴅ</b>\n\n"
                    "Tʜᴇ Iɴsᴛᴀɢʀᴀᴍ Vɪᴅᴇᴏ Cᴏᴜʟᴅ Nᴏᴛ Bᴇ Fᴏᴜɴᴅ."
                    "</blockquote>",
                )

            else:
                await processing.edit_text(
                    "<blockquote>"
                    "<b>❌ Fᴀɪʟᴇᴅ Tᴏ Dᴏᴡɴʟᴏᴀᴅ</b>\n\n"
                    "Tʜᴇ Iɴsᴛᴀɢʀᴀᴍ Vɪᴅᴇᴏ Cᴏᴜʟᴅ Nᴏᴛ Bᴇ Dᴏᴡɴʟᴏᴀᴅᴇᴅ."
                    "</blockquote>",
                )

            return

        downloaded_file = None

        for filename in os.listdir(temp_dir):
            filepath = os.path.join(temp_dir, filename)

            if os.path.isfile(filepath):
                downloaded_file = filepath
                break

        if not downloaded_file:
            await processing.edit_text(
                "<blockquote>"
                "<b>❌ Vɪᴅᴇᴏ Fɪʟᴇ Nᴏᴛ Fᴏᴜɴᴅ</b>\n\n"
                "Tʜᴇ Dᴏᴡɴʟᴏᴀᴅ Fᴀɪʟᴇ Cᴏᴜʟᴅ Nᴏᴛ Bᴇ Fᴏᴜɴᴅ."
                "</blockquote>",
            )
            return

        file_size = os.path.getsize(downloaded_file)

        if file_size == 0:
            await processing.edit_text(
                "<blockquote>"
                "<b>❌ Eᴍᴘᴛʏ Vɪᴅᴇᴏ Fɪʟᴇ</b>\n\n"
                "Tʜᴇ Dᴏᴡɴʟᴏᴀᴅᴇᴅ Fɪʟᴇ Wᴀs Eᴍᴘᴛʏ."
                "</blockquote>",
            )
            return

        await processing.edit_text(
            "<blockquote>"
            "<b>📤 Uᴘʟᴏᴀᴅɪɴɢ Tᴏ Tᴇʟᴇɢʀᴀᴍ...</b>\n\n"
            "Pʟᴇᴀsᴇ Wᴀɪᴛ..."
            "</blockquote>",
        )

        await client.send_video(
            chat_id=message.chat.id,
            video=downloaded_file,
            caption=(
                "<blockquote>"
                "<b>🎬 Iɴsᴛᴀɢʀᴀᴍ Vɪᴅᴇᴏ</b>\n\n"
                "Dᴏᴡɴʟᴏᴀᴅᴇᴅ Bʏ <b>[Bʀᴀɴᴅʀᴅ Mᴜsɪᴄ](https://t.me/Systumm_music_bot)</b>"
                "</blockquote>"
            ),
            supports_streaming=True,
        )

        await processing.delete()

    except FileNotFoundError:
        print("yt-dlp is not installed or not available in PATH.")

        await processing.edit_text(
            "<blockquote>"
            "<b>❌ yt-dlp Nᴏᴛ Fᴏᴜɴᴅ</b>\n\n"
            "Pʟᴇᴀsᴇ Aᴅᴅ <code>yt-dlp</code> Tᴏ Yᴏᴜʀ requirements.txt."
            "</blockquote>",
        )

    except Exception as e:
        print(f"Instagram Downloader Error: {e}")

        try:
            await processing.edit_text(
                "<blockquote>"
                "<b>❌ Sᴏᴍᴇᴛʜɪɴɢ Wᴇɴᴛ Wʀᴏɴɢ</b>\n\n"
                "Uɴᴀʙʟᴇ Tᴏ Dᴏᴡɴʟᴏᴀᴅ Tʜɪs Iɴsᴛᴀɢʀᴀᴍ Vɪᴅᴇᴏ."
                "</blockquote>",
            )
        except Exception:
            pass

    finally:
        try:
            if os.path.exists(temp_dir):
                for filename in os.listdir(temp_dir):
                    filepath = os.path.join(temp_dir, filename)

                    try:
                        if os.path.isfile(filepath):
                            os.remove(filepath)
                    except Exception:
                        pass

                try:
                    os.rmdir(temp_dir)
                except Exception:
                    pass

        except Exception as e:
            print(f"Cleanup Error: {e}")


__MODULE__ = "Iɴsᴛᴀɢʀᴀᴍ"

__HELP__ = """
/reel [ɪɴsᴛᴀɢʀᴀᴍ ʀᴇᴇʟ ᴜʀʟ] - Tᴏ Dᴏᴡɴʟᴏᴀᴅ Tʜᴇ Rᴇᴇʟ Bʏ Bᴏᴛ

/ig [ɪɴsᴛᴀɢʀᴀᴍ ʀᴇᴇʟ ᴜʀʟ] - Tᴏ Dᴏᴡɴʟᴏᴀᴅ Tʜᴇ Rᴇᴇʟ Bʏ Bᴏᴛ

/instagram [ɪɴsᴛᴀɢʀᴀᴍ ʀᴇᴇʟ ᴜʀʟ] - Tᴏ Dᴏᴡɴʟᴏᴀᴅ Tʜᴇ Rᴇᴇʟ Bʏ Bᴏᴛ
"""
