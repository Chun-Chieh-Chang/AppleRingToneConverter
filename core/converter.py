import os
import subprocess
import shutil

class AudioConverter:
    def __init__(self):
        self.ffmpeg_path = self._get_ffmpeg_path()

    def _get_ffmpeg_path(self):
        """Locates ffmpeg binary."""
        # Check system PATH
        if shutil.which("ffmpeg"):
            return "ffmpeg"
        
        # Check local bin folder
        local_bin = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bin", "ffmpeg.exe")
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
        """Checks file info using ffmpeg."""
        if not self.ffmpeg_path:
            raise FileNotFoundError("FFmpeg not found. Please install FFmpeg.")
            
        cmd = [self.ffmpeg_path, "-i", input_path]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()
        return stderr

    def convert_to_m4r(self, input_path, output_path, start_time=None, end_time=None, progress_callback=None):
        """
        Converts input video/audio to M4R (AAC).
        Supports trimming if start_time and end_time are provided.
        """
        if not self.ffmpeg_path:
            raise FileNotFoundError("FFmpeg not found.")

        # Probe to see if it's already AAC (only matters if NOT trimming)
        info = self.probe_file(input_path)
        is_aac = "Audio: aac" in info

        cmd = [self.ffmpeg_path, "-y"]
        cmd.extend(["-i", input_path])

        if start_time and end_time:
            # Use trimming
            cmd.extend(["-ss", start_time, "-to", end_time])
            # When trimming, we re-encode to ensure cut accuracy
            cmd.extend(["-acodec", "aac", "-b:a", "256k"])
        elif is_aac:
            # Stream copy (Lossless)
            cmd.extend(["-acodec", "copy"])
        else:
            # Re-encode (High Quality)
            cmd.extend(["-acodec", "aac", "-b:a", "256k"])

        # -vn: disable video, -f ipod: standard for m4a/m4r container compat
        cmd.extend(["-vn", "-f", "ipod", output_path])

        # Run command
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        if progress_callback:
            for line in process.stdout:
                progress_callback(line)
        
        process.wait()
        
        if process.returncode != 0:
            raise RuntimeError(f"Conversion failed. Cmd: {' '.join(cmd)}")

        return True
