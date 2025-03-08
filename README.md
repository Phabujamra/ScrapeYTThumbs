# ScrapeYTThumbs

ScrapeYTThumbs is a Python script that downloads thumbnails from all videos in a YouTube playlist. It efficiently scrapes video data using `urllib3` and `BeautifulSoup`, ensuring fast and reliable downloads.

## Features
✅ Extracts **all** video IDs and the playlist title from a YouTube playlist URL.  
✅ Downloads **high-quality thumbnails** for each video.  
✅ Saves thumbnails in a **folder named after the playlist title** for easy organization.  
✅ **Handles network errors** gracefully and logs relevant information.  

## Requirements
- Python 3.x  
- `urllib3` (for making HTTP requests)  
- `beautifulsoup4` (for parsing HTML content)  

## Installation
Clone the repository:
```sh
git clone https://github.com/yourusername/ScrapeYTThumbs.git
cd ScrapeYTThumbs
```
Install dependencies:
```sh
pip install -r requirements.txt
```

## Usage
1. Open `main.py` and modify the `playlist_url` variable with the YouTube playlist URL you want to scrape.
2. Run the script:
   ```sh
   python main.py
   ```
3. Thumbnails will be saved in a folder named **"YouTube Thumbnails"**, organized by playlist title.

## Example
**Input:**
```python
playlist_url = "https://www.youtube.com/playlist?list=PL3A5849BDE0581B19"
```
**Output:**
```
📂 YouTube Thumbnails  
 ├── 📂 My Favorite Playlist  
 │   ├── Video1.jpg  
 │   ├── Video2.jpg  
 │   ├── ...
```

## Contributing
💡 Contributions are welcome! If you find a bug or have an idea for improvement, feel free to **open an issue** or **submit a pull request**.

## License
📜 This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.
