"""
Automated Portable Executable Packager
Packages main.py into a standalone portable binary with zero external python dependencies.
"""
import os
import sys
import subprocess
import shutil

def build_portable():
    project_dir = os.path.dirname(os.path.abspath(__file__))
    dist_dir = os.path.join(project_dir, "dist")
    build_dir = os.path.join(project_dir, "build")

    print("[1/3] Cleaning previous build artifacts...")
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir, ignore_errors=True)
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir, ignore_errors=True)

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",
        "--name", "AppleRingtoneConverter",
        "--add-data", f"{os.path.join(project_dir, 'core')};core",
        "--collect-submodules", "cv2",
        "--collect-submodules", "PIL",
        os.path.join(project_dir, "main.py")
    ]

    print("[2/3] Executing PyInstaller build...")
    print(" ".join(cmd))
    res = subprocess.run(cmd, cwd=project_dir)
    if res.returncode != 0:
        raise RuntimeError("PyInstaller packaging failed!")

    exe_path = os.path.join(dist_dir, "AppleRingtoneConverter.exe")
    if os.path.exists(exe_path):
        size_mb = os.path.getsize(exe_path) / (1024 * 1024)
        print(f"[3/3] Success! Standalone portable binary created:")
        print(f"       -> {exe_path} ({size_mb:.2f} MB)")
        return exe_path
    else:
        raise FileNotFoundError(f"Expected binary not found at {exe_path}")

if __name__ == "__main__":
    build_portable()
