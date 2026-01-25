import streamlit as st
import tempfile
import os
import shutil
import yt_dlp
from converter import AudioConverter

def main():
    st.set_page_config(page_title="Apple Audio Converter", page_icon="🎵")
    
    st.title("🎵 Apple Audio Converter (Web)")
    st.write("Convert video/audio from **File Upload** or **YouTube** to iPhone Ringtone (.m4r).")

    # Tabs for different input methods
    tab1, tab2 = st.tabs(["📂 File Upload", "📺 YouTube URL"])

    # --- Tab 1: File Upload ---
    with tab1:
        uploaded_file = st.file_uploader("Select a file (MP4, MKV, MP3, etc.)", type=['mp4', 'mkv', 'avi', 'mov', 'mp3', 'wav', 'flac', 'm4a'])

        if uploaded_file is not None:
            st.info(f"File loaded: {uploaded_file.name}")
            
            if st.button("Convert Uploaded File"):
                process_file(uploaded_file, is_path=False)

    # --- Tab 2: YouTube URL ---
    with tab2:
        yt_url = st.text_input("Paste YouTube URL here:", placeholder="https://www.youtube.com/watch?v=...")
        
        if yt_url:
            if st.button("Download & Convert"):
                with st.spinner("Downloading from YouTube..."):
                    try:
                        download_and_process_yt(yt_url)
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

def process_file(file_input, is_path=False):
    """
    Handles the conversion process.
    file_input: either a file-like object (if is_path=False) or a file path string (if is_path=True)
    """
    converter = AudioConverter()
    
    if not converter.ffmpeg_path:
        st.error("FFmpeg not found on the server.")
        return

    with tempfile.TemporaryDirectory() as temp_dir:
        input_path = ""
        original_name = "ringtone"

        # 1. Prepare Input File
        if not is_path:
            # It's an uploaded file object
            ext = os.path.splitext(file_input.name)[1]
            if not ext: ext = ".tmp"
            original_name = os.path.splitext(file_input.name)[0]
            
            input_path = os.path.join(temp_dir, f"input{ext}")
            with open(input_path, "wb") as f:
                f.write(file_input.getbuffer())
        else:
            # It's a path from YT download
            # file_input is the path
            input_path = file_input
            original_name = os.path.splitext(os.path.basename(file_input))[0]

        output_path = os.path.join(temp_dir, "output.m4r")

        # 2. Convert
        progress_text = st.empty()
        progress_text.text("Converting format...")
        progress_bar = st.progress(0)
        
        try:
            # Since we don't have real-time progress callbacks easy in Web, we simulate or just generic wait
            progress_bar.progress(30)
            converter.convert_to_m4r(input_path, output_path)
            progress_bar.progress(100)
            
            st.success("Conversion Complete!")
            
            # 3. Offer Download
            with open(output_path, "rb") as f:
                st.download_button(
                    label=f"Download {original_name}.m4r",
                    data=f,
                    file_name=f"{original_name}.m4r",
                    mime="audio/mp4"
                )
        except Exception as e:
            st.error(f"Conversion Error: {e}")

def download_and_process_yt(url):
    """Downloads video/audio from YouTube and triggers conversion"""
    
    # Use a temp dir for download
    with tempfile.TemporaryDirectory() as dl_dir:
        # Options: download best audio/video mixed, preferably mp4 to satisfy user request, 
        # but logically we just need audio for ringtone. 
        # But user asked 'download into mp4', so we try 'best[ext=mp4]'.
        # However, for reliability and speed, retrieving 'bestaudio' is safer for ringtone tools.
        # Let's try to get a file.
        
        ydl_opts = {
            'format': 'bestaudio/best', # Get best audio mainly, fallback to best
            'outtmpl': os.path.join(dl_dir, '%(title)s.%(ext)s'),
            'noplaylist': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        
        st.write(f"Downloaded: {os.path.basename(filename)}")
        
        # Now convert this file
        process_file(filename, is_path=True)

if __name__ == "__main__":
    main()
