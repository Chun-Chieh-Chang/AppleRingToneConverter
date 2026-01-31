import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
from core.converter import AudioConverter

class DesktopRingtoneApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Apple Audio Converter")
        self.root.geometry("600x500")
        self.root.configure(bg="#f8f9fa")

        self.converter = AudioConverter()
        self.file_path = tk.StringVar()
        self.status = tk.StringVar(value="Ready")
        
        # Trimming variables
        self.enable_trim = tk.BooleanVar(value=False)
        self.start_time = tk.StringVar(value="00:00:00")
        self.end_time = tk.StringVar(value="00:00:30")

        self._build_ui()
        self._check_ffmpeg()

    def _build_ui(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        main_frame = ttk.Frame(self.root, padding="25")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Header
        title_lbl = ttk.Label(main_frame, text="🎵 Apple Ringtone Converter", font=("Helvetica", 18, "bold"))
        title_lbl.pack(pady=(0, 20))

        # File Selection
        file_group = ttk.LabelFrame(main_frame, text=" 1. Select Source File ", padding="10")
        file_group.pack(fill=tk.X, pady=10)

        entry = ttk.Entry(file_group, textvariable=self.file_path)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        browse_btn = ttk.Button(file_group, text="Browse...", command=self.browse_file)
        browse_btn.pack(side=tk.RIGHT)

        # Trimming Options
        trim_group = ttk.LabelFrame(main_frame, text=" 2. Trimming Options (Optional) ", padding="10")
        trim_group.pack(fill=tk.X, pady=10)

        trim_cb = ttk.Checkbutton(trim_group, text="Enable Trimming", variable=self.enable_trim, command=self._toggle_trim)
        trim_cb.pack(anchor=tk.W)

        self.trim_controls = ttk.Frame(trim_group)
        self.trim_controls.pack(fill=tk.X, pady=5)

        ttk.Label(self.trim_controls, text="Start:").pack(side=tk.LEFT, padx=5)
        st_entry = ttk.Entry(self.trim_controls, textvariable=self.start_time, width=10)
        st_entry.pack(side=tk.LEFT, padx=5)

        ttk.Label(self.trim_controls, text="End:").pack(side=tk.LEFT, padx=5)
        et_entry = ttk.Entry(self.trim_controls, textvariable=self.end_time, width=10)
        et_entry.pack(side=tk.LEFT, padx=5)
        
        self._toggle_trim() # Initial state

        # Action Button
        self.convert_btn = ttk.Button(main_frame, text="Convert to .m4r Ringtone", command=self.start_conversion, state=tk.DISABLED)
        self.convert_btn.pack(pady=20, ipadx=20, ipady=10)

        # Status & Log
        status_lbl = ttk.Label(main_frame, textvariable=self.status, font=("Consolas", 10, "bold"), foreground="#28a745")
        status_lbl.pack(anchor=tk.W)

        self.log_text = tk.Text(main_frame, height=6, font=("Consolas", 9), state=tk.DISABLED, bg="#ffffff", borderwidth=1, relief="solid")
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

    def _toggle_trim(self):
        state = tk.NORMAL if self.enable_trim.get() else tk.DISABLED
        for child in self.trim_controls.winfo_children():
            if isinstance(child, ttk.Entry) or isinstance(child, ttk.Label):
                try:
                    child.configure(state=state)
                except:
                    pass

    def _check_ffmpeg(self):
        if not self.converter.ffmpeg_path:
            self.log("ERROR: FFmpeg not found.")
            self.status.set("Error: FFmpeg missing")
            messagebox.showerror("Dependency Error", "FFmpeg is required. Please install it or place ffmpeg.exe in a 'bin' folder.")
            return False
        self.log(f"FFmpeg detected: {self.converter.ffmpeg_path}")
        return True

    def browse_file(self):
        file = filedialog.askopenfilename(filetypes=[("Video/Audio", "*.mp4;*.mkv;*.avi;*.mov;*.mp3;*.wav;*.flac;*.m4a"), ("All Files", "*.*")])
        if file:
            self.file_path.set(file)
            self.convert_btn.config(state=tk.NORMAL)
            self.log(f"Selected: {os.path.basename(file)}")

    def log(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def start_conversion(self):
        input_path = self.file_path.get()
        if not input_path: return

        # Prepare output
        folder = os.path.dirname(input_path)
        filename = os.path.splitext(os.path.basename(input_path))[0]
        suffix = "_trim" if self.enable_trim.get() else ""
        output_path = os.path.join(folder, f"{filename}{suffix}.m4r")

        self.status.set("Processing...")
        self.convert_btn.config(state=tk.DISABLED)
        
        args = {
            "input_path": input_path,
            "output_path": output_path,
        }
        if self.enable_trim.get():
            args["start_time"] = self.start_time.get()
            args["end_time"] = self.end_time.get()

        t = threading.Thread(target=self._run_conversion, kwargs=args)
        t.daemon = True
        t.start()

    def _run_conversion(self, **kwargs):
        try:
            self.log("Converting...")
            self.converter.convert_to_m4r(**kwargs, progress_callback=None)
            self.root.after(0, lambda: self._on_success(kwargs["output_path"]))
        except Exception as e:
            self.root.after(0, lambda: self._on_error(str(e)))

    def _on_success(self, path):
        self.status.set("Done!")
        self.log(f"Success: {path}")
        self.convert_btn.config(state=tk.NORMAL)
        messagebox.showinfo("Success", f"Ringtone saved to:\n{path}")

    def _on_error(self, msg):
        self.status.set("Error")
        self.log(f"Failed: {msg}")
        self.convert_btn.config(state=tk.NORMAL)
        messagebox.showerror("Error", msg)

if __name__ == "__main__":
    root = tk.Tk()
    app = DesktopRingtoneApp(root)
    root.mainloop()
