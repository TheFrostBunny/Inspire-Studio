import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os
from PIL import Image, ImageTk

class VideoAudioMergerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video + Audio Merger")
        self.video_path = None
        self.audio_path = None

        tk.Label(root, text="Velg video:").pack(pady=5)
        self.video_btn = tk.Button(root, text="Velg video", command=self.select_video)
        self.video_btn.pack(pady=5)

        tk.Label(root, text="Velg lyd:").pack(pady=5)
        self.audio_btn = tk.Button(root, text="Velg lyd", command=self.select_audio)
        self.audio_btn.pack(pady=5)

        self.merge_btn = tk.Button(root, text="Slå sammen og eksporter", command=self.merge, state=tk.DISABLED)
        self.merge_btn.pack(pady=20)

        self.image_path = None
        self.image_thumbnail = None
        self.status_var = tk.StringVar()
        self.status_var.set("Velg video og lyd.")
        self.status_bar = tk.Label(root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)

        self.image_btn = tk.Button(root, text="(Valgfritt) Velg bilde (thumbnail)", command=self.select_image)
        self.image_btn.pack(pady=5)
        self.thumbnail_label = tk.Label(root)
        self.thumbnail_label.pack(pady=5)

    def select_video(self):
        path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4;*.mov;*.avi;*.mkv")])
        if path:
            self.video_path = path
            self.status_var.set(f"Video valgt: {os.path.basename(path)}")
            self.check_ready()

    def select_audio(self):
        path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3;*.wav;*.aac;*.ogg")])
        if path:
            self.audio_path = path
            self.status_var.set(f"Lyd valgt: {os.path.basename(path)}")
            self.check_ready()

    def select_image(self):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.bmp")])
        if path:
            self.image_path = path
            self.status_var.set(f"Bilde valgt: {os.path.basename(path)} (kun thumbnail)")
            try:
                img = Image.open(path)
                img.thumbnail((120, 120))
                self.image_thumbnail = ImageTk.PhotoImage(img)
                self.thumbnail_label.config(image=self.image_thumbnail, text="")
                self.thumbnail_label.image = self.image_thumbnail  # Prevent garbage collection
            except Exception as e:
                self.thumbnail_label.config(image="", text=f"(Forhåndsvisning feilet: {e})")

    def check_ready(self):
        if self.video_path and self.audio_path:
            self.merge_btn.config(state=tk.NORMAL)
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
            "ffmpeg",
            "-y",
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
                        messagebox.showwarning("Advarsel", "Video eksportert, men thumbnail må være JPG eller PNG.")
                        os.rename(temp_output, output_path)
                    else:
                        # For best compatibility, convert PNG to JPEG if needed
                        cover_path = self.image_path
                        if ext == ".png":
                            try:
                                from PIL import Image
                                img = Image.open(self.image_path)
                                cover_path = self.image_path + ".jpg"
                                img.convert("RGB").save(cover_path, "JPEG")
                            except Exception as e:
                                self.status_var.set(f"Video eksportert, men thumbnail-konvertering feilet: {e}")
                                messagebox.showwarning("Advarsel", f"Video eksportert, men thumbnail-konvertering feilet: {e}")
                                os.rename(temp_output, output_path)
                                return
                        thumb_cmd = [
                            "ffmpeg", "-y",
                            "-i", temp_output,
                            "-i", cover_path,
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
                        if ext == ".png" and os.path.exists(cover_path):
                            try:
                                os.remove(cover_path)
                            except Exception:
                                pass
                        if thumb_result.returncode == 0:
                            self.status_var.set(f"Ferdig: {os.path.basename(output_path)} eksportert med thumbnail.")
                            messagebox.showinfo("Ferdig", f"Video eksportert til:\n{output_path}\nThumbnail lagt til.")
                        else:
                            self.status_var.set("Video eksportert, men thumbnail feilet.")
                            messagebox.showwarning("Advarsel", f"Video eksportert, men thumbnail kunne ikke legges til:\n{thumb_result.stderr}")
                else:
                    os.rename(temp_output, output_path)
                    self.status_var.set(f"Ferdig: {os.path.basename(output_path)} eksportert.")
                    messagebox.showinfo("Ferdig", f"Video eksportert til:\n{output_path}")
            else:
                self.status_var.set("Feil under sammenslåing.")
                messagebox.showerror("Feil", f"Kunne ikke slå sammen:\n{result.stderr}")
        except Exception as e:
            self.status_var.set("Feil under sammenslåing.")
            messagebox.showerror("Feil", f"Kunne ikke slå sammen:\n{e}")
        finally:
            if os.path.exists(temp_output):
                try:
                    os.remove(temp_output)
                except Exception:
                    pass

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoAudioMergerApp(root)
    root.mainloop()
