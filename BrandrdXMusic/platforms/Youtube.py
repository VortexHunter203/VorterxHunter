import asyncio
import os
import re
from typing import Union

import aiohttp
import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from py_yt import VideosSearch, Playlist


# ============================================================
# YOUTUBE STREAM API CONFIG
# ============================================================

PRIMARY_API_URL = os.getenv(
    "API_URL",
    "http://165.232.182.138:8000",
)

FALLBACK_API_URL = os.getenv(
    "API_URL_FALLBACK",
    "https://api.shrutibots.in",
)

API_KEY = os.getenv(
    "API_KEY",
    "ShrutiBots8dd7YecpYDzZ8TjOzDeV",
)

DOWNLOAD_DIR = "downloads"


# ============================================================
# HELPERS
# ============================================================

def time_to_seconds(time):
    stringt = str(time)
    return sum(
        int(x) * 60 ** i
        for i, x in enumerate(reversed(stringt.split(":")))
    )


# ============================================================
# STREAM DOWNLOADER
# PRIMARY API -> FALLBACK API
# ============================================================

async def _stream_to_file(video_id: str, s_type: str) -> str:
    """
    Download YouTube stream.

    Order:
        1. PRIMARY API
        2. FALLBACK API

    If primary API fails for any reason, fallback API is tried.
    """

    ext = "mp4" if s_type == "video" else "webm"

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    path = os.path.join(
        DOWNLOAD_DIR,
        f"{video_id}.{ext}",
    )

    # --------------------------------------------------------
    # Existing file check
    # --------------------------------------------------------

    if os.path.exists(path) and os.path.getsize(path) > 0:
        print(
            f"[YouTube API] Existing file found: "
            f"{video_id}.{ext}"
        )
        return path

    # --------------------------------------------------------
    # API ORDER
    # --------------------------------------------------------

    api_urls = [
        ("PRIMARY", PRIMARY_API_URL),
        ("FALLBACK", FALLBACK_API_URL),
    ]

    # --------------------------------------------------------
    # Try APIs one by one
    # --------------------------------------------------------

    for api_name, api_url in api_urls:

        if not api_url:
            continue

        api_url = api_url.rstrip("/")

        print(
            f"[YouTube API] Trying {api_name}: "
            f"{api_url}"
        )

        # ====================================================
        # HEALTH CHECK
        # ====================================================

        try:
            timeout = aiohttp.ClientTimeout(
                total=30
            )

            async with aiohttp.ClientSession(
                timeout=timeout
            ) as session:

                async with session.get(
                    f"{api_url}/stream",
                    params={
                        "query": video_id,
                        "type": s_type,
                    },
                ) as resp:

                    if resp.status != 200:

                        print(
                            f"[YouTube API] "
                            f"{api_name} health check failed: "
                            f"HTTP {resp.status}"
                        )

                        continue

                    print(
                        f"[YouTube API] "
                        f"{api_name} health check OK"
                    )

        except asyncio.TimeoutError:

            print(
                f"[YouTube API] "
                f"{api_name} health check timeout"
            )

            continue

        except aiohttp.ClientError as e:

            print(
                f"[YouTube API] "
                f"{api_name} connection error: {e}"
            )

            continue

        except Exception as e:

            print(
                f"[YouTube API] "
                f"{api_name} health check error: {e}"
            )

            continue

        # ====================================================
        # DOWNLOAD
        # ====================================================

        tmp = f"{path}.part"

        try:

            # Remove old partial file
            try:
                if os.path.exists(tmp):
                    os.remove(tmp)
            except OSError:
                pass

            timeout = aiohttp.ClientTimeout(
                total=600
            )

            async with aiohttp.ClientSession(
                timeout=timeout
            ) as session:

                async with session.get(
                    f"{api_url}/stream/{s_type}/{video_id}"
                ) as resp:

                    if resp.status != 200:

                        print(
                            f"[YouTube API] "
                            f"{api_name} download failed: "
                            f"HTTP {resp.status}"
                        )

                        continue

                    with open(
                        tmp,
                        "wb",
                    ) as f:

                        async for chunk in resp.content.iter_chunked(
                            1024 * 64
                        ):

                            if chunk:
                                f.write(chunk)

            # =================================================
            # Validate downloaded file
            # =================================================

            if (
                not os.path.exists(tmp)
                or os.path.getsize(tmp) <= 0
            ):

                print(
                    f"[YouTube API] "
                    f"{api_name} returned empty file"
                )

                continue

            # Atomic replace
            os.replace(
                tmp,
                path,
            )

            print(
                f"[YouTube API] "
                f"{api_name} download SUCCESS: "
                f"{video_id} ({s_type})"
            )

            return path

        except asyncio.TimeoutError:

            print(
                f"[YouTube API] "
                f"{api_name} download timeout"
            )

        except aiohttp.ClientError as e:

            print(
                f"[YouTube API] "
                f"{api_name} download connection error: "
                f"{e}"
            )

        except Exception as e:

            print(
                f"[YouTube API] "
                f"{api_name} unexpected download error: "
                f"{e}"
            )

        finally:

            # ------------------------------------------------
            # Always remove partial file
            # ------------------------------------------------

            try:

                if os.path.exists(tmp):
                    os.remove(tmp)

            except OSError:
                pass

    # ========================================================
    # BOTH APIS FAILED
    # ========================================================

    print(
        f"[YouTube API] "
        f"PRIMARY and FALLBACK both failed "
        f"for {video_id} ({s_type})"
    )

    return None


