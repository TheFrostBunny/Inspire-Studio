# Inspire Studio

Inspire Studio is a modern, user-friendly app for Windows that lets you:

- **Merge video and audio**: Select a video file and an audio file, and export a new video with your chosen audio.
- **Download from YouTube**: Paste a YouTube link or playlist and download videos with automatic thumbnails.

The app features a modern interface built with Python, customtkinter, and ffmpeg.

## Features
- Select and merge video (MP4, MOV, AVI, MKV) and audio (MP3, WAV, AAC, OGG)
- Add a custom thumbnail to exported videos
- Download single videos or entire playlists from YouTube
- Automatic embedding of cover images (thumbnails) on all downloaded videos
- Modern, theme-based UI

## Requirements
- On Linux:
	- Install ffmpeg with your package manager, e.g. `sudo apt install ffmpeg` (Debian/Ubuntu) or `sudo dnf install ffmpeg` (Fedora)
	- Make sure Python 3.8+ is installed: `python3 --version`
	- Install Python dependencies: `pip install customtkinter yt-dlp`

- Python 3.8 or newer
- ffmpeg (must be installed and in PATH)
- customtkinter (`pip install customtkinter`)
- yt-dlp (`pip install yt-dlp`)

## How to use Inspire Studio
### On Linux
1. Run the app: `python3 main.py`
2. Use the app as described above. All features work on Linux, but the system tray icon may not be available on all desktop environments.
1. Run the app: `python main.py`
2. Choose "Video + Audio" to merge video and audio, or "YouTube" to download videos
3. Follow the instructions in the app
4. Done!
