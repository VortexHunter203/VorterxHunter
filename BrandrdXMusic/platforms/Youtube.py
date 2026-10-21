import asyncio
import logging
import os
import re
from typing import Union

import aiohttp
import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from py_yt import VideosSearch, Playlist

LOGGER = logging.getLogger(__name__)

# PRIMARY API
PRIMARY_API_URL = os.environ.get(
    "PRIMARY_API_URL",
    os.environ.get("API_URL", ""),
).strip().rstrip("/")

# FALLBACK API
FALLBACK_API_URL = os.environ.get(
    "FALLBACK_API_URL", ""
).strip().rstrip("/")

FALLBACK_API_KEY = os.environ.get(
    "FALLBACK_API_KEY", ""
).strip()

# API URL and API KEY pairs
# FIXED: Every entry contains exactly two values.
API_LIST = [
    (url, key)
    for url, key in [
        (PRIMARY_API_URL, ),
        (FALLBACK_API_URL, FALLBACK_API_KEY),
    ]
    if url
]

DOWNLOAD_DIR = "downloads"

AUTOPLAY_REQUEST_TIMEOUT = 20
AUTOPLAY_MAX_RETRIES = 3
AUTOPLAY_RETRY_DELAY = 1

AUTOPLAY_RETRYABLE_STATUS = (
    408, 425, 429, 500, 502, 503, 504
)


def is_external_path(path):
    return bool(path and os.path.isfile(path))


def time_to_seconds(time):
    stringt = str(time)
    return sum(
        int(x) * 60 ** i
        for i, x in enumerate(reversed(stringt.split(":")))
    )


def _extract_video_id(link: str) -> str:
    """Extract a YouTube video ID from common YouTube URL formats."""
    if not link:
        return ""

    link = str(link).strip()

    patterns = [
        r"(?:youtube\.com/watch\?.*?\bv=)([A-Za-z0-9_-]{11})",
        r"(?:youtu\.be/)([A-Za-z0-9_-]{11})",
        r"(?:youtube\.com/shorts/)([A-Za-z0-9_-]{11})",
        r"(?:youtube\.com/embed/)([A-Za-z0-9_-]{11})",
        r"(?:youtube\.com/live/)([A-Za-z0-9_-]{11})",
    ]

    for pattern in patterns:
        match = re.search(pattern, link)
        if match:
            return match.group(1)

    if re.fullmatch(r"[A-Za-z0-9_-]{11}", link):
        return link

    return ""