# ============================================================
# DOWNLOAD SONG
# ============================================================

async def download_song(link: str) -> str:

    video_id = (
        link.split("v=")[-1].split("&")[0]
        if "v=" in link
        else link
    )

    if not video_id or len(video_id) < 3:
        return None

    os.makedirs(
        DOWNLOAD_DIR,
        exist_ok=True,
    )

    return await _stream_to_file(
        video_id,
        "audio",
    )


# ============================================================
# DOWNLOAD VIDEO
# ============================================================

async def download_video(link: str) -> str:

    video_id = (
        link.split("v=")[-1].split("&")[0]
        if "v=" in link
        else link
    )

    if not video_id or len(video_id) < 3:
        return None

    os.makedirs(
        DOWNLOAD_DIR,
        exist_ok=True,
    )

    return await _stream_to_file(
        video_id,
        "video",
    )


# ============================================================
# YOUTUBE API CLASS
# ============================================================

class YouTubeAPI:

    def __init__(self):

        self.base = (
            "https://www.youtube.com/watch?v="
        )

        self.regex = r"(?:youtube\.com|youtu\.be)"

        self.status = (
            "https://www.youtube.com/oembed?url="
        )

        self.listbase = (
            "https://youtube.com/playlist?list="
        )

        self.reg = re.compile(
            r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])"
        )

    # ========================================================
    # EXISTS
    # ========================================================

    async def exists(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):

        if videoid:
            link = self.base + link

        return bool(
            re.search(
                self.regex,
                link,
            )
        )

    # ========================================================
    # URL
    # ========================================================

    async def url(
        self,
        message_1: Message,
    ) -> Union[str, None]:

        messages = [message_1]

        if message_1.reply_to_message:
            messages.append(
                message_1.reply_to_message
            )

        for message in messages:

            if message.entities:

                for entity in message.entities:

                    if (
                        entity.type
                        == MessageEntityType.URL
                    ):

                        text = (
                            message.text
                            or message.caption
                        )

                        if text:
                            return text[
                                entity.offset:
                                entity.offset
                                + entity.length
                            ]

            elif message.caption_entities:

                for entity in message.caption_entities:

                    if (
                        entity.type
                        == MessageEntityType.TEXT_LINK
                    ):

                        return entity.url

        return None

    # ========================================================
    # DETAILS
    # ========================================================

    async def details(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):

        if videoid:
            link = self.base + link

        if "&" in link:
            link = link.split("&")[0]

        results = VideosSearch(
            link,
            limit=1,
        )

        for result in (
            await results.next()
        )["result"]:

            title = result["title"]

            duration_min = result["duration"]

            thumbnail = (
                result["thumbnails"][0]["url"]
                .split("?")[0]
            )

            vidid = result["id"]

            duration_sec = (
                int(
                    time_to_seconds(
                        duration_min
                    )
                )
                if duration_min
                else 0
            )

        return (
            title,
            duration_min,
            duration_sec,
            thumbnail,
            vidid,
        )

    # ========================================================
    # TITLE
    # ========================================================

    async def title(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):

        if videoid:
            link = self.base + link

        if "&" in link:
            link = link.split("&")[0]

        results = VideosSearch(
            link,
            limit=1,
        )

        for result in (
            await results.next()
        )["result"]:

            return result["title"]

    # ========================================================
    # DURATION
    # ========================================================

    async def duration(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):

        if videoid:
            link = self.base + link

        if "&" in link:
            link = link.split("&")[0]

        results = VideosSearch(
            link,
            limit=1,
        )

        for result in (
            await results.next()
        )["result"]:

            return result["duration"]

    # ========================================================
    # THUMBNAIL
    # ========================================================

    async def thumbnail(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):

        if videoid:
            link = self.base + link

        if "&" in link:
            link = link.split("&")[0]

        results = VideosSearch(
            link,
            limit=1,
        )

        for result in (
            await results.next()
        )["result"]:

            return (
                result["thumbnails"][0]["url"]
                .split("?")[0]
            )

    # ========================================================
    # VIDEO
    # ========================================================

    async def video(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):

        if videoid:
            link = self.base + link

        if "&" in link:
            link = link.split("&")[0]

        try:

            downloaded_file = (
                await download_video(link)
            )

            if downloaded_file:

                return (
                    1,
                    downloaded_file,
                )

            return (
                0,
                "Video download failed",
            )

        except Exception as e:

            return (
                0,
                f"Video download error: {e}",
            )

    # ========================================================
    # PLAYLIST
    # ========================================================

    async def playlist(
        self,
        link,
        limit,
        user_id,
        videoid: Union[bool, str] = None,
    ):

        if videoid:
            link = self.listbase + link

        if "&" in link:
            link = link.split("&")[0]

        try:

            plist = await Playlist.get(
                link
            )

        except Exception:

            return []

        videos = (
            plist.get("videos")
            or []
        )

        ids = []

        for data in videos[:limit]:

            if not data:
                continue

            vid = data.get("id")

            if not vid:
                continue

            ids.append(vid)

        return ids

    # ========================================================
    # TRACK
    # ========================================================

    async def track(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):

        if videoid:
            link = self.base + link

        if "&" in link:
            link = link.split("&")[0]

        results = VideosSearch(
            link,
            limit=1,
        )

        for result in (
            await results.next()
        )["result"]:

            title = result["title"]

            duration_min = result["duration"]

            vidid = result["id"]

            yturl = result["link"]

            thumbnail = (
                result["thumbnails"][0]["url"]
                .split("?")[0]
            )

        track_details = {
            "title": title,
            "link": yturl,
            "vidid": vidid,
            "duration_min": duration_min,
            "thumb": thumbnail,
        }

        return (
            track_details,
            vidid,
        )

    # ========================================================
    # FORMATS
    # ========================================================

    async def formats(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):

        if videoid:
            link = self.base + link

        if "&" in link:
            link = link.split("&")[0]

        ytdl_opts = {
            "quiet": True,
        }

        ydl = yt_dlp.YoutubeDL(
            ytdl_opts
        )

        with ydl:

            formats_available = []

            r = ydl.extract_info(
                link,
                download=False,
            )

            for format in r["formats"]:

                try:

                    if (
                        "dash"
                        not in str(
                            format["format"]
                        ).lower()
                    ):

                        formats_available.append(
                            {
                                "format": format[
                                    "format"
                                ],
                                "filesize": format.get(
                                    "filesize"
                                ),
                                "format_id": format[
                                    "format_id"
                                ],
                                "ext": format[
                                    "ext"
                                ],
                                "format_note": format[
                                    "format_note"
                                ],
                                "yturl": link,
                            }
                        )

                except Exception:

                    continue

        return (
            formats_available,
            link,
        )

    # ========================================================
    # SLIDER
    # ========================================================

    async def slider(
        self,
        link: str,
        query_type: int,
        videoid: Union[bool, str] = None,
    ):

        if videoid:
            link = self.base + link

        if "&" in link:
            link = link.split("&")[0]

        a = VideosSearch(
            link,
            limit=10,
        )

        result = (
            await a.next()
        ).get("result")

        title = result[
            query_type
        ]["title"]

        duration_min = result[
            query_type
        ]["duration"]

        vidid = result[
            query_type
        ]["id"]

        thumbnail = (
            result[
                query_type
            ]["thumbnails"][0]["url"]
            .split("?")[0]
        )

        return (
            title,
            duration_min,
            thumbnail,
            vidid,
        )

    # ========================================================
    # DOWNLOAD
    # ========================================================

    async def download(
        self,
        link: str,
        mystic,
        video: Union[bool, str] = None,
        videoid: Union[bool, str] = None,
        songaudio: Union[bool, str] = None,
        songvideo: Union[bool, str] = None,
        format_id: Union[bool, str] = None,
        title: Union[bool, str] = None,
    ) -> str:

        if videoid:
            link = self.base + link

        try:

            if video:

                downloaded_file = (
                    await download_video(link)
                )

            else:

                downloaded_file = (
                    await download_song(link)
                )

            if downloaded_file:

                return (
                    downloaded_file,
                    True,
                )

            return (
                None,
                False,
            )

        except Exception:

            return (
                None,
                False,
            )


# ============================================================
# YOUTUBE INSTANCE
# ============================================================

YouTube = YouTubeAPI()
