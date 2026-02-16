import customtkinter as ctk
from video_audio_merger import VideoAudioMergerApp
from youtube_downloader import YouTubeDownloaderApp
import Theme.color_theme
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
        self.title("Inspire Studio")
        self.geometry("400x700")
        self.resizable(False, False)
        self.configure(fg_color=Theme.color_theme.BG_COLOR)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Sentrer vinduet på skjermen
        self.update_idletasks()
        w, h = 500, 700
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = (ws // 2) - (w // 2)
        y = (hs // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

        # App-ikon (kun hvis PIL er tilgjengelig)
        if Image:
            icon_img = Image.new("RGB", (64, 64), (58, 140, 255))
            try:
                import tempfile
                icon_path = tempfile.mktemp(suffix=".ico")
                icon_img.save(icon_path)
                self.iconbitmap(icon_path)
            except Exception:
                pass

        # Toppmeny med moderne stil og ikoner
        self.menu_frame = ctk.CTkFrame(self, height=60, fg_color=Theme.color_theme.MENU_COLOR, corner_radius=12)
        self.menu_frame.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 0))
        self.menu_frame.grid_columnconfigure(0, weight=1)
        self.menu_frame.grid_columnconfigure(1, weight=1)
        self.va_btn = ctk.CTkButton(
            self.menu_frame, text="🎬 Video + Audio", command=self.show_va,
            fg_color=Theme.color_theme.BTN_GREEN, text_color=Theme.color_theme.BTN_TEXT, font=ctk.CTkFont(size=16, weight="bold"), height=44, corner_radius=8, hover_color=Theme.color_theme.BTN_GREEN_HOVER
        )
        self.va_btn.grid(row=0, column=0, padx=14, pady=10, sticky="ew")
        self.yt_btn = ctk.CTkButton(
            self.menu_frame, text="⬇️  YouTube", command=self.show_yt,
            fg_color=Theme.color_theme.BTN_BLUE, text_color=Theme.color_theme.BTN_TEXT, font=ctk.CTkFont(size=16, weight="bold"), height=44, corner_radius=8, hover_color=Theme.color_theme.BTN_BLUE_HOVER
        )
        self.yt_btn.grid(row=0, column=1, padx=14, pady=10, sticky="ew")

        # Innholdsruter
        self.content_frame = ctk.CTkFrame(self, fg_color=Theme.color_theme.CONTENT_BG, corner_radius=12)
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=12, pady=12)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

        self.va_app = VideoAudioMergerApp(self.content_frame)
        self.yt_app = YouTubeDownloaderApp(self.content_frame)
        self.va_app.grid(row=0, column=0, sticky="nsew")
        self.yt_app.grid(row=0, column=0, sticky="nsew")
        self.show_va()

        self.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)
        self.tray_icon = None

    def show_va(self):
        self.va_app.grid(row=0, column=0, sticky="nsew")
        self.va_app.tkraise()
        self.yt_btn.configure(fg_color=Theme.color_theme.BTN_BLUE)
        self.va_btn.configure(fg_color=Theme.color_theme.BTN_GREEN)

    def show_yt(self):
        self.yt_app.grid(row=0, column=0, sticky="nsew")
        self.yt_app.tkraise()
        self.va_btn.configure(fg_color=Theme.color_theme.BTN_GREEN)
        self.yt_btn.configure(fg_color=Theme.color_theme.BTN_BLUE)

    def minimize_to_tray(self):
        self.withdraw()
        if pystray and Image:
            icon_img = Image.new("RGB", (64, 64), (58, 140, 255))
            menu = pystray.Menu(
                pystray.MenuItem("Vis Inspire Studio", self.restore_window),
                pystray.MenuItem("Avslutt Inspire Studio", self.exit_app)
            )
            self.tray_icon = pystray.Icon("InspireStudio", icon_img, "Inspire Studio", menu)
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
