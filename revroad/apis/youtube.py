from urllib.parse import urlparse, parse_qs

from django.conf import settings
from googleapiclient.discovery import build

YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'
youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=settings.GOOGLE_API_KEY)


def _make_request(video_id):
    try:
        return youtube.videos().list(part='snippet,contentDetails,statistics', id=video_id).execute()
    except:
        pass


def get_video_data(video_id):
    return _make_request(video_id)


def get_video_id_from_url(url):
    o = urlparse(url)
    qs = parse_qs(o.query)
    if 'watch' in o.path:
        video_id = qs['v'][0] if 'v' in qs else None
    else:
        video_id = o.path.replace('/', '')
    return video_id
