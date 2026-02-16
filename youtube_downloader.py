import customtkinter as ctk
from tkinter import filedialog, messagebox
import subprocess
import os
import threading
import Theme.color_theme

class YouTubeDownloaderApp(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid(row=0, column=0, sticky="nsew")
        self.progress_var = ctk.DoubleVar(value=0)

        # Hovedramme for padding og bakgrunn
        self.bg_frame = ctk.CTkFrame(self, fg_color=Theme.color_theme.MENU_COLOR, corner_radius=18)
        self.bg_frame.grid(row=0, column=0, sticky="nsew", padx=24, pady=24)
        self.bg_frame.grid_columnconfigure(0, weight=1)

        # Tittel med større font og ikon
        self.yt_label = ctk.CTkLabel(self.bg_frame, text="📥 YouTube Video Henter", anchor="w", font=ctk.CTkFont(size=22, weight="bold"), text_color=Theme.color_theme.BTN_GREEN)
        self.yt_label.grid(row=0, column=0, sticky="w", padx=12, pady=(12, 0))

        # Inndeling for lenkeinput
        self.link_frame = ctk.CTkFrame(self.bg_frame, fg_color=Theme.color_theme.CONTENT_BG, corner_radius=14)
        self.link_frame.grid(row=1, column=0, sticky="ew", padx=0, pady=(16, 10))
        self.link_frame.grid_columnconfigure(1, weight=1)
        self.link_icon = ctk.CTkLabel(self.link_frame, text="🔗", font=ctk.CTkFont(size=18))
        self.link_icon.grid(row=0, column=0, padx=(12, 4), pady=12)
        self.yt_entry = ctk.CTkEntry(self.link_frame, placeholder_text="Lim inn YouTube-lenke eller spilleliste", height=40, font=ctk.CTkFont(size=15))
        self.yt_entry.grid(row=0, column=1, sticky="ew", padx=(0, 12), pady=12)

        # Nedlastingsknapp med farge og ikon
        self.yt_btn = ctk.CTkButton(self.bg_frame, text="⬇️  Last ned", command=self.download_youtube, fg_color=Theme.color_theme.BTN_GREEN, text_color="white", font=ctk.CTkFont(size=17, weight="bold"), height=44, corner_radius=12)
        self.yt_btn.grid(row=2, column=0, sticky="ew", padx=0, pady=(0, 18))

        # Status og progresjon
        self.status_var = ctk.StringVar(value="")
        self.status_bar = ctk.CTkLabel(self.bg_frame, textvariable=self.status_var, anchor="w", height=32, font=ctk.CTkFont(size=14), text_color=Theme.color_theme.BTN_BLUE, fg_color=Theme.color_theme.MENU_COLOR, corner_radius=8)
        self.status_bar.grid(row=3, column=0, sticky="ew", padx=0, pady=(0, 0))
        self.progress_bar = ctk.CTkProgressBar(self.bg_frame, variable=self.progress_var, width=420, height=22, progress_color=Theme.color_theme.BTN_BLUE, corner_radius=8)
        self.progress_bar.grid(row=4, column=0, padx=0, pady=(10, 10))
        self.progress_bar.set(0)

    def set_progress(self, value):
        self.progress_var.set(value)
        self.update_idletasks()

    def download_youtube(self):
        url = self.yt_entry.get().strip()
        if not url:
            self.status_var.set("Lim inn en YouTube-lenke.")
            return
        # Sjekk om det er en spilleliste
        if "list=" in url:
            threading.Thread(target=self._download_playlist_worker, args=(url,), daemon=True).start()
        else:
            threading.Thread(target=self._download_worker, args=(url,), daemon=True).start()

    def _download_playlist_worker(self, url):
        # Velg hovedmappe for å lagre spillelisten
        base_dir = filedialog.askdirectory(title="Velg mappe for å lagre spilleliste")
        if not base_dir:
            self.status_var.set("Ingen mappe valgt for nedlasting.")
            return
        self.status_var.set("Henter spilleliste-informasjon...")
        self.set_progress(0.05)
        # Hent navn på spillelisten
        try:
            title_cmd = [
                "yt-dlp",
                "--flat-playlist",
                "--print", "%(playlist_title)s",
                url
            ]
            title_result = subprocess.run(title_cmd, capture_output=True, text=True)
            playlist_title = title_result.stdout.strip().splitlines()[0] if title_result.returncode == 0 else "YouTube_Playlist"
            invalid_chars = '<>:"/\\|?*'
            for c in invalid_chars:
                playlist_title = playlist_title.replace(c, "_")
        except Exception:
            playlist_title = "YouTube_Playlist"
        # Lag mappe med spillelistenavn
        save_dir = os.path.join(base_dir, playlist_title)
        os.makedirs(save_dir, exist_ok=True)
        # Hent antall videoer i spillelisten
        try:
            count_cmd = [
                "yt-dlp",
                "--flat-playlist",
                "--print", "%(id)s",
                url
            ]
            count_result = subprocess.run(count_cmd, capture_output=True, text=True)
            video_ids = [line.strip() for line in count_result.stdout.splitlines() if line.strip()]
            total = len(video_ids)
        except Exception:
            total = 0
        if total == 0:
            self.status_var.set("Fant ingen videoer i spillelisten.")
            return
        self.status_var.set(f"Laster ned {total} videoer fra spillelisten til '{playlist_title}'...")
        self.set_progress(0.1)
        # Last ned og legg til thumbnail for hver video
        for idx, vid in enumerate(video_ids, 1):
            self.status_var.set(f"Laster ned video {idx} av {total} ...")
            self.set_progress(0.1 + 0.7 * idx / total)
            # Last ned video
            video_cmd = [
                "yt-dlp",
                "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4",
                "--merge-output-format", "mp4",
                "-o", os.path.join(save_dir, f"{idx:02d} - %(title)s.%(ext)s"),
                f"https://www.youtube.com/watch?v={vid}"
            ]
            result = subprocess.run(video_cmd, capture_output=True, text=True)
            # Finn filnavn
            out_name = None
            for line in result.stdout.splitlines():
                if "Destination:" in line:
                    out_name = line.split("Destination:",1)[-1].strip()
            # Søk etter mp4-fil hvis ikke funnet
            if not out_name:
                files = [f for f in os.listdir(save_dir) if f.endswith(".mp4")]
                files = sorted(files, key=lambda x: os.path.getmtime(os.path.join(save_dir, x)), reverse=True)
                out_name = os.path.join(save_dir, files[0]) if files else None
            # Last ned thumbnail
            if out_name:
                thumb_path = out_name.replace('.mp4', '.jpg')
                thumb_cmd = [
                    "yt-dlp",
                    "--skip-download",
                    "--write-thumbnail",
                    "--convert-thumbnails", "jpg",
                    "-o", out_name.replace('.mp4', ''),
                    f"https://www.youtube.com/watch?v={vid}"
                ]
                thumb_result = subprocess.run(thumb_cmd, capture_output=True, text=True)
                image_path = thumb_path if os.path.exists(thumb_path) else None
                if image_path:
                    temp_output = out_name + ".temp.mp4"
                    ffmpeg_cmd = [
                        "ffmpeg", "-y",
                        "-i", out_name,
                        "-i", image_path,
                        "-map", "0",
                        "-map", "1",
                        "-c", "copy",
                        "-metadata:s:t", "title=Thumbnail",
                        "-metadata:s:t", "comment=Cover (front)",
                        "-disposition:v:1", "attached_pic",
                        temp_output
                    ]
                    ffmpeg_result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
                    if ffmpeg_result.returncode == 0:
                        try:
                            os.remove(out_name)
                            os.rename(temp_output, out_name)
                        except Exception:
                            pass
        self.status_var.set(f"Ferdig: {total} videoer lastet ned til '{playlist_title}' med thumbnails.")
        self.set_progress(1)

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
