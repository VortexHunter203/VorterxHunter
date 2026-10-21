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
API_LIST = [
    (url, key)
    for url, key in [
        (PRIMARY_API_URL, ""),
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
    return
