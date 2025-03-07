import re
import os
import logging

import urllib3
from bs4 import BeautifulSoup


# Initialize urllib3 PoolManager
http = urllib3.PoolManager()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_playlist_id(playlist_url: str) -> str:
    """
    Get the playlist ID from the playlist URL
    :param playlist_url: URL of the playlist
    :return: Playlist ID
    """
    match = re.search(pattern=r"list=([\w-]+)", string=playlist_url)
    return match.group(1) if match else None

def get_playlist_videos(playlist_url: str) -> list:
    """
    Get the video IDs and title of a YouTube playlist
    :param playlist_url: URL of the playlist
    :return: List of video IDs and playlist title
    """
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = http.request(method="GET", url=playlist_url, headers=headers)
    except urllib3.exceptions.RequestError as e:
        logging.error(f"Request failed: {e}")
        return [], "YouTube_Playlist"

    if response.status != 200:
        logging.error("Failed to fetch playlist page.")
        return [], "YouTube_Playlist"
    
    soup = BeautifulSoup(response.data, "html.parser")

    # Extract video IDs (unique values only)
    video_ids = list(set(re.findall(pattern=r"watch\?v=([\w-]+)", string=response.data.decode("utf-8"))))

    # Extract playlist title
    title_tag = soup.find("title")
    playlist_title = title_tag.text.replace(" - YouTube", "").strip() if title_tag else "YouTube_Playlist"

    return video_ids, playlist_title

def get_youtube_thumbnail(video_id: str, save_folder: str) -> None:
    """
    Download the thumbnail of a YouTube video
    :param video_id: ID of the YouTube video
    :param save_folder: Folder to save the thumbnail
    :return: None
    """
    url = f"http://www.youtube.com/watch?v={video_id}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = http.request(method="GET", url=url, headers=headers)
    except urllib3.exceptions.RequestError as e:
        logging.error(f"Request failed: {e}")
        return

    if response.status != 200:
        logging.error(f"Failed to fetch video page for {video_id}")
        return
    
    # Extract video title
    title_match = re.search(pattern=r"<title>(.*?) - YouTube</title>", string=response.data.decode("utf-8"))
    if not title_match:
        logging.error(f"Could not find title for {video_id}")
        return
    
    title = title_match.group(1).strip()
    # Remove invalid filename characters from title
    safe_title = re.sub(pattern=r'[\/:*?"<>|]', repl="", string=title)

    # Get thumbnail URL
    thumbnail_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"

    # Download thumbnail
    try:
        thumbnail_response = http.request(method="GET", url=thumbnail_url, headers=headers)
    except urllib3.exceptions.RequestError as e:
        logging.error(f"Request failed: {e}")
        return

    if thumbnail_response.status == 200:
        filepath = os.path.join(save_folder, f"{safe_title}.jpg")
        with open(filepath, "wb") as file:
            file.write(thumbnail_response.data)
        logging.info(f"Thumbnail saved as {filepath}")
    else:
        logging.error(f"Failed to fetch thumbnail for {video_id}")

def download_playlist_thumbnails(playlist_url: str) -> None:
    """
    Download thumbnails of all videos in a YouTube playlist
    :param playlist_url: URL of the playlist
    :return: None
    """
    ROOT_DOWNLOAD_FOLDER = "Youtube Thumbnails"

    # Get videos and playlist title
    video_ids, playlist_title = get_playlist_videos(playlist_url=playlist_url)
    if not video_ids:
        logging.error("No videos found in the playlist.")
        return
    
    # Create a folder with the playlist name
    safe_folder_name = re.sub(pattern=r'[\/:*?"<>|]', repl="", string=playlist_title)
    safe_download_folder = os.path.join(ROOT_DOWNLOAD_FOLDER, safe_folder_name)
    os.makedirs(name=safe_download_folder, exist_ok=True)

    logging.info(f"Downloading {len(video_ids)} thumbnails from {playlist_title} into {safe_download_folder} folder.")

    # Download each thumbnail
    for video_id in video_ids:
        get_youtube_thumbnail(video_id=video_id, save_folder=safe_download_folder)

# Example usage
download_playlist_thumbnails(playlist_url="https://www.youtube.com/playlist?list=PLW4OkC7jggFuIjf6iTXkCmIWWlevIPuk4")
