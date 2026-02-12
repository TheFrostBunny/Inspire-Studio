import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import subprocess
import os

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")

class VideoAudioMergerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Video + Audio Merger")
        self.geometry("480x520")
        self.resizable(False, False)
        self.video_path = None
        self.audio_path = None
        self.image_path = None
        self.image_thumbnail = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(6, weight=1)

        # Video
        self.video_label = ctk.CTkLabel(self, text="1. Velg videofil", anchor="w")
        self.video_label.grid(row=0, column=0, sticky="w", padx=24, pady=(24, 0))
        self.video_btn = ctk.CTkButton(self, text="Velg video", command=self.select_video)
        self.video_btn.grid(row=1, column=0, sticky="ew", padx=24, pady=4)
        self.video_file_label = ctk.CTkLabel(self, text="Ingen valgt", anchor="w")
        self.video_file_label.grid(row=2, column=0, sticky="w", padx=24, pady=(0, 12))

        # Audio
        self.audio_label = ctk.CTkLabel(self, text="2. Velg lydfil", anchor="w")
        self.audio_label.grid(row=3, column=0, sticky="w", padx=24, pady=(0, 0))
        self.audio_btn = ctk.CTkButton(self, text="Velg lyd", command=self.select_audio)
        self.audio_btn.grid(row=4, column=0, sticky="ew", padx=24, pady=4)
        self.audio_file_label = ctk.CTkLabel(self, text="Ingen valgt", anchor="w")
        self.audio_file_label.grid(row=5, column=0, sticky="w", padx=24, pady=(0, 12))

        # Thumbnail
        self.thumb_label = ctk.CTkLabel(self, text="3. (Valgfritt) Velg bilde for thumbnail", anchor="w")
        self.thumb_label.grid(row=6, column=0, sticky="w", padx=24, pady=(0, 0))
        self.image_btn = ctk.CTkButton(self, text="Velg bilde", command=self.select_image)
        self.image_btn.grid(row=7, column=0, sticky="ew", padx=24, pady=4)
        self.thumb_file_label = ctk.CTkLabel(self, text="Ingen valgt", anchor="w")
        self.thumb_file_label.grid(row=8, column=0, sticky="w", padx=24, pady=(0, 0))
        self.thumbnail_label = ctk.CTkLabel(self, text="")
        self.thumbnail_label.grid(row=9, column=0, sticky="w", padx=24, pady=(0, 12))

        # Merge button
        self.merge_btn = ctk.CTkButton(self, text="Slå sammen og eksporter", command=self.merge, fg_color="#4CAF50", text_color="white", font=ctk.CTkFont(size=16, weight="bold"))
        self.merge_btn.grid(row=10, column=0, sticky="ew", padx=24, pady=16)

        # Status bar
        self.status_var = ctk.StringVar(value="Velg video og lyd.")
        self.status_bar = ctk.CTkLabel(self, textvariable=self.status_var, anchor="w", height=28)
        self.status_bar.grid(row=11, column=0, sticky="ew", padx=0, pady=(0, 0))

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
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.bmp")])
        if path:
            self.image_path = path
            self.status_var.set(f"Bilde valgt: {os.path.basename(path)} (kun thumbnail)")
            self.thumb_file_label.configure(text=os.path.basename(path))
            try:
                img = Image.open(path)
                img.thumbnail((60, 60))
                self.image_thumbnail = ImageTk.PhotoImage(img)
                self.thumbnail_label.configure(image=self.image_thumbnail, text="")
                self.thumbnail_label.image = self.image_thumbnail
            except Exception as e:
                self.thumbnail_label.configure(image="", text=f"(Forhåndsvisning feilet: {e})")
        else:
            self.thumb_file_label.configure(text="Ingen valgt")
            self.thumbnail_label.configure(image="", text="")

    def check_ready(self):
        if self.video_path and self.audio_path:
            self.merge_btn.configure(state="normal")
            self.status_var.set("Klar til å slå sammen.")

    def merge(self):
        output_path = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 Video", "*.mp4")])
        if not output_path:
            self.status_var.set("Ingen fil valgt for eksport.")
            return
        self.status_var.set("Slår sammen video og lyd...")
        if not self.video_path or not self.audio_path:
            self.status_var.set("Du må velge både video og lyd.")
            messagebox.showerror("Feil", "Du må velge både video og lyd for å eksportere.")
            return
        temp_output = output_path + ".temp.mp4"
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
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                # Legg til thumbnail hvis valgt
                if self.image_path:
                    ext = os.path.splitext(self.image_path)[1].lower()
                    if ext not in [".jpg", ".jpeg", ".png"]:
                        self.status_var.set("Video eksportert, men thumbnail må være JPG eller PNG.")
                        os.rename(temp_output, output_path)
                    else:
                        thumb_cmd = [
                            "ffmpeg", "-y",
                            "-i", temp_output,
                            "-i", self.image_path,
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
                        if thumb_result.returncode == 0:
                            self.status_var.set(f"Ferdig: {os.path.basename(output_path)} eksportert med thumbnail.")
                        else:
                            self.status_var.set("Video eksportert, men thumbnail feilet.")
                else:
                    os.rename(temp_output, output_path)
                    self.status_var.set(f"Ferdig: {os.path.basename(output_path)} eksportert.")
            else:
                self.status_var.set("Feil under sammenslåing.")
        except Exception as e:
            self.status_var.set("Feil under sammenslåing.")

if __name__ == "__main__":
    app = VideoAudioMergerApp()
    app.mainloop()
