import os
import sys
import tempfile
import subprocess
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.converter import AudioConverter
from core.utils import format_seconds, parse_seconds
from streamlit_app import format_seconds as st_format_seconds, parse_seconds as st_parse_seconds
from main import format_seconds as main_format_seconds, parse_seconds as main_parse_seconds

def test_time_conversion_consistency():
    # Test valid formats via SSOT
    assert format_seconds(0) == "00:00:00"
    assert format_seconds(30) == "00:00:30"
    assert format_seconds(3665) == "01:01:05"
    assert format_seconds(-10) == "00:00:00"
    assert format_seconds(None) == "00:00:00"

    assert parse_seconds("00:00:30") == 30
    assert parse_seconds("01:30") == 90
    assert parse_seconds("45") == 45
    assert parse_seconds("invalid") == 0
    assert parse_seconds("") == 0
    assert parse_seconds(None) == 0

    # Ensure SSOT identity across modules
    assert format_seconds is st_format_seconds
    assert format_seconds is main_format_seconds
    assert parse_seconds is st_parse_seconds
    assert parse_seconds is main_parse_seconds

def test_audio_media_validation():
    converter = AudioConverter()
    assert converter.ffmpeg_path is not None

    with tempfile.TemporaryDirectory() as td:
        wav_path = os.path.join(td, "sample_audio.wav")
        # Generate 15-second test audio sine tone
        subprocess.run([
            converter.ffmpeg_path, "-y",
            "-f", "lavfi",
            "-i", "sine=frequency=440:duration=15",
            wav_path
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

        # 1. Media Info Probe
        info = converter.get_media_info(wav_path)
        assert info["has_audio"] is True
        assert info["has_video"] is False
        assert abs(info["duration"] - 15.0) < 0.5

        # 2. Preview Clip Generation
        prev_path = os.path.join(td, "preview.mp3")
        converter.extract_preview_audio(wav_path, "00:00:02", "00:00:07", prev_path)
        assert os.path.exists(prev_path)
        prev_info = converter.get_media_info(prev_path)
        assert abs(prev_info["duration"] - 5.0) < 0.5

        # 3. Full M4R Conversion
        m4r_path = os.path.join(td, "sample.m4r")
        converter.convert_to_m4r(wav_path, m4r_path, start_time="00:00:00", end_time="00:00:10")
        assert os.path.exists(m4r_path)
        m4r_info = converter.get_media_info(m4r_path)
        assert m4r_info["has_audio"] is True
        assert abs(m4r_info["duration"] - 10.0) < 0.5

def test_video_media_validation():
    converter = AudioConverter()
    with tempfile.TemporaryDirectory() as td:
        mp4_path = os.path.join(td, "sample_video.mp4")
        # Generate 6-second video with audio
        subprocess.run([
            converter.ffmpeg_path, "-y",
            "-f", "lavfi", "-i", "testsrc=duration=6:size=320x240:rate=25",
            "-f", "lavfi", "-i", "sine=frequency=800:duration=6",
            "-c:v", "libx264", "-c:a", "aac",
            mp4_path
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

        info = converter.get_media_info(mp4_path)
        assert info["has_video"] is True
        assert info["has_audio"] is True
        assert abs(info["duration"] - 6.0) < 0.5

        # Verify preview extraction from video
        prev_wav = os.path.join(td, "prev.wav")
        converter.extract_preview_audio(mp4_path, "00:00:01", "00:00:04", prev_wav)
        assert os.path.exists(prev_wav)
        prev_info = converter.get_media_info(prev_wav)
        assert abs(prev_info["duration"] - 3.0) < 0.5
