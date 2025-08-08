import datetime, tempfile, os
from pytube import YouTube, Playlist
import youtube_dl
from urllib.parse import urlparse, parse_qs
from youtube_api import get_video_info_api, YOUTUBE_API_KEY

try:
    import whisper
    WHISPER_AVAILABLE = True
except Exception:
    WHISPER_AVAILABLE = False

def extract_video_id(url):
    parsed = urlparse(url)
    qs = parse_qs(parsed.query)
    v = qs.get("v")
    if v:
        return v[0]
    if "youtu.be" in parsed.netloc:
        return parsed.path.lstrip('/')
    return None

def get_video_info_pytube(url):
    try:
        yt = YouTube(url)
        return {
            "title": yt.title,
            "author": yt.author,
            "publish_date": yt.publish_date.strftime("%Y-%m-%d") if yt.publish_date else None,
            "views": yt.views,
            "length_sec": yt.length,
            "description": yt.description[:1000] if yt.description else "",
            "thumbnail_url": yt.thumbnail_url,
        }
    except Exception as e:
        return {"error": f"pytube error: {e}"}

def get_video_info_ytdl(url):
    try:
        with youtube_dl.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            upload_date = None
            if info.get('upload_date'):
                upload_date = datetime.datetime.strptime(info['upload_date'], "%Y%m%d").date().isoformat()
            return {
                "title": info.get('title'),
                "author": info.get('uploader'),
                "publish_date": upload_date,
                "views": info.get('view_count'),
                "length_sec": info.get('duration'),
                "description": (info.get('description') or '')[:1000],
                "thumbnail_url": info.get('thumbnail'),
            }
    except Exception as e:
        return {"error": f"youtube_dl error: {e}"}

def transcribe_audio_with_whisper(url):
    if not WHISPER_AVAILABLE:
        return ""
    try:
        yt = YouTube(url)
        stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
        if not stream:
            return ""
        with tempfile.TemporaryDirectory() as tmpdir:
            out = stream.download(output_path=tmpdir, filename="audio")
            model = whisper.load_model("base")
            res = model.transcribe(out)
            return res.get('text','')[:3000]
    except Exception as e:
        return ""

def get_all_videos_from_playlist(playlist_url):
    try:
        pl = Playlist(playlist_url)
        return list(pl.video_urls)
    except Exception:
        return []

def get_video_info(url, prefer_api=False):
    vid = extract_video_id(url)
    if prefer_api and vid and YOUTUBE_API_KEY:
        api_info = get_video_info_api(vid)
        if api_info and "error" not in api_info:
            if WHISPER_AVAILABLE:
                api_info['transcript'] = transcribe_audio_with_whisper(url)
            api_info['url'] = url
            return api_info

    info = get_video_info_pytube(url)
    if info and "error" not in info:
        if WHISPER_AVAILABLE:
            info['transcript'] = transcribe_audio_with_whisper(url)
        info['url'] = url
        return info

    info = get_video_info_ytdl(url)
    info['url'] = url
    if WHISPER_AVAILABLE:
        info['transcript'] = transcribe_audio_with_whisper(url)
    return info