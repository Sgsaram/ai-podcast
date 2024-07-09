from googleapiclient.discovery import build
import re
from bs4 import BeautifulSoup
import requests
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())

API_KEY = os.getenv("YT_API_TOKEN", "")
youtube = build('youtube', 'v3', developerKey=API_KEY)


def _get_channel_id_from_url(url):
    try:
        response = requests.get(url)
    except:
        return None
    
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
    if 'items' not in response:
        return None, None

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

    if 'items' not in response:
        return None
    
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

    data = {'subscriber_count': 0,
        'channel_view_count': 0,
        'channel_video_count': 0}
    for i in range(10):
            data[f'view_count_{i}'] = 0

    channel_id = _parse_url(channel_url)
    if channel_id is None:
        return data

    statistics, uploads_playlist_id = _get_channel_statistics(channel_id)
    if statistics is None or uploads_playlist_id is None:
        return data

#    print(len(statistics), len(channel_ids))
        
#       print(statistics)
#       print(channel_statistics)

    subscriber_count = statistics.get('subscriberCount', 0)
    channel_view_count = statistics.get('viewCount', 0)
    channel_video_count = statistics.get('videoCount', 0)

    data['subscriber_count'] = int(subscriber_count)
    data['channel_view_count'] = int(channel_view_count)
    data['channel_video_count'] = int(channel_video_count)

    last_ten_videos = _get_last_ten_videos(uploads_playlist_id)

    if last_ten_videos is None:
        return data
    else:
       view_counts = _get_video_stats(last_ten_videos)

    

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

if __name__ == "__main__":
    print("Not intended to run ytparser.py as a script.")
