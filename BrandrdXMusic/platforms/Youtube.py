import asyncio
import logging
import os
import re
import time
from typing import Union
from urllib.parse import urlparse, parse_qs

import aiohttp
import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from py_yt import VideosSearch, Playlist

# Hide routine YouTube INFO messages; retain warnings and errors.
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.WARNING)

PRIMARY_API_URL = os.getenv("API_URL", "http://165.232.182.138:8000").rstrip("/")
FALLBACK_API_URL = os.getenv("API_URL_FALLBACK", "https://api.shrutibots.in").rstrip("/")
API_KEY = os.getenv("API_KEY", "")
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

CONNECT_TIMEOUT = 10
READ_TIMEOUT = 35
TOTAL_TIMEOUT = 120
MAX_AUDIO_SIZE = 100 * 1024 * 1024
MAX_VIDEO_SIZE = 500 * 1024 * 1024
DOWNLOAD_TIMEOUT = 260
DOWNLOAD_LOCKS = {}


def time_to_seconds(value):
    if not value:
        return 0
    try:
        return sum(int(x) * 60 ** i for i, x in enumerate(reversed(str(value).split(":"))))
    except (ValueError, TypeError):
        return 0


def extract_video_id(link):
    link = str(link).strip()
    if re.fullmatch(r"[\w-]{11}", link):
        return link
    parsed = urlparse(link)
    host = (parsed.hostname or "").lower()
    video_id = None
    if host in ("youtube.com", "www.youtube.com", "m.youtube.com", "music.youtube.com", "www.music.youtube.com"):
        video_id = parse_qs(parsed.query).get("v", [None])[0]
        if not video_id:
            parts = parsed.path.strip("/").split("/")
            if len(parts) >= 2 and parts[0] in ("shorts", "live", "embed"):
                video_id = parts[1]
    elif host in ("youtu.be", "www.youtu.be"):
        video_id = parsed.path.strip("/").split("/")[0]
    return video_id if video_id and re.fullmatch(r"[\w-]{11}", video_id) else None


def detect_media_extension(header, content_type, stream_type):
    """Use file signature first; MIME type only when the signature is inconclusive."""
    raw = header
    h = raw.lstrip()
    if not h or h[:32].lower().startswith((b"<!doctype", b"<html", b"<?xml", b"{", b"[{")):
        return None
    if raw.startswith(b"\x1a\x45\xdf\xa3"):
        return "webm"  # Matroska/WebM signature; FFmpeg probes actual codec.
    if len(raw) >= 12 and raw[4:8] == b"ftyp":
        return "mp4" if stream_type == "video" else "m4a"
    if raw.startswith(b"ID3") or raw.startswith((b"\xff\xfb", b"\xff\xf3")):
        return "mp3"
    if raw.startswith((b"\xff\xf1", b"\xff\xf9")):
        return "aac"
    if raw.startswith(b"OggS"):
        return "ogg"
    if raw.startswith(b"fLaC"):
        return "flac"
    mime = content_type.split(";", 1)[0].strip().lower()
    mapping = {
        "audio/mp4": "m4a", "video/mp4": "mp4", "audio/x-m4a": "m4a",
        "audio/webm": "webm", "video/webm": "webm", "audio/mpeg": "mp3",
        "audio/mp3": "mp3", "audio/aac": "aac", "audio/ogg": "ogg",
        "application/ogg": "ogg", "audio/flac": "flac",
    }
    return mapping.get(mime)


def valid_media_header(header):
    return detect_media_extension(header, "", "audio") is not None


def _cached_file(video_id, stream_type):
    # Check only known extensions, and verify the header so an old misnamed .webm
    # file containing MP4 data will not be reused.
    extensions = ("mp4", "webm") if stream_type == "video" else ("m4a", "webm", "mp3", "aac", "ogg", "flac", "mp4")
    for ext in extensions:
        path = os.path.join(DOWNLOAD_DIR, f"{video_id}.{ext}")
        if not os.path.isfile(path):
            continue
        try:
            if os.path.getsize(path) <= 1024:
                os.remove(path)
                continue
            with open(path, "rb") as f:
                header = f.read(32)
            actual = detect_media_extension(header, "", stream_type)
            if actual == ext or (stream_type == "video" and actual == "mp4" and ext == "mp4"):
                return path
            # Old files can be incorrectly named: rename only if their actual
            # signature is recognizable and the corrected target does not exist.
            if actual:
                corrected = os.path.join(DOWNLOAD_DIR, f"{video_id}.{actual}")
                if not os.path.exists(corrected):
                    os.replace(path, corrected)
                    return corrected
        except OSError as e:
            LOGGER.warning("[YouTube] Cache check failed: %s", e)
    return None


