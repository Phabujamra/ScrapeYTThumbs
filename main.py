import re
import os
import logging
from concurrent.futures import ThreadPoolExecutor
import threading

import urllib3
from bs4 import BeautifulSoup
from tqdm import tqdm


# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Thread-local storage to keep a separate PoolManager per thread
thread_local = threading.local()

def get_http() -> urllib3.PoolManager:
    """Return a thread-local PoolManager instance"""
    if not hasattr(thread_local, "http"):
        thread_local.http = urllib3.PoolManager(num_pools=5, maxsize=5)
    return thread_local.http


def get_playlist_videos(playlist_url: str) -> tuple:
    """
    Get the video IDs and title of a YouTube playlist.
    :param playlist_url: URL of the playlist
    :return: Tuple (List of video IDs, Playlist title)
    """
    http = get_http()  # Use thread-local HTTP connection pool

    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = http.request("GET", playlist_url, headers=headers)
    except urllib3.exceptions.RequestError as e:
        logging.error(f"Request failed: {e}")
        return [], "YouTube_Playlist"

    if response.status != 200:
        logging.error("Failed to fetch playlist page.")
        return [], "YouTube_Playlist"
    
    soup = BeautifulSoup(response.data, "html.parser")

    # Extract video IDs (unique values only)
    video_ids = list(set(re.findall(r"watch\?v=([\w-]+)", response.data.decode("utf-8"))))

    # Extract playlist title
    title_tag = soup.find("title")
    playlist_title = title_tag.text.replace(" - YouTube", "").strip() if title_tag else "YouTube_Playlist"

    return video_ids, playlist_title


def get_youtube_thumbnail(video_id: str, save_folder: str) -> None:
    """
    Download the thumbnail of a YouTube video.
    :param video_id: ID of the YouTube video
    :param save_folder: Folder to save the thumbnail
    :return: None
    """
    http = get_http()  # Get thread-local PoolManager
    
    url = f"https://www.youtube.com/watch?v={video_id}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = http.request("GET", url, headers=headers)
    except urllib3.exceptions.RequestError as e:
        logging.error(f"Request failed: {e}")
        return

    if response.status != 200:
        logging.error(f"Failed to fetch video page for {video_id}")
        return
    
    # Extract video title
    title_match = re.search(r"<title>(.*?) - YouTube</title>", response.data.decode("utf-8"))
    if not title_match:
        logging.error(f"Could not find title for {video_id}")
        return
    
    title = title_match.group(1).strip()
    safe_title = re.sub(r'[\/:*?"<>|]', "", title)

    # Get thumbnail URL
    thumbnail_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"

    try:
        thumbnail_response = http.request("GET", thumbnail_url, headers=headers)
    except urllib3.exceptions.RequestError as e:
        logging.error(f"Request failed: {e}")
        return

    if thumbnail_response.status == 200:
        filepath = os.path.join(save_folder, f"{safe_title}.jpg")
        with open(filepath, "wb") as file:
            file.write(thumbnail_response.data)
        # logging.info(f"Thumbnail saved: {filepath}")
    else:
        logging.error(f"Failed to fetch thumbnail for {video_id}")


def download_playlist_thumbnails(playlist_url: str, max_threads: int = 5) -> None:
    """
    Download thumbnails of all videos in a YouTube playlist using multithreading.
    :param playlist_url: URL of the playlist
    :param max_threads: Maximum number of concurrent downloads
    :return: None
    """
    ROOT_DOWNLOAD_FOLDER = "Youtube Thumbnails"

    # Get videos and playlist title
    video_ids, playlist_title = get_playlist_videos(playlist_url)
    if not video_ids:
        logging.error("No videos found in the playlist.")
        return
    
    # Create a folder with the playlist name
    safe_folder_name = re.sub(r'[\/:*?"<>|]', "", playlist_title)
    safe_download_folder = os.path.join(ROOT_DOWNLOAD_FOLDER, safe_folder_name)
    os.makedirs(safe_download_folder, exist_ok=True)

    logging.info(f"Downloading {len(video_ids)} thumbnails from '{playlist_title}' into '{safe_download_folder}'")

    # Progress bar
    with tqdm(total=len(video_ids), desc="Downloading thumbnails") as pbar:
        def wrapped_download(video_id, safe_download_folder):
            get_youtube_thumbnail(video_id=video_id, save_folder=safe_download_folder)
            pbar.update(1)

        # Use ThreadPoolExecutor for parallel downloads
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            for video_id in video_ids:
                executor.submit(wrapped_download, video_id, safe_download_folder)


# Example usage
download_playlist_thumbnails("https://www.youtube.com/playlist?list=PLW4OkC7jggFuIjf6iTXkCmIWWlevIPuk4", max_threads=10)
