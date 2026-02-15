import customtkinter as ctk
from tkinter import filedialog, messagebox
import subprocess
import os
import threading

class YouTubeDownloaderApp(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid(row=0, column=0, sticky="nsew")
        self.progress_var = ctk.DoubleVar(value=0)

        self.yt_label = ctk.CTkLabel(self, text="Last ned video fra YouTube", anchor="w")
        self.yt_label.grid(row=0, column=0, sticky="w", padx=24, pady=(24, 0))
        self.yt_entry = ctk.CTkEntry(self, placeholder_text="Lim inn YouTube-lenke her")
        self.yt_entry.grid(row=1, column=0, sticky="ew", padx=24, pady=4)
        self.yt_btn = ctk.CTkButton(self, text="Last ned YouTube-video", command=self.download_youtube)
        self.yt_btn.grid(row=2, column=0, sticky="ew", padx=24, pady=(0, 12))
        self.status_var = ctk.StringVar(value="")
        self.status_bar = ctk.CTkLabel(self, textvariable=self.status_var, anchor="w", height=28)
        self.status_bar.grid(row=3, column=0, sticky="ew", padx=0, pady=(0, 0))
        self.progress_bar = ctk.CTkProgressBar(self, variable=self.progress_var, width=420, height=16)
        self.progress_bar.grid(row=4, column=0, padx=24, pady=(0, 16))
        self.progress_bar.set(0)

    def set_progress(self, value):
        self.progress_var.set(value)
        self.update_idletasks()

    def download_youtube(self):
        url = self.yt_entry.get().strip()
        if not url:
            self.status_var.set("Lim inn en YouTube-lenke.")
            return
        threading.Thread(target=self._download_worker, args=(url,), daemon=True).start()

    def _download_worker(self, url):
        try:
            title_cmd = [
                "yt-dlp",
                "--get-title",
                url
            ]
            title_result = subprocess.run(title_cmd, capture_output=True, text=True)
            if title_result.returncode == 0:
                video_title = title_result.stdout.strip()
                invalid_chars = '<>:"/\\|?*'
                for c in invalid_chars:
                    video_title = video_title.replace(c, "_")
                default_filename = video_title + ".mp4"
            else:
                default_filename = "youtube_video.mp4"
        except Exception:
            default_filename = "youtube_video.mp4"
        save_path = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 Video", "*.mp4")], initialfile=default_filename)
        if not save_path:
            self.status_var.set("Ingen fil valgt for nedlasting.")
            return
        self.status_var.set("Laster ned fra YouTube...")
        self.set_progress(0.1)
        cmd = [
            "yt-dlp",
            "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4",
            "--merge-output-format", "mp4",
            "-o", save_path,
            url
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            self.set_progress(0.4)
            if result.returncode == 0:
                thumb_path = save_path.replace('.mp4', '.jpg')
                thumb_cmd = [
                    "yt-dlp",
                    "--skip-download",
                    "--write-thumbnail",
                    "--convert-thumbnails", "jpg",
                    "-o", save_path.replace('.mp4', ''),
                    url
                ]
                thumb_result = subprocess.run(thumb_cmd, capture_output=True, text=True)
                self.set_progress(0.6)
                image_path = thumb_path if os.path.exists(thumb_path) else None
                if image_path:
                    # Embed thumbnail as cover art in MP4
                    temp_output = save_path + ".temp.mp4"
                    thumb_cmd = [
                        "ffmpeg", "-y",
                        "-i", save_path,
                        "-i", image_path,
                        "-map", "0",
                        "-map", "1",
                        "-c", "copy",
                        "-metadata:s:t", "title=Thumbnail",
                        "-metadata:s:t", "comment=Cover (front)",
                        "-disposition:v:1", "attached_pic",
                        temp_output
                    ]
                    thumb_result = subprocess.run(thumb_cmd, capture_output=True, text=True)
                    if thumb_result.returncode == 0:
                        try:
                            os.remove(save_path)
                            os.rename(temp_output, save_path)
                        except Exception:
                            pass
                        self.status_var.set(f"Ferdig: {os.path.basename(save_path)} lastet ned med thumbnail.")
                    else:
                        self.status_var.set(f"Ferdig: {os.path.basename(save_path)} lastet ned. Thumbnail kunne ikke legges til.")
                else:
                    self.status_var.set(f"Ferdig: {os.path.basename(save_path)} lastet ned.")
                self.set_progress(1)
            else:
                self.status_var.set("Nedlasting feilet. Sjekk at yt-dlp og ffmpeg er installert.")
                self.set_progress(0)
        except Exception as e:
            self.status_var.set(f"Feil under nedlasting: {e}")
            self.set_progress(0)
