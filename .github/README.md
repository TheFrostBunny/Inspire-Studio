# Video and Audio Merger App

This app lets you select a video file and an audio file, merges them so the output video keeps the original video image but uses the selected audio, and exports the result. Built with Python, Tkinter (or PySimpleGUI), and ffmpeg.

## Features
- Select a video file (e.g., MP4)
- Select an audio file (e.g., MP3, WAV)
- Merge: Replace the video's audio with the selected audio, keeping the original video image
- Export the merged video

## Requirements
- Python 3.8+
- ffmpeg (must be installed and available in PATH)
- Tkinter (comes with standard Python) or PySimpleGUI

## How to Use
1. Run the app: `python app.py`
2. Select your video and audio files
3. Click merge/export
4. The output video will have the original video image and the new audio

---
This is a minimal demo. For production, add error handling and support for more formats as needed.
