import asyncio
import os
import re
from typing import Union

import aiohttp
import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from py_yt import VideosSearch, Playlist

from BrandrdXMusic.logging import LOGGER


API_URL = os.getenv("API_URL", "").rstrip("/")
DOWNLOAD_DIR = "downloads"

AUTOPLAY_REQUEST_TIMEOUT = 20
AUTOPLAY_MAX_RETRIES = 3
AUTOPLAY_RETRY_DELAY = 1

AUTOPLAY_RETRYABLE_STATUS = (
    408, 425, 429, 500, 502, 503, 504
)

DOWNLOAD_TIMEOUT = 600
DOWNLOAD_CONNECT_TIMEOUT = 30
DOWNLOAD_RETRIES = 2


def is_external_path(path):
    if not path or not isinstance(path, str):
        return False

    if path.startswith(("http://", "https://")):
        return True

    try:
        download_root = os.path.abspath(DOWNLOAD_DIR)
        file_path = os.path.abspath(path)

        return os.path.commonpath(
            [download_root, file_path]
        ) != download_root

    except (ValueError, OSError):
        return True


def extract_video_id(link):
    if not link:
        return None

    link = str(link).strip()

    patterns = [
        r"(?:youtube\.com/watch\?v=)([a-zA-Z0-9_-]{11})",
        r"(?:youtu\.be/)([a-zA-Z0-9_-]{11})",
        r"(?:youtube\.com/shorts/)([a-zA-Z0-9_-]{11})",
        r"(?:youtube\.com/embed/)([a-zA-Z0-9_-]{11})",
    ]

    for pattern in patterns:
        match = re.search(pattern, link)
        if match:
            return match.group(1)

    if re.fullmatch(r"[a-zA-Z0-9_-]{11}", link):
        return link

    if "v=" in link:
        video_id = link.split("v=", 1)[1].split("&")[0]

        if re.fullmatch(r"[a-zA-Z0-9_-]{11}", video_id):
            return video_id

    return None


async def get_autoplay(
    video_id: str,
    timeout: int = AUTOPLAY_REQUEST_TIMEOUT,
    retries: int = AUTOPLAY_MAX_RETRIES,
    seed_id: str = None,
) -> list:

    video_id = extract_video_id(video_id)

    if not video_id or not API_URL:
        LOGGER(__name__).warning(
            "Autoplay skipped: invalid video ID or missing API_URL"
        )
        return []

    params = {"video_id": video_id}

    if seed_id and seed_id != video_id:
        params["seed_id"] = (
            extract_video_id(seed_id) or seed_id
        )

    try:
        async with aiohttp.ClientSession() as session:

            for attempt in range(retries):
                try:
                    async with session.get(
                        f"{API_URL}/autoplay",
                        params=params,
                        timeout=aiohttp.ClientTimeout(total=timeout),
                    ) as resp:

                        if resp.status == 200:
                            data = await resp.json()

                            if isinstance(data, dict):
                                tracks = data.get("tracks", [])

                                if isinstance(tracks, list):
                                    return tracks

                            LOGGER(__name__).warning(
                                "Autoplay API returned invalid JSON structure"
                            )
                            return []

                        if resp.status == 404:
                            LOGGER(__name__).error(
                                "Autoplay endpoint not found: %s/autoplay",
                                API_URL,
                            )
                            return []

                        LOGGER(__name__).warning(
                            "Autoplay API HTTP %s",
                            resp.status,
                        )

                        if (
                            resp.status in AUTOPLAY_RETRYABLE_STATUS
                            and attempt + 1 < retries
                        ):
                            await asyncio.sleep(
                                AUTOPLAY_RETRY_DELAY
                            )
                            continue

                        return []

                except asyncio.TimeoutError:
                    LOGGER(__name__).warning(
                        "Autoplay request timeout (%s/%s)",
                        attempt + 1,
                        retries,
                    )

                except aiohttp.ClientError:
                    LOGGER(__name__).warning(
                        "Autoplay connection error",
                        exc_info=True,
                    )

                if attempt + 1 < retries:
                    await asyncio.sleep(
                        AUTOPLAY_RETRY_DELAY
                    )

    except Exception:
        LOGGER(__name__).error(
            "Autoplay session failed",
            exc_info=True,
        )

    return []


