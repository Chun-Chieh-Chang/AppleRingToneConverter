import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
import tempfile
import time
from core.converter import AudioConverter
from core.utils import format_seconds, parse_seconds

# Optional Visual Preview modules
try:
    import cv2
    from PIL import Image, ImageTk
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False

# Windows audio playback
try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False

class DesktopRingtoneApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Apple Ringtone Converter - 直觀視訊/音訊預覽版")
        self.root.geometry("740x880")
        self.root.minsize(680, 750)
        self.root.configure(bg="#f8fafc")

        self.converter = AudioConverter()
        self.file_path = tk.StringVar()
        self.status = tk.StringVar(value="準備就緒")
        
        # Media state
        self.cap = None
        self.media_info = {"duration": 0, "has_video": False, "has_audio": False}
        self.total_duration = 0.0
        self.is_video_playing = False
        self.play_thread = None
        self.current_preview_photo = None
        self.preview_wav_path = None

        # Trimming variables
        self.enable_trim = tk.BooleanVar(value=True)
        self.fixed_30s = tk.BooleanVar(value=True)
        self.start_seconds = tk.DoubleVar(value=0.0)
        self.end_seconds = tk.DoubleVar(value=30.0)
        self.start_time_str = tk.StringVar(value="00:00:00")
        self.end_time_str = tk.StringVar(value="00:00:30")

        self._build_ui()
        self._check_ffmpeg()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Color palette tokens
        bg_base = "#f8fafc"
        surface_card = "#ffffff"
        border_color = "#e2e8f0"
        primary_blue = "#2563eb"
        text_primary = "#0f172a"
        text_secondary = "#64748b"

        style.configure(".", background=bg_base, foreground=text_primary, font=("Microsoft JhengHei UI", 9))
        style.configure("Card.TFrame", background=surface_card, relief="solid", borderwidth=1)
        style.configure("Header.TLabel", font=("Microsoft JhengHei UI", 16, "bold"), foreground=text_primary, background=bg_base)
        style.configure("Sub.TLabel", font=("Microsoft JhengHei UI", 9), foreground=text_secondary, background=bg_base)
        style.configure("Primary.TButton", font=("Microsoft JhengHei UI", 10, "bold"), background=primary_blue, foreground="#ffffff")
        style.map("Primary.TButton", background=[("active", "#1d4ed8")])

        # Main Scrollable / Padded Container
        container = ttk.Frame(self.root, padding="16")
        container.pack(fill=tk.BOTH, expand=True)

        # Header
        header_frame = ttk.Frame(container)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(header_frame, text="🎵 Apple Ringtone Converter", style="Header.TLabel").pack(anchor=tk.W)
        ttk.Label(header_frame, text="即時視訊/音訊畫面預覽與 30 秒片段試聽，精準定位副歌", style="Sub.TLabel").pack(anchor=tk.W)

        # Step 1: File Selection Card
        step1_card = ttk.LabelFrame(container, text=" 1. 選擇來源影音檔案 ", padding="10")
        step1_card.pack(fill=tk.X, pady=(0, 10))

        file_row = ttk.Frame(step1_card)
        file_row.pack(fill=tk.X)
        self.file_entry = ttk.Entry(file_row, textvariable=self.file_path, font=("Consolas", 9))
        self.file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))

        browse_btn = ttk.Button(file_row, text="瀏覽檔案...", command=self.browse_file)
        browse_btn.pack(side=tk.RIGHT)

        # Step 2: Live Media Preview Window (Visual)
        self.preview_group = ttk.LabelFrame(container, text=" 2. 即時畫面與媒體預覽 (Live Media Preview) ", padding="10")
        self.preview_group.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Canvas for Video Frame or Audio Graphic
        self.preview_width = 440
        self.preview_height = 240
        self.canvas_frame = tk.Frame(self.preview_group, bg="#0f172a", width=self.preview_width, height=self.preview_height)
        self.canvas_frame.pack(pady=5)
        self.canvas_frame.pack_propagate(False)

        self.preview_label = tk.Label(self.canvas_frame, bg="#0f172a", fg="#94a3b8", text="尚未選擇檔案\n支援 MP4, MKV, AVI, MOV, MP3, WAV 等", font=("Microsoft JhengHei UI", 10))
        self.preview_label.pack(fill=tk.BOTH, expand=True)

        # Preview Controls (Play/Pause for video)
        self.preview_ctrl_frame = ttk.Frame(self.preview_group)
        self.preview_ctrl_frame.pack(fill=tk.X, pady=(5, 0))

        self.play_btn = ttk.Button(self.preview_ctrl_frame, text="▶️ 播放視訊", command=self.toggle_video_play, state=tk.DISABLED)
        self.play_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.media_info_lbl = ttk.Label(self.preview_ctrl_frame, text="時長: --:--:--", style="Sub.TLabel")
        self.media_info_lbl.pack(side=tk.LEFT)

        # Step 3: Trimming & Auditory Preview
        trim_card = ttk.LabelFrame(container, text=" 3. 剪輯時間軸與聽覺試聽 (Trimming & Auditory Preview) ", padding="10")
        trim_card.pack(fill=tk.X, pady=(0, 10))

        # Toggles
        toggle_row = ttk.Frame(trim_card)
        toggle_row.pack(fill=tk.X, pady=(0, 5))
        ttk.Checkbutton(toggle_row, text="啟用時間剪輯", variable=self.enable_trim, command=self._toggle_trim).pack(side=tk.LEFT, padx=(0, 15))
        ttk.Checkbutton(toggle_row, text="🔒 鎖定 30 秒長度 (iPhone 鈴聲規格)", variable=self.fixed_30s, command=self._on_fixed_toggle).pack(side=tk.LEFT)

        # Sliders Frame
        self.slider_frame = ttk.Frame(trim_card)
        self.slider_frame.pack(fill=tk.X, pady=5)

        # Start Slider
        s_lbl_row = ttk.Frame(self.slider_frame)
        s_lbl_row.pack(fill=tk.X)
        ttk.Label(s_lbl_row, text="鈴聲起點 (拖動即時同步畫面):").pack(side=tk.LEFT)
        self.start_disp_lbl = ttk.Label(s_lbl_row, textvariable=self.start_time_str, font=("Consolas", 9, "bold"), foreground=primary_blue)
        self.start_disp_lbl.pack(side=tk.RIGHT)

        self.start_scale = ttk.Scale(self.slider_frame, from_=0, to=100, variable=self.start_seconds, command=self._on_start_scale_move)
        self.start_scale.pack(fill=tk.X, pady=(2, 6))

        # End Slider
        e_lbl_row = ttk.Frame(self.slider_frame)
        e_lbl_row.pack(fill=tk.X)
        ttk.Label(e_lbl_row, text="鈴聲終點:").pack(side=tk.LEFT)
        self.end_disp_lbl = ttk.Label(e_lbl_row, textvariable=self.end_time_str, font=("Consolas", 9, "bold"), foreground=primary_blue)
        self.end_disp_lbl.pack(side=tk.RIGHT)

        self.end_scale = ttk.Scale(self.slider_frame, from_=0, to=100, variable=self.end_seconds, command=self._on_end_scale_move)
        self.end_scale.pack(fill=tk.X, pady=(2, 6))

        # Auditory Testing Row
        audio_test_row = ttk.Frame(trim_card)
        audio_test_row.pack(fill=tk.X, pady=(6, 0))

        self.auditory_test_btn = ttk.Button(audio_test_row, text="🎧 試聽選定鈴聲片段 (Preview 30s)", command=self.test_audio_segment, state=tk.DISABLED)
        self.auditory_test_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.stop_audio_btn = ttk.Button(audio_test_row, text="⏹️ 停止試聽", command=self.stop_audio_playback, state=tk.DISABLED)
        self.stop_audio_btn.pack(side=tk.LEFT)

        self.audio_status_lbl = ttk.Label(audio_test_row, text="", foreground="#10b981", font=("Microsoft JhengHei UI", 8))
        self.audio_status_lbl.pack(side=tk.LEFT, padx=10)

        # Step 4: Convert & Output Action
        action_row = ttk.Frame(container)
        action_row.pack(fill=tk.X, pady=(5, 5))

        self.convert_btn = ttk.Button(
            action_row,
            text="🚀 轉檔為 iPhone 鈴聲 (.m4r)",
            style="Primary.TButton",
            command=self.start_conversion,
            state=tk.DISABLED
        )
        self.convert_btn.pack(fill=tk.X, ipady=6)

        # Status & Console Log
        status_bar = ttk.Frame(container)
        status_bar.pack(fill=tk.X, pady=(5, 2))
        ttk.Label(status_bar, text="狀態:").pack(side=tk.LEFT)
        self.status_lbl = ttk.Label(status_bar, textvariable=self.status, font=("Consolas", 9, "bold"), foreground="#2563eb")
        self.status_lbl.pack(side=tk.LEFT, padx=5)

        self.log_text = tk.Text(container, height=4, font=("Consolas", 8), state=tk.DISABLED, bg="#ffffff", borderwidth=1, relief="solid")
        self.log_text.pack(fill=tk.BOTH, expand=False)

    def _check_ffmpeg(self):
        if not self.converter.ffmpeg_path:
            self.log("ERROR: 未檢測到 FFmpeg。")
            self.status.set("錯誤: FFmpeg 未安裝")
            messagebox.showerror("依賴錯誤", "請安裝 FFmpeg 或將 ffmpeg.exe 放置於專案根目錄或 bin 目錄。")
            return False
        self.log(f"已就緒: FFmpeg -> {self.converter.ffmpeg_path}")
        return True

    def browse_file(self):
        file = filedialog.askopenfilename(
            title="選擇影音檔案",
            filetypes=[
                ("影音媒體檔案", "*.mp4;*.mkv;*.avi;*.mov;*.webm;*.mp3;*.wav;*.flac;*.m4a"),
                ("所有檔案", "*.*")
            ]
        )
        if file:
            self.stop_audio_playback()
            self.stop_video_play()
            self.file_path.set(file)
            self.load_media_preview(file)

    def load_media_preview(self, path):
        self.log(f"載入檔案: {os.path.basename(path)}")
        self.status.set("正在分析檔案資訊...")

        # Release previous cv2 capture
        if self.cap:
            self.cap.release()
            self.cap = None

        try:
            info = self.converter.get_media_info(path)
            self.media_info = info
            self.total_duration = max(1.0, info.get("duration", 30.0))
        except Exception as e:
            self.log(f"檔案探測警告: {e}")
            self.media_info = {"duration": 30.0, "has_video": False, "has_audio": True}
            self.total_duration = 30.0

        # Update Scales
        self.start_scale.config(to=self.total_duration)
        self.end_scale.config(to=self.total_duration)
        
        self.start_seconds.set(0.0)
        end_val = min(30.0, self.total_duration)
        self.end_seconds.set(end_val)
        self.start_time_str.set(format_seconds(0))
        self.end_time_str.set(format_seconds(end_val))

        dur_str = format_seconds(self.total_duration)
        self.media_info_lbl.config(text=f"時長: {dur_str} | 類型: {'視訊(Video)' if info.get('has_video') else '純音訊(Audio)'}")

        # Visual Frame Handling
        if HAS_CV2 and info.get("has_video"):
            try:
                self.cap = cv2.VideoCapture(path)
                self.show_frame_at_second(0.0)
                self.play_btn.config(state=tk.NORMAL)
            except Exception as e:
                self.log(f"無法開啟視訊影格: {e}")
                self._show_audio_card(path)
        else:
            self._show_audio_card(path)

        self.auditory_test_btn.config(state=tk.NORMAL)
        self.convert_btn.config(state=tk.NORMAL)
        self.status.set("檔案載入完成")

    def _show_audio_card(self, path):
        self.play_btn.config(state=tk.DISABLED)
        # Display audio graphic in canvas
        self.preview_label.config(
            image="",
            text=f"🎵 純音訊檔案預覽\n\n檔名: {os.path.basename(path)}\n總長度: {format_seconds(self.total_duration)}\n\n💡 請拖動下方滑桿選取 30 秒片段並點擊試聽",
            font=("Microsoft JhengHei UI", 10, "bold"),
            fg="#60a5fa"
        )

    def show_frame_at_second(self, sec):
        if not self.cap or not HAS_CV2:
            return
        self.cap.set(cv2.CAP_PROP_POS_MSEC, sec * 1000)
        ret, frame = self.cap.read()
        if ret:
            # Resize while preserving aspect ratio
            h, w = frame.shape[:2]
            aspect = w / h
            target_w = self.preview_width
            target_h = int(target_w / aspect)
            if target_h > self.preview_height:
                target_h = self.preview_height
                target_w = int(target_h * aspect)

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(frame_rgb).resize((target_w, target_h), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(pil_img)
            self.current_preview_photo = photo
            self.preview_label.config(image=photo, text="")

    def toggle_video_play(self):
        if self.is_video_playing:
            self.stop_video_play()
        else:
            self.start_video_play()

    def start_video_play(self):
        if not self.cap or not HAS_CV2:
            return
        self.is_video_playing = True
        self.play_btn.config(text="⏸️ 暫停視訊")
        
        def play_loop():
            fps = self.cap.get(cv2.CAP_PROP_FPS) or 25
            delay = 1.0 / fps
            while self.is_video_playing and self.cap:
                ret, frame = self.cap.read()
                if not ret:
                    # Loop back to start
                    self.cap.set(cv2.CAP_PROP_POS_MSEC, self.start_seconds.get() * 1000)
                    continue

                curr_pos_ms = self.cap.get(cv2.CAP_PROP_POS_MSEC)
                curr_sec = curr_pos_ms / 1000.0

                # Check if exceed end time
                if curr_sec > self.end_seconds.get():
                    self.cap.set(cv2.CAP_PROP_POS_MSEC, self.start_seconds.get() * 1000)
                    continue

                # Render frame in main thread
                try:
                    h, w = frame.shape[:2]
                    aspect = w / h
                    target_w = self.preview_width
                    target_h = int(target_w / aspect)
                    if target_h > self.preview_height:
                        target_h = self.preview_height
                        target_w = int(target_h * aspect)

                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    pil_img = Image.fromarray(frame_rgb).resize((target_w, target_h), Image.Resampling.BILINEAR)
                    photo = ImageTk.PhotoImage(pil_img)
                    self.root.after(0, self._update_play_frame, photo)
                except:
                    break
                time.sleep(delay)

        self.play_thread = threading.Thread(target=play_loop, daemon=True)
        self.play_thread.start()

    def _update_play_frame(self, photo):
        if self.is_video_playing:
            self.current_preview_photo = photo
            self.preview_label.config(image=photo, text="")

    def stop_video_play(self):
        self.is_video_playing = False
        self.play_btn.config(text="▶️ 播放視訊")

    def _on_start_scale_move(self, val):
        s = float(val)
        self.start_time_str.set(format_seconds(s))
        if self.fixed_30s.get():
            e = min(self.total_duration, s + 30.0)
            self.end_seconds.set(e)
            self.end_time_str.set(format_seconds(e))
        else:
            if s > self.end_seconds.get():
                self.end_seconds.set(s)
                self.end_time_str.set(format_seconds(s))

        # Real-time frame update on scrub
        if not self.is_video_playing:
            self.show_frame_at_second(s)

    def _on_end_scale_move(self, val):
        e = float(val)
        self.end_time_str.set(format_seconds(e))
        if self.fixed_30s.get():
            s = max(0.0, e - 30.0)
            self.start_seconds.set(s)
            self.start_time_str.set(format_seconds(s))
            if not self.is_video_playing:
                self.show_frame_at_second(s)
        else:
            if e < self.start_seconds.get():
                self.start_seconds.set(e)
                self.start_time_str.set(format_seconds(e))
            if not self.is_video_playing:
                self.show_frame_at_second(e)

    def _on_fixed_toggle(self):
        if self.fixed_30s.get():
            s = self.start_seconds.get()
            e = min(self.total_duration, s + 30.0)
            self.end_seconds.set(e)
            self.end_time_str.set(format_seconds(e))

    def _toggle_trim(self):
        state = tk.NORMAL if self.enable_trim.get() else tk.DISABLED
        self.start_scale.config(state=state)
        self.end_scale.config(state=state)
        self.auditory_test_btn.config(state=state)

    def test_audio_segment(self):
        input_path = self.file_path.get()
        if not input_path:
            return

        self.audio_status_lbl.config(text="正在擷取試聽片段...", foreground="#2563eb")
        self.stop_audio_playback()

        def run_extract_and_play():
            try:
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf:
                    wav_path = tf.name

                s_time = self.start_time_str.get()
                e_time = self.end_time_str.get()
                self.converter.extract_preview_audio(input_path, s_time, e_time, wav_path)
                self.preview_wav_path = wav_path

                if HAS_WINSOUND:
                    winsound.PlaySound(wav_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
                    self.root.after(0, lambda: self._on_audio_play_started(s_time, e_time))
                else:
                    self.root.after(0, lambda: self.audio_status_lbl.config(text="此系統無 winsound 模組", foreground="#ef4444"))
            except Exception as e:
                self.root.after(0, lambda: self.audio_status_lbl.config(text=f"試聽失敗: {e}", foreground="#ef4444"))

        t = threading.Thread(target=run_extract_and_play, daemon=True)
        t.start()

    def _on_audio_play_started(self, s, e):
        self.audio_status_lbl.config(text=f"🔊 正在試聽: {s} ➜ {e}", foreground="#10b981")
        self.stop_audio_btn.config(state=tk.NORMAL)

    def stop_audio_playback(self):
        if HAS_WINSOUND:
            try:
                winsound.PlaySound(None, winsound.SND_PURGE)
            except:
                pass
        self.audio_status_lbl.config(text="")
        self.stop_audio_btn.config(state=tk.DISABLED)

    def start_conversion(self):
        input_path = self.file_path.get()
        if not input_path:
            return

        self.stop_audio_playback()
        self.stop_video_play()

        folder = os.path.dirname(input_path)
        filename = os.path.splitext(os.path.basename(input_path))[0]
        suffix = "_ringtone" if self.enable_trim.get() else ""
        output_path = os.path.join(folder, f"{filename}{suffix}.m4r")

        self.status.set("高規格編碼中...")
        self.convert_btn.config(state=tk.DISABLED)

        args = {
            "input_path": input_path,
            "output_path": output_path,
        }
        if self.enable_trim.get():
            args["start_time"] = self.start_time_str.get()
            args["end_time"] = self.end_time_str.get()

        t = threading.Thread(target=self._run_conversion, kwargs=args, daemon=True)
        t.start()

    def _run_conversion(self, **kwargs):
        try:
            self.log(f"開始轉換: {kwargs['input_path']}")
            self.converter.convert_to_m4r(**kwargs)
            self.root.after(0, lambda: self._on_success(kwargs["output_path"]))
        except Exception as e:
            self.root.after(0, lambda: self._on_error(str(e)))

    def _on_success(self, path):
        self.status.set("轉檔成功！")
        self.log(f"🎉 鈴聲已儲存至: {path}")
        self.convert_btn.config(state=tk.NORMAL)
        messagebox.showinfo("轉檔成功", f"鈴聲已順利建立！\n檔案路徑:\n{path}")

    def _on_error(self, msg):
        self.status.set("轉檔失敗")
        self.log(f"❌ 錯誤: {msg}")
        self.convert_btn.config(state=tk.NORMAL)
        messagebox.showerror("轉檔失敗", msg)

    def log(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def _on_close(self):
        self.stop_video_play()
        self.stop_audio_playback()
        if self.cap:
            self.cap.release()
            self.cap = None
        if self.preview_wav_path and os.path.exists(self.preview_wav_path):
            try:
                os.remove(self.preview_wav_path)
            except:
                pass
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = DesktopRingtoneApp(root)
    root.mainloop()