async def _stream_to_file(
    video_id: str,
    s_type: str,
) -> Union[str, None]:
    """Download media using the configured /download API endpoints."""
    video_id = _extract_video_id(video_id)

    if not video_id:
        LOGGER.error("YouTube download: invalid video ID")
        return None

    if s_type not in ("audio", "video"):
        LOGGER.error(
            "YouTube download: unsupported media type: %s",
            s_type,
        )
        return None

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    ext = "mp4" if s_type == "video" else "webm"
    path = os.path.abspath(
        os.path.join(DOWNLOAD_DIR, f"{video_id}.{ext}")
    )
    tmp = f"{path}.part"

    if os.path.isfile(path) and os.path.getsize(path) > 0:
        LOGGER.info(
            "YouTube download: using cached file for %s",
            video_id,
        )
        return path

    if not API_LIST:
        LOGGER.error(
            "YouTube download: no API configured. Set PRIMARY_API_URL "
            "or API_URL, or configure FALLBACK_API_URL."
        )
        return None

    timeout = aiohttp.ClientTimeout(
        total=600,
        connect=30,
        sock_connect=30,
        sock_read=120,
    )

    # Pass the full YouTube URL to the API.
    youtube_url = f"https://www.youtube.com/watch?v={video_id}"

    for api_url, api_key in API_LIST:
        headers = {}
        params = {
            "url": youtube_url,
            "type": s_type,
        }

        if api_key:
            params["api_key"] = api_key
            headers["Authorization"] = f"Bearer {api_key}"

        download_url = f"{api_url}/download"

        try:
            LOGGER.info(
                "YouTube download: trying API %s for %s (%s)",
                download_url,
                video_id,
                s_type,
            )

            async with aiohttp.ClientSession(
                timeout=timeout
            ) as session:
                try:
                    async with session.get(
                        download_url,
                        params=params,
                        headers=headers,
                    ) as resp:
                        if resp.status != 200:
                            body = (await resp.text())[:500]
                            LOGGER.warning(
                                "YouTube API download failed: "
                                "url=%s status=%s body=%s",
                                resp.url,
                                resp.status,
                                body,
                            )
                            continue

                        content_type = resp.headers.get(
                            "Content-Type", ""
                        ).lower()

                        # Do not save JSON or HTML errors as media.
                        if (
                            "json" in content_type
                            or "text/html" in content_type
                        ):
                            body = (await resp.text())[:1000]
                            LOGGER.error(
                                "YouTube API returned a response "
                                "instead of media: url=%s body=%s",
                                resp.url,
                                body,
                            )
                            continue

                        bytes_written = 0

                        try:
                            with open(tmp, "wb") as file:
                                async for chunk in (
                                    resp.content.iter_chunked(65536)
                                ):
                                    if not chunk:
                                        continue

                                    file.write(chunk)
                                    bytes_written += len(chunk)

                        except Exception:
                            if os.path.exists(tmp):
                                os.remove(tmp)
                            raise

                except (aiohttp.ClientError, asyncio.TimeoutError):
                    LOGGER.exception(
                        "YouTube API request failed: %s",
                        download_url,
                    )
                    continue

                if (
                    os.path.isfile(tmp)
                    and os.path.getsize(tmp) > 0
                    and bytes_written > 0
                ):
                    os.replace(tmp, path)

                    LOGGER.info(
                        "YouTube download successful: "
                        "id=%s type=%s size=%s path=%s",
                        video_id,
                        s_type,
                        os.path.getsize(path),
                        path,
                    )
                    return path

                LOGGER.warning(
                    "YouTube API returned an empty file: %s",
                    download_url,
                )

        except Exception:
            LOGGER.exception(
                "Unexpected YouTube API error: %s",
                api_url,
            )

        finally:
            try:
                if os.path.exists(tmp):
                    os.remove(tmp)
            except OSError:
                LOGGER.warning(
                    "Could not remove temporary download file: %s",
                    tmp,
                )

    LOGGER.error(
        "YouTube download failed on all configured APIs: "
        "id=%s type=%s",
        video_id,
        s_type,
    )
    return None


async def download_song(link: str) -> Union[str, None]:
    video_id = _extract_video_id(link)

    if not video_id:
        LOGGER.error(
            "download_song: invalid YouTube link or video ID"
        )
        return None

    return await _stream_to_file(video_id, "audio")


async def download_video(link: str) -> Union[str, None]:
    video_id = _extract_video_id(link)

    if not video_id:
        LOGGER.error(
            "download_video: invalid YouTube link or video ID"
        )
        return None

    return await _stream_to_file(video_id, "video")