def time_to_seconds(time):
    stringt = str(time)

    try:
        return sum(
            int(x) * 60 ** i
            for i, x in enumerate(
                reversed(stringt.split(":"))
            )
        )
    except (ValueError, TypeError):
        return 0


async def _stream_to_file(
    video_id: str,
    s_type: str,
) -> str:

    video_id = extract_video_id(video_id)

    if not video_id or s_type not in ("audio", "video"):
        return None

    if not API_URL:
        LOGGER(__name__).error(
            "YouTube API_URL is missing in Config Vars"
        )
        return None

    ext = "mp4" if s_type == "video" else "webm"

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    path = os.path.join(
        DOWNLOAD_DIR,
        f"{video_id}.{ext}",
    )

    tmp = f"{path}.part"

    if os.path.exists(path):
        try:
            if os.path.getsize(path) > 0:
                return path
        except OSError:
            pass

    for attempt in range(DOWNLOAD_RETRIES + 1):

        try:
            timeout = aiohttp.ClientTimeout(
                total=DOWNLOAD_TIMEOUT,
                connect=DOWNLOAD_CONNECT_TIMEOUT,
            )

            async with aiohttp.ClientSession() as session:

                # API health check
                async with session.get(
                    f"{API_URL}/stream",
                    params={
                        "query": video_id,
                        "type": s_type,
                    },
                    timeout=timeout,
                ) as resp:

                    if resp.status != 200:
                        LOGGER(__name__).warning(
                            "YouTube API health failed: HTTP %s | %s",
                            resp.status,
                            video_id,
                        )

                        if (
                            resp.status in AUTOPLAY_RETRYABLE_STATUS
                            and attempt < DOWNLOAD_RETRIES
                        ):
                            await asyncio.sleep(
                                AUTOPLAY_RETRY_DELAY
                            )
                            continue

                        return None

                # Download through API
                async with session.get(
                    f"{API_URL}/stream/{s_type}/{video_id}",
                    timeout=timeout,
                ) as resp:

                    if resp.status != 200:
                        LOGGER(__name__).warning(
                            "YouTube stream failed: HTTP %s | %s",
                            resp.status,
                            video_id,
                        )

                        if (
                            resp.status in AUTOPLAY_RETRYABLE_STATUS
                            and attempt < DOWNLOAD_RETRIES
                        ):
                            await asyncio.sleep(
                                AUTOPLAY_RETRY_DELAY
                            )
                            continue

                        return None

                    content_type = resp.headers.get(
                        "Content-Type", ""
                    ).lower()

                    if "application/json" in content_type:
                        LOGGER(__name__).error(
                            "YouTube API returned JSON instead of media: %s",
                            video_id,
                        )
                        return None

                    with open(tmp, "wb") as file:
                        async for chunk in resp.content.iter_chunked(
                            65536
                        ):
                            file.write(chunk)

            if (
                not os.path.exists(tmp)
                or os.path.getsize(tmp) == 0
            ):
                LOGGER(__name__).error(
                    "YouTube API returned empty file: %s",
                    video_id,
                )

                if attempt < DOWNLOAD_RETRIES:
                    await asyncio.sleep(
                        AUTOPLAY_RETRY_DELAY
                    )
                    continue

                return None

            os.replace(tmp, path)

            LOGGER(__name__).info(
                "YouTube download successful: %s",
                video_id,
            )

            return path

        except asyncio.TimeoutError:
            LOGGER(__name__).warning(
                "YouTube download timeout: %s",
                video_id,
            )

        except aiohttp.ClientError:
            LOGGER(__name__).warning(
                "YouTube API connection error: %s",
                video_id,
                exc_info=True,
            )

        except Exception:
            LOGGER(__name__).error(
                "YouTube extraction error: %s",
                video_id,
                exc_info=True,
            )

        finally:
            try:
                if os.path.exists(tmp):
                    os.remove(tmp)
            except OSError:
                pass

        if attempt < DOWNLOAD_RETRIES:
            await asyncio.sleep(
                AUTOPLAY_RETRY_DELAY
            )

    return None


async def download_song(link: str) -> str:
    video_id = extract_video_id(link)

    if not video_id:
        return None

    return await _stream_to_file(video_id, "audio")


async def download_video(link: str) -> str:
    video_id = extract_video_id(link)

    if not video_id:
        return None

    return await _stream_to_file(video_id, "video")


