from googleapiclient.discovery import build
import re
from bs4 import BeautifulSoup
import requests
API_KEY = 'AIzaSyDEApaU_MZLMN5EtLiVZ6GHc9acGW5dp2M'
youtube = build('youtube', 'v3', developerKey=API_KEY)


def _get_channel_id_from_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the meta tag that contains the channel ID
    meta_tag = soup.find('meta', attrs={'itemprop': 'identifier'})
    if meta_tag:
        return meta_tag['content']
    else:
        return None


def _get_channel_statistics(channel_id: str) -> tuple[dict, str]:
    # Function to process a batch of channel IDs (max 50 per request)
    request = youtube.channels().list(
        part='statistics,contentDetails',
        id=channel_id
    )
    
    response = request.execute()
    item = response['items'][0]

    statistics = item['statistics']
    uploads_playlist_id = item['contentDetails']['relatedPlaylists']['uploads']

    return statistics, uploads_playlist_id

def _get_last_ten_videos(uploads_playlist_id: list[str]) -> list[str]:
    # Retrieve the last ten videos from the uploads playlist
    request = youtube.playlistItems().list(
        part='contentDetails',
        playlistId=uploads_playlist_id,
        maxResults=50
    )
    response = request.execute()
    video_ids = [item['contentDetails']['videoId'] for item in response['items']]
    return video_ids

def _get_video_stats(video_ids: list[str]) -> list[int]:
    # Retrieve view counts for each video
    request = youtube.videos().list(
        part='statistics',
        id=','.join(video_ids)
    )   
    response = request.execute()
    
    view_counts = [item['statistics'].get('viewCount', 0) for item in response['items']]

    return view_counts

def _parse_url(url: str) -> dict:
    # Regex patterns for different URL formats
    channel_id_pattern = re.compile(r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/channel\/([a-zA-Z0-9_-]+)')

    # Match the URL with regex patterns
    channel_id_match = channel_id_pattern.match(url)
    if channel_id_match:
        return channel_id_match.group(1)
    else:
        return _get_channel_id_from_url(url)

def get_channel_data(channel_url: str) -> dict:

    channel_id = _parse_url(channel_url)

    data = {'subscriber_count': 0,
        'channel_view_count': 0,
        'channel_video_count': 0}
    for i in range(10):
            data[f'view_count_{i}'] = 0

    
    
    statistics, uploads_playlist_id = _get_channel_statistics(channel_id)
#    print(len(statistics), len(channel_ids))
        
#       print(statistics)
#       print(channel_statistics)

    subscriber_count = statistics.get('subscriberCount', 0)
    channel_view_count = statistics.get('viewCount', 0)
    channel_video_count = statistics.get('videoCount', 0)
    last_ten_videos = _get_last_ten_videos(uploads_playlist_id)
    view_counts = _get_video_stats(last_ten_videos)

    data['subscriber_count'] = int(subscriber_count)
    data['channel_view_count'] = int(channel_view_count)
    data['channel_video_count'] = int(channel_video_count)

    for j in range(10):
        last_j = 0
        if j < len(view_counts):
            data[f'view_count_{j}'] = int(view_counts[j])
            last_j = j
        else:
            data[f'view_count_{j}'] = int(view_counts[last_j])

    # Create a DataFrame
#    print(data)
    return data