async def get_autoplay(
    video_id: str,
    timeout: int = AUTOPLAY_REQUEST_TIMEOUT,
    retries: int = AUTOPLAY_MAX_RETRIES,
    seed_id: str = None,
) -> list:
    video_id = _extract_video_id(video_id)

    if not video_id or not FALLBACK_API_URL:
        LOGGER.warning(
            "Autoplay unavailable: invalid video ID or "
            "FALLBACK_API_URL not configured"
        )
        return []

    params = {"video_id": video_id}

    if FALLBACK_API_KEY:
        params["api_key"] = FALLBACK_API_KEY

    if seed_id:
        seed_id = _extract_video_id(seed_id) or seed_id
        if seed_id != video_id:
            params["seed_id"] = seed_id

    headers = {}
    if FALLBACK_API_KEY:
        headers["Authorization"] = f"Bearer {FALLBACK_API_KEY}"

    for attempt in range(1, retries + 1):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{FALLBACK_API_URL}/autoplay",
                    params=params,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=timeout),
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get("tracks", [])

                    body = (await resp.text())[:300]
                    LOGGER.warning(
                        "Autoplay API returned status %s: %s",
                        resp.status,
                        body,
                    )

                    if (
                        resp.status in AUTOPLAY_RETRYABLE_STATUS
                        and attempt < retries
                    ):
                        await asyncio.sleep(AUTOPLAY_RETRY_DELAY)
                        continue

                    return []

        except (asyncio.TimeoutError, aiohttp.ClientError):
            LOGGER.exception(
                "Autoplay API request failed (attempt %s/%s)",
                attempt,
                retries,
            )

            if attempt < retries:
                await asyncio.sleep(AUTOPLAY_RETRY_DELAY)
                continue

            return []

        except Exception:
            LOGGER.exception("Unexpected autoplay API error")
            return []

    return []


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
        return bool(re.search(self.regex, link))

    async def url(self, message_1: Message) -> Union[str, None]:
        messages = [message_1]

        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)

        for message in messages:
            if message.entities:
                for entity in message.entities:
                    if entity.type == MessageEntityType.URL:
                        text = message.text or message.caption or ""
                        return text[
                            entity.offset:entity.offset + entity.length
                        ]

            elif message.caption_entities:
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
        data = (await results.next()).get("result", [])

        for result in data:
            title = result["title"]
            duration_min = result["duration"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            vidid = result["id"]
            duration_sec = (
                int(time_to_seconds(duration_min))
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

        return None

    async def title(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):
        if videoid:
            link = self.base + link

        if "&" in link:
            link = link.split("&")[0]

        results = VideosSearch(link, limit=1)
        for result in (await results.next()).get("result", []):
            return result["title"]

        return None

    async def duration(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):
        if videoid:
            link = self.base + link

        if "&" in link:
            link = link.split("&")[0]

        results = VideosSearch(link, limit=1)
        for result in (await results.next()).get("result", []):
            return result["duration"]

        return None

    async def thumbnail(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):
        if videoid:
            link = self.base + link

        if "&" in link:
            link = link.split("&")[0]

        results = VideosSearch(link, limit=1)
        for result in (await results.next()).get("result", []):
            thumbnails = result.get("thumbnails", [])
            if thumbnails:
                return thumbnails[0]["url"].split("?")[0]

        return None

    async def video(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):
        if videoid:
            link = self.base + link

        try:
            downloaded_file = await download_video(link)

            if downloaded_file and os.path.isfile(downloaded_file):
                return 1, downloaded_file

            return (
                0,
                "Video download failed. Check the YouTube API logs.",
            )

        except Exception as exc:
            LOGGER.exception("YouTube video resolution failed")
            return 0, f"Video download error: {exc}"

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
            LOGGER.exception("YouTube playlist retrieval failed")
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

        for result in (await results.next()).get("result", []):
            title = result["title"]
            duration_min = result["duration"]
            vidid = result["id"]
            yturl = result["link"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]

            track_details = {
                "title": title,
                "link": yturl,
                "vidid": vidid,
                "duration_min": duration_min,
                "thumb": thumbnail,
            }

            return track_details, vidid

        return None, None

    async def formats(
        self,
        link: str,
        videoid: Union[bool, str] = None,
    ):
        if videoid:
            link = self.base + link

        if "&" in link:
            link = link.split("&")[0]

        ytdl_opts = {"quiet": True}
        ydl = yt_dlp.YoutubeDL(ytdl_opts)

        with ydl:
            formats_available = []
            info = ydl.extract_info(link, download=False)

            for fmt in info.get("formats", []):
                try:
                    if "dash" not in str(
                        fmt.get("format", "")
                    ).lower():
                        formats_available.append(
                            {
                                "format": fmt.get("format"),
                                "filesize": fmt.get("filesize"),
                                "format_id": fmt.get("format_id"),
                                "ext": fmt.get("ext"),
                                "format_note": fmt.get("format_note"),
                                "yturl": link,
                            }
                        )
                except Exception:
                    continue

        return formats_available, link

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
        results = (await search.next()).get("result", [])

        if not results or query_type >= len(results):
            raise ValueError(
                "No YouTube search result at the requested index"
            )

        result = results[query_type]

        return (
            result["title"],
            result["duration"],
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
    ):
        if videoid:
            link = self.base + link

        try:
            if video:
                downloaded_file = await download_video(link)
            else:
                downloaded_file = await download_song(link)

            if (
                downloaded_file
                and os.path.isfile(downloaded_file)
                and os.path.getsize(downloaded_file) > 0
            ):
                return downloaded_file, True

            LOGGER.error(
                "YouTube.download returned no valid file. "
                "link=%s video=%s",
                link,
                bool(video),
            )
            return None, False

        except Exception:
            LOGGER.exception(
                "YouTube.download failed for %s",
                link,
            )
            return None, False


YouTube = YouTubeAPI()
