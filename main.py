import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
from converter import AudioConverter
import webbrowser

class AudioConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Apple Audio Converter (Lossless/High-Quality)")
        self.root.geometry("600x400")
        self.root.configure(bg="#f0f0f0")

        self.converter = AudioConverter()
        
        self.file_path = tk.StringVar()
        self.status = tk.StringVar(value="Ready")

        self._build_ui()
        self._check_ffmpeg()

    def _build_ui(self):
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Main Frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_lbl = ttk.Label(main_frame, text="Video to iPhone Ringtone Converter", font=("Helvetica", 16, "bold"))
        title_lbl.pack(pady=(0, 20))

        # File Selection
        file_frame = ttk.LabelFrame(main_frame, text="Select Video File (MP4, etc.)", padding="10")
        file_frame.pack(fill=tk.X, pady=10)

        entry = ttk.Entry(file_frame, textvariable=self.file_path)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        browse_btn = ttk.Button(file_frame, text="Browse...", command=self.browse_file)
        browse_btn.pack(side=tk.RIGHT)

        # Convert Button
        self.convert_btn = ttk.Button(main_frame, text="Convert to M4R", command=self.start_conversion, state=tk.DISABLED)
        self.convert_btn.pack(pady=20, ipadx=20, ipady=10)

        # Status & Log
        status_lbl = ttk.Label(main_frame, textvariable=self.status, font=("Consolas", 10))
        status_lbl.pack(anchor=tk.W)

        self.log_text = tk.Text(main_frame, height=8, font=("Consolas", 9), state=tk.DISABLED, bg="#ffffff")
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

    def _check_ffmpeg(self):
        if not self.converter.ffmpeg_path:
            self.log("ERROR: FFmpeg not found on this system.")
            self.log("Please download FFmpeg and place 'ffmpeg.exe' in a 'bin' folder here, or install it to your PATH.")
            self.status.set("Error: FFmpeg missing")
            messagebox.showerror("Missing Dependency", "FFmpeg is required but not found.\n\nPlease install FFmpeg or place the executable in the 'bin' folder.")
            # Verify if we can offer a link
            # webbrowser.open("https://ffmpeg.org/download.html") 
            return False
        self.log(f"FFmpeg found at: {self.converter.ffmpeg_path}")
        return True

    def browse_file(self):
        file = filedialog.askopenfilename(filetypes=[("Video/Audio Files", "*.mp4;*.mkv;*.avi;*.mov;*.mp3"), ("All Files", "*.*")])
        if file:
            self.file_path.set(file)
            self.convert_btn.config(state=tk.NORMAL)
            self.log(f"Selected: {file}")

    def log(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def start_conversion(self):
        input_path = self.file_path.get()
        if not input_path:
            return

        if not self.converter.ffmpeg_path:
             messagebox.showerror("Error", "FFmpeg not available.")
             return

        # Prepare output path
        folder = os.path.dirname(input_path)
        filename = os.path.splitext(os.path.basename(input_path))[0]
        output_path = os.path.join(folder, f"{filename}.m4r")

        self.status.set("Converting...")
        self.convert_btn.config(state=tk.DISABLED)
        
        # Run in thread
        t = threading.Thread(target=self._run_process, args=(input_path, output_path))
        t.daemon = True
        t.start()

    def _run_process(self, input_path, output_path):
        try:
            self.log("Starting conversion...")
            self.converter.convert_to_m4r(input_path, output_path, self._log_progress)
            self.root.after(0, lambda: self._conversion_success(output_path))
        except Exception as e:
            self.root.after(0, lambda: self._conversion_error(str(e)))

    def _log_progress(self, line):
        # We could parse this, but just logging is fine for now
        # self.root.after(0, lambda: self.log(line.strip()))
        pass

    def _conversion_success(self, output_path):
        self.status.set("Done!")
        self.log(f"Success! Saved to: {output_path}")
        self.convert_btn.config(state=tk.NORMAL)
        messagebox.showinfo("Success", f"Ringtone created:\n{output_path}")

    def _conversion_error(self, error_msg):
        self.status.set("Error")
        self.log(f"Error: {error_msg}")
        self.convert_btn.config(state=tk.NORMAL)
        messagebox.showerror("Conversion Failed", error_msg)

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioConverterApp(root)
    root.mainloop()
