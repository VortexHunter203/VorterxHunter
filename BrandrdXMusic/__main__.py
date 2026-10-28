import asyncio
import logging

import config
from pyrogram import idle
from pytgcalls.exceptions import NoActiveGroupCall

from BrandrdXMusic import LOGGER, app, userbot
from BrandrdXMusic.core.call import Hotty
from BrandrdXMusic.misc import sudo
from BrandrdXMusic.plugins import ALL_MODULES
from BrandrdXMusic.utils.database import get_banned_users, get_gbanned
from config import BANNED_USERS


# --------------------------------------------- #
# BOT INITIALIZATION
# --------------------------------------------- #

async def init():
    if not any(
        [
            config.STRING1,
            config.STRING2,
            config.STRING3,
            config.STRING4,
            config.STRING5,
        ]
    ):
        LOGGER("BrandrdXMusic").error(
            "Assistant client variables not defined, exiting..."
        )
        return

    await sudo()

    try:
        users = await get_gbanned()
        for user_id in users:
            BANNED_USERS.add(user_id)

        users = await get_banned_users()
        for user_id in users:
            BANNED_USERS.add(user_id)

    except Exception:
        LOGGER("BrandrdXMusic").exception(
            "Could not load banned users."
        )

    await app.start()

    # Load existing music bot plugins.
    for all_module in ALL_MODULES:
        try:
            importlib.import_module(
                "BrandrdXMusic.plugins" + all_module
            )
        except Exception:
            LOGGER("BrandrdXMusic.plugins").exception(
                "Failed to load plugin: %s", all_module
            )

    LOGGER("BrandrdXMusic.plugins").info(
        "Successfully imported music bot modules."
    )

    await userbot.start()
    await Hotty.start()

    try:
        await Hotty.stream_call(
            "https://graph.org/file/e999c40cb700e7c684b75.mp4"
        )

    except NoActiveGroupCall:
        LOGGER("BrandrdXMusic").error(
            "Please turn on the videochat of your log group/channel."
        )
        await Hotty.stop()
        await userbot.stop()
        await app.stop()
        return

    except Exception:
        LOGGER("BrandrdXMusic").exception(
            "Could not start the initial stream. Continuing..."
        )

    await Hotty.decorators()

    LOGGER("BrandrdXMusic").info(
    "ᴅʀᴏᴘ ʏᴏᴜʀ ɢɪʀʟꜰʀɪᴇɴᴅ'ꜱ ɴᴜᴍʙᴇʀ ᴀᴛ @BRANDED_PAID_CC ᴊᴏɪɴ @BRANDRD_BOT , @BRANDEDKING8 ꜰᴏʀ ᴀɴʏ ɪꜱꜱᴜᴇꜱ"
            )

    try:
        await idle()
    finally:
        await Hotty.stop()
        await userbot.stop()
        await app.stop()

        LOGGER("BrandrdXMusic").info(
            "Stopping BrandrdXMusic bot..."
        )


if __name__ == "__main__":
    logging.getLogger("telethon.crypto.aes").setLevel(logging.WARNING)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(init())
