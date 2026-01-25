import os
import subprocess
import shutil
import sys
import platform

class AudioConverter:
    def __init__(self):
        self.ffmpeg_path = self._get_ffmpeg_path()

    def _get_ffmpeg_path(self):
        """Locates ffmpeg binary."""
        # Check system PATH
        if shutil.which("ffmpeg"):
            return "ffmpeg"
        
        # Check local bin folder
        local_bin = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bin", "ffmpeg.exe")
        if os.path.exists(local_bin):
            return local_bin

        # Check imageio-ffmpeg
        try:
            import imageio_ffmpeg
            return imageio_ffmpeg.get_ffmpeg_exe()
        except ImportError:
            pass
            
        return None

    def probe_file(self, input_path):
        """Checks file info using ffprobe."""
        if not self.ffmpeg_path:
            raise FileNotFoundError("FFmpeg not found. Please install FFmpeg.")
            
        # We'll use ffmpeg to probe since it's simpler than needing ffprobe separate exe sometimes
        cmd = [self.ffmpeg_path, "-i", input_path]
        
        # ffmpeg prints info to stderr
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()
        
        return stderr

    def convert_to_m4r(self, input_path, output_path, progress_callback=None):
        """
        Converts input video/audio to M4R (AAC).
        Tries to stream copy if possible for lossless quality.
        """
        if not self.ffmpeg_path:
            raise FileNotFoundError("FFmpeg not found.")

        # Probe to see if it's already AAC
        info = self.probe_file(input_path)
        is_aac = "Audio: aac" in info

        cmd = [self.ffmpeg_path, "-y", "-i", input_path, "-vn"] # -vn: disable video

        if is_aac:
            # Stream copy (Lossless)
            print("Detected AAC. Using stream copy for lossless conversion.")
            cmd.extend(["-acodec", "copy"])
        else:
            # Re-encode (High Quality)
            print("Detected non-AAC. Re-encoding at 256k.")
            cmd.extend(["-acodec", "aac", "-b:a", "256k"])

        # Output to .m4a first (ffmpeg is picky about m4r sometimes being strictly m4a container)
        # We will write directly to output_path which should end in .m4r, ffmpeg handles it usually.
        # But safest is -f ipod for m4a/m4r compatibility or just let ffmpeg detect from extension.
        cmd.extend(["-f", "ipod", output_path])

        # Run command
        # For a simple GUI, we might want to run this with Popen to capture output/progress
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        for line in process.stdout:
            if progress_callback:
                progress_callback(line)
        
        process.wait()
        
        if process.returncode != 0:
            raise RuntimeError("Conversion failed.")

        return True
