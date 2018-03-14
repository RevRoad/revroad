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


def get_video_data(url):
    o = urlparse(url)
    qs = parse_qs(o.query)
    if 'watch' in o.path:
        video_id = qs['v'][0] if 'v' in qs else None
    else:
        video_id = o.path.replace('/', '')
    if video_id:
        video_data_items = _make_request(video_id)['items']
        if video_data_items:
            video_data = video_data_items[0]
            video_data['embed_url'] = 'https://www.youtube.com/embed/{}'.format(video_id)
            t = qs.get('t')
            if t:
                t = t[0]
                if 'm' in t:
                    t = int(t.replace('m', '')) * 60
                else:
                    t = t.replace('s', '')
                video_data['embed_url'] += '?start={}'.format(t)
            return video_data
