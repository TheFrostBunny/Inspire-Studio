import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import subprocess
import os
import threading
import Theme.color_theme

class VideoAudioMergerApp(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid(row=0, column=0, sticky="nsew")
        self.video_path = None
        self.audio_path = None
        self.image_path = None
        self.image_thumbnail = None
        self.progress_var = ctk.DoubleVar(value=0)

        # Hovedramme for padding og bakgrunn
        self.bg_frame = ctk.CTkFrame(self, fg_color=Theme.color_theme.CONTENT_BG, corner_radius=18)
        self.bg_frame.grid(row=0, column=0, sticky="nsew", padx=24, pady=24)
        self.bg_frame.grid_columnconfigure(0, weight=1)

        # Tittel med større font og ikon
        self.title_label = ctk.CTkLabel(self.bg_frame, text="🎬 Video + Audio Merger", anchor="w", font=ctk.CTkFont(size=22, weight="bold"), text_color="#FFD600")
        self.title_label.grid(row=0, column=0, sticky="w", padx=12, pady=(12, 0))

        # Videoinput
        self.video_frame = ctk.CTkFrame(self.bg_frame, fg_color=Theme.color_theme.CONTENT_BG, corner_radius=14)
        self.video_frame.grid(row=1, column=0, sticky="ew", padx=0, pady=(16, 10))
        self.video_frame.grid_columnconfigure(1, weight=1)
        self.video_icon = ctk.CTkLabel(self.video_frame, text="📹", font=ctk.CTkFont(size=16))
        self.video_icon.grid(row=0, column=0, padx=(12, 4), pady=10)
        self.video_label = ctk.CTkLabel(self.video_frame, text="Videofil", anchor="w", font=ctk.CTkFont(size=14))
        self.video_label.grid(row=0, column=1, sticky="w", padx=(0, 8), pady=10)
        self.video_btn = ctk.CTkButton(self.video_frame, text="Velg video", command=self.select_video, height=36, corner_radius=10)
        self.video_btn.grid(row=0, column=2, padx=(0, 12), pady=10)
        self.video_file_label = ctk.CTkLabel(self.video_frame, text="Ingen valgt", anchor="w", font=ctk.CTkFont(size=12), text_color="#B0BEC5")
        self.video_file_label.grid(row=1, column=1, columnspan=2, sticky="w", padx=(0, 12), pady=(0, 8))

        # Lydinput
        self.audio_frame = ctk.CTkFrame(self.bg_frame, fg_color=Theme.color_theme.CONTENT_BG, corner_radius=14)
        self.audio_frame.grid(row=2, column=0, sticky="ew", padx=0, pady=(0, 10))
        self.audio_frame.grid_columnconfigure(1, weight=1)
        self.audio_icon = ctk.CTkLabel(self.audio_frame, text="🎵", font=ctk.CTkFont(size=16))
        self.audio_icon.grid(row=0, column=0, padx=(12, 4), pady=10)
        self.audio_label = ctk.CTkLabel(self.audio_frame, text="Lydfil", anchor="w", font=ctk.CTkFont(size=14))
        self.audio_label.grid(row=0, column=1, sticky="w", padx=(0, 8), pady=10)
        self.audio_btn = ctk.CTkButton(self.audio_frame, text="Velg lyd", command=self.select_audio, height=36, corner_radius=10)
        self.audio_btn.grid(row=0, column=2, padx=(0, 12), pady=10)
        self.audio_file_label = ctk.CTkLabel(self.audio_frame, text="Ingen valgt", anchor="w", font=ctk.CTkFont(size=12), text_color="#B0BEC5")
        self.audio_file_label.grid(row=1, column=1, columnspan=2, sticky="w", padx=(0, 12), pady=(0, 8))

        # Thumbnail input
        self.thumb_frame = ctk.CTkFrame(self.bg_frame, fg_color=Theme.color_theme.CONTENT_BG, corner_radius=14)
        self.thumb_frame.grid(row=3, column=0, sticky="ew", padx=0, pady=(0, 10))
        self.thumb_frame.grid_columnconfigure(1, weight=1)
        self.thumb_icon = ctk.CTkLabel(self.thumb_frame, text="🖼️", font=ctk.CTkFont(size=16))
        self.thumb_icon.grid(row=0, column=0, padx=(12, 4), pady=10)
        self.thumb_label = ctk.CTkLabel(self.thumb_frame, text="(Valgfritt) Bilde for thumbnail", anchor="w", font=ctk.CTkFont(size=14))
        self.thumb_label.grid(row=0, column=1, sticky="w", padx=(0, 8), pady=10)
        self.image_btn = ctk.CTkButton(self.thumb_frame, text="Velg bilde", command=self.select_image, height=36, corner_radius=10)
        self.image_btn.grid(row=0, column=2, padx=(0, 12), pady=10)
        self.thumb_file_label = ctk.CTkLabel(self.thumb_frame, text="Ingen valgt", anchor="w", font=ctk.CTkFont(size=12), text_color="#B0BEC5")
        self.thumb_file_label.grid(row=1, column=1, sticky="w", padx=(0, 12), pady=(0, 8))
        self.thumbnail_label = ctk.CTkLabel(self.thumb_frame, text="", width=64, height=64, fg_color="#23272e", corner_radius=8)
        self.thumbnail_label.grid(row=1, column=2, sticky="e", padx=(0, 12), pady=(0, 8))

        # Slå sammen knapp
        self.merge_btn = ctk.CTkButton(self.bg_frame, text="🔀 Slå sammen og eksporter", command=self.merge, fg_color=Theme.color_theme.BTN_GREEN, text_color="white", font=ctk.CTkFont(size=17, weight="bold"), height=44, corner_radius=12)
        self.merge_btn.grid(row=4, column=0, sticky="ew", padx=0, pady=18)

        # Status og progresjon
        self.status_var = ctk.StringVar(value="Velg video og lyd.")
        self.status_bar = ctk.CTkLabel(self.bg_frame, textvariable=self.status_var, anchor="w", height=32, font=ctk.CTkFont(size=14), text_color="#FFD600", fg_color="#23272e", corner_radius=8)
        self.status_bar.grid(row=5, column=0, sticky="ew", padx=0, pady=(0, 0))
        self.progress_bar = ctk.CTkProgressBar(self.bg_frame, variable=self.progress_var, width=420, height=22, progress_color="#FFD600", corner_radius=8)
        self.progress_bar.grid(row=6, column=0, padx=0, pady=(10, 10))
        self.progress_bar.set(0)

    def select_video(self):
        path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4;*.mov;*.avi;*.mkv")])
        if path:
            self.video_path = path
            self.status_var.set(f"Video valgt: {os.path.basename(path)}")
            self.video_file_label.configure(text=os.path.basename(path))
            self.check_ready()

    def select_audio(self):
        path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3;*.wav;*.aac;*.ogg")])
        if path:
            self.audio_path = path
            self.status_var.set(f"Lyd valgt: {os.path.basename(path)}")
            self.audio_file_label.configure(text=os.path.basename(path))
            self.check_ready()

    def select_image(self):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.bmp;*.webp")])
        if path:
            self.image_path = path
            self.status_var.set(f"Bilde valgt: {os.path.basename(path)} (kun thumbnail)")
            self.thumb_file_label.configure(text=os.path.basename(path))
            try:
                img = Image.open(path)
                img.thumbnail((64, 64))
                self.image_thumbnail = ctk.CTkImage(light_image=img, dark_image=img, size=(64, 64))
                self.thumbnail_label.configure(image=self.image_thumbnail, text="")
                self.thumbnail_label.image = self.image_thumbnail
            except Exception as e:
                self.thumbnail_label.configure(image="", text=f"(Forhåndsvisning feilet: {e})")
        else:
            self.thumb_file_label.configure(text="Ingen valgt")
            self.thumbnail_label.configure(image="", text="")

    def check_ready(self):
        if self.video_path:
            self.merge_btn.configure(state="normal")
            self.status_var.set("Klar til å eksportere.")

    def merge(self):
        output_path = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 Video", "*.mp4")])
        if not output_path:
            self.status_var.set("Ingen fil valgt for eksport.")
            return
        self.status_var.set("Eksporterer video...")
        if not self.video_path:
            self.status_var.set("Du må velge en video.")
            messagebox.showerror("Feil", "Du må velge en video for å eksportere.")
            return
        threading.Thread(target=self._merge_worker, args=(output_path,), daemon=True).start()

    def _merge_worker(self, output_path):
        temp_output = output_path + ".temp.mp4"
        if self.audio_path:
            cmd = [
                "ffmpeg", "-y",
                "-i", self.video_path,
                "-i", self.audio_path,
                "-c:v", "copy",
                "-map", "0:v:0",
                "-map", "1:a:0",
                "-shortest",
                temp_output
            ]
        else:
            cmd = [
                "ffmpeg", "-y",
                "-i", self.video_path,
                "-c:v", "copy",
                temp_output
            ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                # Legg til thumbnail hvis valgt
                if self.image_path:
                    ext = os.path.splitext(self.image_path)[1].lower()
                    thumb_image_path = self.image_path
                    temp_jpg = None
                    if ext == ".webp":
                        try:
                            img = Image.open(self.image_path).convert("RGB")
                            temp_jpg = self.image_path + ".temp.jpg"
                            img.save(temp_jpg, "JPEG")
                            thumb_image_path = temp_jpg
                        except Exception as e:
                            self.status_var.set(f"Kunne ikke konvertere WEBP: {e}")
                            os.rename(temp_output, output_path)
                            return
                    if ext not in [".jpg", ".jpeg", ".png", ".webp"]:
                        self.status_var.set("Video eksportert, men thumbnail må være JPG, PNG eller WEBP.")
                        os.rename(temp_output, output_path)
                    else:
                        thumb_cmd = [
                            "ffmpeg", "-y",
                            "-i", temp_output,
                            "-i", thumb_image_path,
                            "-map", "0",
                            "-map", "1",
                            "-c", "copy",
                            "-metadata:s:t", "title=Thumbnail",
                            "-metadata:s:t", "comment=Cover (front)",
                            "-disposition:v:1", "attached_pic",
                            output_path
                        ]
                        thumb_result = subprocess.run(thumb_cmd, capture_output=True, text=True)
                        try:
                            os.remove(temp_output)
                        except Exception:
                            pass
                        if temp_jpg and os.path.exists(temp_jpg):
                            try:
                                os.remove(temp_jpg)
                            except Exception:
                                pass
                        if thumb_result.returncode == 0:
                            self.status_var.set(f"Ferdig: {os.path.basename(output_path)} eksportert med thumbnail.")
                        else:
                            self.status_var.set("Video eksportert, men thumbnail feilet.")
                else:
                    os.rename(temp_output, output_path)
                    self.status_var.set(f"Ferdig: {os.path.basename(output_path)} eksportert.")
            else:
                self.status_var.set("Feil under eksport.")
        except Exception as e:
            self.status_var.set("Feil under eksport.")
