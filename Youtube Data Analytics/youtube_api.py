import os
from googleapiclient.discovery import build
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY", "AIzaSyC651JQc-DSfBsH2BytBfTRFQExQELvyhg")

def get_video_info_api(video_id):
    if not YOUTUBE_API_KEY:
        return {"error": "No API key configured"}
    try:
        youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
        resp = youtube.videos().list(part="snippet,statistics,contentDetails", id=video_id).execute()
        items = resp.get("items", [])
        if not items:
            return {"error": "Video not found via API"}
        item = items[0]
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})
        thumb = snippet.get("thumbnails", {}).get("high", {}).get("url") or snippet.get("thumbnails", {}).get("default", {}).get("url")
        return {
            "title": snippet.get("title"),
            "author": snippet.get("channelTitle"),
            "publish_date": snippet.get("publishedAt", "").split("T")[0],
            "views": stats.get("viewCount"),
            "description": (snippet.get("description") or "")[:1000],
            "thumbnail_url": thumb,
        }
    except Exception as e:
        return {"error": f"API error: {e}"}