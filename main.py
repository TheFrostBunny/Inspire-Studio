import customtkinter as ctk
from video_audio_merger import VideoAudioMergerApp
from youtube_downloader import YouTubeDownloaderApp
import threading
try:
    import pystray
    from PIL import Image
except ImportError:
    pystray = None
    Image = None

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Video + Audio Merger & YouTube Downloader")
        self.geometry("520x620")
        self.resizable(False, False)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.menu_frame = ctk.CTkFrame(self, height=48)
        self.menu_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 0))
        self.menu_frame.grid_columnconfigure(0, weight=1)
        self.menu_frame.grid_columnconfigure(1, weight=1)
        self.va_btn = ctk.CTkButton(self.menu_frame, text="Video + Audio Merger", command=self.show_va, fg_color="#3A7CA5", text_color="white", font=ctk.CTkFont(size=15, weight="bold"))
        self.va_btn.grid(row=0, column=0, padx=16, pady=8, sticky="ew")
        self.yt_btn = ctk.CTkButton(self.menu_frame, text="YouTube Downloader", command=self.show_yt, fg_color="#3A7CA5", text_color="white", font=ctk.CTkFont(size=15, weight="bold"))
        self.yt_btn.grid(row=0, column=1, padx=16, pady=8, sticky="ew")

        self.va_app = VideoAudioMergerApp(self)
        self.yt_app = YouTubeDownloaderApp(self)
        self.show_va()

        self.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)
        self.tray_icon = None

    def show_va(self):
        self.va_app.grid(row=1, column=0, sticky="nsew")
        self.yt_app.grid_remove()
        self.va_btn.configure(fg_color="#4CAF50")
        self.yt_btn.configure(fg_color="#3A7CA5")

    def show_yt(self):
        self.yt_app.grid(row=1, column=0, sticky="nsew")
        self.va_app.grid_remove()
        self.yt_btn.configure(fg_color="#4CAF50")
        self.va_btn.configure(fg_color="#3A7CA5")

    def minimize_to_tray(self):
        self.withdraw()
        if pystray and Image:
            icon_img = Image.new("RGB", (64, 64), (58, 140, 255))
            menu = pystray.Menu(
                pystray.MenuItem("Vis", self.restore_window),
                pystray.MenuItem("Avslutt", self.exit_app)
            )
            self.tray_icon = pystray.Icon("VideoAudioMerger", icon_img, "Video + Audio Merger", menu)
            threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def restore_window(self):
        self.deiconify()
        if self.tray_icon:
            self.tray_icon.stop()
            self.tray_icon = None

    def exit_app(self):
        if self.tray_icon:
            self.tray_icon.stop()
        self.destroy()

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