async def _stream_to_file(video_id: str, stream_type: str):
    video_id = extract_video_id(video_id)
    if not video_id:
        LOGGER.error("[YouTube] Invalid video ID")
        return None
    if stream_type not in ("audio", "video"):
        LOGGER.error("[YouTube] Invalid stream type: %s", stream_type)
        return None
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    lock_key = (video_id, stream_type)
    lock = DOWNLOAD_LOCKS.setdefault(lock_key, asyncio.Lock())
    async with lock:
        cached = _cached_file(video_id, stream_type)
        if cached:
            LOGGER.info("[YouTube] Cached file found: %s", cached)
            return cached

        api_list = [("PRIMARY", PRIMARY_API_URL), ("FALLBACK", FALLBACK_API_URL)]
        max_size = MAX_VIDEO_SIZE if stream_type == "video" else MAX_AUDIO_SIZE
        timeout = aiohttp.ClientTimeout(total=TOTAL_TIMEOUT, connect=CONNECT_TIMEOUT, sock_read=READ_TIMEOUT)

        for api_name, api_url in api_list:
            if not api_url:
                continue
            temp_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.{stream_type}.{api_name.lower()}.part")
            started = time.monotonic()
            LOGGER.info("[YouTube] Trying %s API: %s (%s)", api_name, video_id, stream_type)
            try:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    stream_url = f"{api_url}/stream/{stream_type}/{video_id}"
                    async with session.get(stream_url, allow_redirects=True, headers={"Accept": "*/*"}) as response:
                        content_type = response.headers.get("Content-Type", "")
                        LOGGER.info("[YouTube] %s HTTP=%s TYPE=%s", api_name, response.status, content_type)
                        if response.status != 200:
                            LOGGER.warning("[YouTube] %s API failed: HTTP %s", api_name, response.status)
                            continue
                        if any(v in content_type.lower() for v in ("application/json", "text/html", "text/plain")):
                            LOGGER.warning("[YouTube] %s returned non-media response: %s", api_name, content_type)
                            continue
                        total_bytes = 0
                        header = b""
                        with open(temp_path, "wb") as file:
                            async for chunk in response.content.iter_chunked(64 * 1024):
                                if not chunk:
                                    continue
                                if len(header) < 32:
                                    header += chunk[:32 - len(header)]
                                total_bytes += len(chunk)
                                if total_bytes > max_size:
                                    raise ValueError("Maximum file size exceeded")
                                file.write(chunk)
                        if total_bytes <= 1024:
                            LOGGER.warning("[YouTube] %s returned empty/small file", api_name)
                            continue
                        extension = detect_media_extension(header, content_type, stream_type)
                        if not extension:
                            LOGGER.warning("[YouTube] %s returned invalid/unknown media", api_name)
                            continue
                        file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.{extension}")
                        os.replace(temp_path, file_path)
                        LOGGER.info("[YouTube] DOWNLOAD SUCCESS API=%s FILE=%s SIZE=%s TIME=%.2fs", api_name, file_path, total_bytes, time.monotonic() - started)
                        return file_path
            except asyncio.CancelledError:
                raise
            except asyncio.TimeoutError:
                LOGGER.warning("[YouTube] %s API timeout after %.2fs", api_name, time.monotonic() - started)
            except aiohttp.ClientError as error:
                LOGGER.warning("[YouTube] %s connection error: %s", api_name, error)
            except Exception:
                LOGGER.exception("[YouTube] %s unexpected error", api_name)
            finally:
                try:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                except OSError:
                    pass
        LOGGER.error("[YouTube] PRIMARY + FALLBACK both failed: %s (%s)", video_id, stream_type)
        return None


async def download_song(link: str):
    video_id = extract_video_id(link)
    return await _stream_to_file(video_id, "audio") if video_id else None


async def download_video(link: str):
    video_id = extract_video_id(link)
    return await _stream_to_file(video_id, "video") if video_id else None