class YouTubeAPI:

    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.status = "https://www.youtube.com/oembed?url="
        self.listbase = "https://youtube.com/playlist?list="
        self.reg = re.compile(
            r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])"
        )

    async def exists(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):
        if videoid:
            link = self.base + link

        return bool(
            re.search(self.regex, link)
        )

    async def url(self, message_1: Message):
        messages = [message_1]

        if message_1.reply_to_message:
            messages.append(
                message_1.reply_to_message
            )

        for message in messages:

            if message.entities:
                for entity in message.entities:
                    if entity.type == MessageEntityType.URL:
                        text = message.text or message.caption

                        if text:
                            return text[
                                entity.offset:
                                entity.offset + entity.length
                            ]

            if message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url

        return None

    async def details(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):
        if videoid:
            link = self.base + link

        if "&" in link:
            link = link.split("&")[0]

        results = VideosSearch(link, limit=1)
        data = (
            await results.next()
        ).get("result", [])

        if not data:
            return None, None, 0, None, None

        result = data[0]

        title = result["title"]
        duration_min = result.get("duration")
        thumbnail = (
            result["thumbnails"][0]["url"].split("?")[0]
        )
        vidid = result["id"]

        duration_sec = (
            time_to_seconds(duration_min)
            if duration_min else 0
        )

        return (
            title,
            duration_min,
            duration_sec,
            thumbnail,
            vidid,
        )

    async def title(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):
        details = await self.details(link, videoid)
        return details[0]

    async def duration(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):
        details = await self.details(link, videoid)
        return details[1]

    async def thumbnail(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):
        details = await self.details(link, videoid)
        return details[3]

    async def video(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):
        if videoid:
            link = self.base + link

        try:
            downloaded_file = await download_video(link)

            if downloaded_file:
                return 1, downloaded_file

            return 0, "Video download failed"

        except Exception as e:
            LOGGER(__name__).error(
                "YouTube video error",
                exc_info=True,
            )
            return 0, f"Video download error: {e}"

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
            plist = await Playlist.get(link)
        except Exception:
            LOGGER(__name__).error(
                "YouTube playlist error",
                exc_info=True,
            )
            return []

        videos = plist.get("videos") or []
        ids = []

        for data in videos[:limit]:
            if not data:
                continue

            vid = data.get("id")

            if vid:
                ids.append(vid)

        return ids

    async def track(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):
        if videoid:
            link = self.base + link

        if "&" in link:
            link = link.split("&")[0]

        results = VideosSearch(link, limit=1)
        data = (
            await results.next()
        ).get("result", [])

        if not data:
            return None, None

        result = data[0]

        track_details = {
            "title": result["title"],
            "link": result["link"],
            "vidid": result["id"],
            "duration_min": result.get("duration"),
            "thumb": (
                result["thumbnails"][0]["url"].split("?")[0]
            ),
        }

        return track_details, result["id"]

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
            "no_warnings": True,
        }

        try:
            with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
                result = ydl.extract_info(
                    link,
                    download=False,
                )

                formats_available = []

                for fmt in result.get("formats", []):
                    if "dash" not in str(
                        fmt.get("format", "")
                    ).lower():

                        formats_available.append({
                            "format": fmt.get("format"),
                            "filesize": fmt.get("filesize"),
                            "format_id": fmt.get("format_id"),
                            "ext": fmt.get("ext"),
                            "format_note": fmt.get("format_note"),
                            "yturl": link,
                        })

                return formats_available, link

        except Exception:
            LOGGER(__name__).error(
                "YouTube formats extraction failed",
                exc_info=True,
            )
            return [], link

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

        search = VideosSearch(link, limit=10)
        results = (
            await search.next()
        ).get("result", [])

        if not results or query_type >= len(results):
            return None, None, None, None

        result = results[query_type]

        return (
            result["title"],
            result.get("duration"),
            result["thumbnails"][0]["url"].split("?")[0],
            result["id"],
        )

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
                downloaded_file = await download_video(link)
            else:
                downloaded_file = await download_song(link)

            if downloaded_file:
                return downloaded_file, True

            return None, False

        except Exception:
            LOGGER(__name__).error(
                "YouTube download failed",
                exc_info=True,
            )
            return None, False


YouTube = YouTubeAPI()