class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.status = "https://www.youtube.com/oembed?url="
        self.listbase = "https://youtube.com/playlist?list="
        self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    async def exists(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        return bool(re.search(self.regex, link))

    async def url(self, message_1: Message) -> Union[str, None]:
        messages = [message_1]
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)
        for message in messages:
            text = message.text or message.caption or ""
            entities = message.entities or message.caption_entities or []
            for entity in entities:
                if entity.type == MessageEntityType.TEXT_LINK:
                    return entity.url
                if entity.type == MessageEntityType.URL:
                    return text[entity.offset:entity.offset + entity.length]
        return None

    async def details(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        data = await asyncio.wait_for(results.next(), timeout=35)
        items = data.get("result") or []
        if not items:
            raise ValueError("No YouTube search results found")
        result = items[0]
        title = result.get("title") or "Unknown Title"
        duration_min = result.get("duration") or "0:00"
        thumbnails = result.get("thumbnails") or []
        thumbnail = thumbnails[0].get("url", "").split("?")[0] if thumbnails else ""
        vidid = result.get("id")
        duration_sec = time_to_seconds(duration_min)
        return title, duration_min, duration_sec, thumbnail, vidid

    async def title(self, link: str, videoid: Union[bool, str] = None):
        data = await self.details(link, videoid)
        return data[0]

    async def duration(self, link: str, videoid: Union[bool, str] = None):
        data = await self.details(link, videoid)
        return data[1]

    async def thumbnail(self, link: str, videoid: Union[bool, str] = None):
        data = await self.details(link, videoid)
        return data[3]

    async def video(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        try:
            downloaded_file = await asyncio.wait_for(download_video(link), timeout=DOWNLOAD_TIMEOUT)
            return (1, downloaded_file) if downloaded_file else (0, "Video download failed")
        except asyncio.CancelledError:
            raise
        except Exception:
            LOGGER.exception("[YouTube] Video download error")
            return 0, "Video download error"

    async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None):
        if videoid:
            link = self.listbase + link
        try:
            plist = await asyncio.wait_for(Playlist.get(link), timeout=45)
        except asyncio.CancelledError:
            raise
        except Exception:
            LOGGER.exception("[YouTube] Playlist fetch failed")
            return []
        videos = plist.get("videos") or []
        ids = []
        for data in videos[:limit]:
            if data and data.get("id"):
                ids.append(data["id"])
        return ids

    async def track(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        data = await asyncio.wait_for(results.next(), timeout=35)
        items = data.get("result") or []
        if not items:
            raise ValueError("No YouTube track found")
        result = items[0]
        title = result.get("title") or "Unknown Title"
        duration_min = result.get("duration") or "0:00"
        vidid = result.get("id")
        yturl = result.get("link") or (self.base + str(vidid))
        thumbnails = result.get("thumbnails") or []
        thumbnail = thumbnails[0].get("url", "").split("?")[0] if thumbnails else ""
        track_details = {"title": title, "link": yturl, "vidid": vidid, "duration_min": duration_min, "thumb": thumbnail}
        return track_details, vidid

    async def formats(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        ytdl_opts = {"quiet": True, "no_warnings": True, "noplaylist": True, "socket_timeout": 15, "retries": 1, "extractor_retries": 1}
        def extract():
            with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
                return ydl.extract_info(link, download=False)
        try:
            result = await asyncio.wait_for(asyncio.to_thread(extract), timeout=45)
        except asyncio.CancelledError:
            raise
        except Exception:
            LOGGER.exception("[YouTube] Format extraction failed")
            return [], link
        formats_available = []
        for fmt in (result or {}).get("formats", []):
            try:
                if "dash" in str(fmt.get("format", "")).lower():
                    continue
                formats_available.append({"format": fmt.get("format"), "filesize": fmt.get("filesize"), "format_id": fmt.get("format_id"), "ext": fmt.get("ext"), "format_note": fmt.get("format_note"), "yturl": link})
            except Exception:
                continue
        return formats_available, link

    async def slider(self, link: str, query_type: int, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=10)
        data = await asyncio.wait_for(results.next(), timeout=35)
        items = data.get("result") or []
        if not items:
            raise ValueError("No YouTube slider results")
        if query_type < 0 or query_type >= len(items):
            raise IndexError("Invalid slider index")
        result = items[query_type]
        title = result.get("title") or "Unknown Title"
        duration_min = result.get("duration") or "0:00"
        vidid = result.get("id")
        thumbnails = result.get("thumbnails") or []
        thumbnail = thumbnails[0].get("url", "").split("?")[0] if thumbnails else ""
        return title, duration_min, thumbnail, vidid

    async def download(self, link: str, mystic, video: Union[bool, str] = None, videoid: Union[bool, str] = None, songaudio: Union[bool, str] = None, songvideo: Union[bool, str] = None, format_id: Union[bool, str] = None, title: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        stream_type = "video" if video or songvideo else "audio"
        LOGGER.info("[YouTube] Download requested: %s | %s", link, stream_type)
        try:
            downloaded_file = await asyncio.wait_for(download_video(link) if stream_type == "video" else download_song(link), timeout=DOWNLOAD_TIMEOUT)
            if not downloaded_file:
                LOGGER.error("[YouTube] Download returned None: %s", link)
                return None, False
            if not os.path.isfile(downloaded_file):
                LOGGER.error("[YouTube] Downloaded file missing: %s", downloaded_file)
                return None, False
            size = os.path.getsize(downloaded_file)
            if size <= 1024:
                LOGGER.error("[YouTube] Invalid downloaded file size: %s", size)
                return None, False
            LOGGER.info("[YouTube] Download complete: %s (%s bytes)", downloaded_file, size)
            return downloaded_file, True
        except asyncio.CancelledError:
            raise
        except asyncio.TimeoutError:
            LOGGER.error("[YouTube] Download timeout: %s", link)
            return None, False
        except Exception:
            LOGGER.exception("[YouTube] Unexpected download error")
            return None, False


YouTube = YouTubeAPI()
