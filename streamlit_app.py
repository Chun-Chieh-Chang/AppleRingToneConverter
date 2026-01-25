import streamlit as st
import tempfile
import os
import shutil
import yt_dlp
import subprocess
from converter import AudioConverter

# Initialize session state for downloaded file path
if 'downloaded_file_path' not in st.session_state:
    st.session_state.downloaded_file_path = None
if 'downloaded_file_name' not in st.session_state:
    st.session_state.downloaded_file_name = None

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
            render_cut_and_convert_ui(uploaded_file, is_path=False, key_prefix="upload")

    # --- Tab 2: YouTube URL ---
    with tab2:
        yt_url = st.text_input("Paste YouTube URL here:", placeholder="https://www.youtube.com/watch?v=...")
        
        if yt_url:
            if st.button("Download from YouTube"):
                with st.spinner("Downloading..."):
                    try:
                        path, name = download_yt(yt_url)
                        st.session_state.downloaded_file_path = path
                        st.session_state.downloaded_file_name = name
                        st.success(f"Downloaded: {name}")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

        # If we have a file in session state (from YouTube), show the UI
        # Note: Session state persists across re-runs, so this UI stays visible
        if st.session_state.downloaded_file_path and os.path.exists(st.session_state.downloaded_file_path):
            st.write("---")
            st.write(f"**Target File:** {st.session_state.downloaded_file_name}")
            
            # Allow clearing to start over
            if st.button("Clear / Download Another"):
                st.session_state.downloaded_file_path = None
                st.session_state.downloaded_file_name = None
                st.rerun()
                
            render_cut_and_convert_ui(st.session_state.downloaded_file_path, is_path=True, key_prefix="yt")

def render_cut_and_convert_ui(file_input, is_path, key_prefix):
    """
    Renders the UI for cutting and converting a file.
    """
    st.markdown("### ✂️ Cut & Convert")
    
    # 1. Trim Options
    enable_trim = st.checkbox("Enable Trimming", key=f"{key_prefix}_trim")
    
    start_time = "00:00:00"
    end_time = "00:00:30"
    
    if enable_trim:
        col1, col2 = st.columns(2)
        with col1:
            start_time = st.text_input("Start Time (HH:MM:SS)", value="00:00:00", key=f"{key_prefix}_start")
        with col2:
            end_time = st.text_input("End Time (HH:MM:SS)", value="00:00:30", key=f"{key_prefix}_end")
            
        st.caption("Format: HH:MM:SS (e.g. 00:01:15 for 1 min 15 sec)")

    if st.button("Convert to M4R", key=f"{key_prefix}_btn"):
        process_conversion(file_input, is_path, enable_trim, start_time, end_time)

def process_conversion(file_input, is_path, enable_trim, start_time, end_time):
    converter = AudioConverter()
    
    if not converter.ffmpeg_path:
        st.error("FFmpeg not found on the server.")
        return

    # Use a specific temp folder context for this operation
    with tempfile.TemporaryDirectory() as temp_dir:
        input_path = ""
        original_name = "ringtone"

        # A. Prepare Input File on Disk
        if not is_path:
            # Uploaded file object
            ext = os.path.splitext(file_input.name)[1]
            if not ext: ext = ".tmp"
            original_name = os.path.splitext(file_input.name)[0]
            
            input_path = os.path.join(temp_dir, f"input{ext}")
            with open(input_path, "wb") as f:
                f.write(file_input.getbuffer())
        else:
            # Path string (YouTube download)
            # We copy it to temp_dir to be safe and clean
            original_path = file_input
            original_name = st.session_state.downloaded_file_name
            ext = os.path.splitext(original_path)[1]
            input_path = os.path.join(temp_dir, f"input{ext}")
            shutil.copy2(original_path, input_path)

        # B. Prepare Intermediate Path (if trimming) and Final Output Path
        # We need a robust pipeline: Input -> [Trim] -> [Convert] -> Output
        
        # Define output
        final_output_path = os.path.join(temp_dir, "output.m4r")
        
        status_text = st.empty()
        status_text.text("Processing...")
        progress_bar = st.progress(0)
        
        try:
            current_source = input_path
            
            # Step 1: Trimming (if enabled)
            if enable_trim:
                status_text.text("Trimming audio...")
                trimmed_path = os.path.join(temp_dir, "trimmed_temp.m4a") # intermediate
                
                # ffmpeg -i input -ss start -to end -c copy (if possible) or re-encode
                # For safety and accuracy in cutting, we'll re-encode or at least let ffmpeg handle it
                # -c copy might be inaccurate on keyframes for video, but for audio it is usually fine-ish.
                # Let's simple re-encode to be safe and ensure format consistency
                
                cmd = [
                    converter.ffmpeg_path, "-y",
                    "-i", current_source,
                    "-ss", start_time,
                    "-to", end_time,
                    "-vn", # No video
                    "-acodec", "aac", "-b:a", "256k", # High quality AAC
                    trimmed_path
                ]
                
                subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                current_source = trimmed_path
                progress_bar.progress(50)
            
            # Step 2: Final Conversion/Container change to M4R
            status_text.text("Finalizing M4R...")
            
            # If we trimmed, current_source is already AAC M4A. We just need to rename/container it.
            # If we didn't trim, we use the original converter logic
            
            if enable_trim:
                 # Just copy to m4r since we already encoded to aac above
                 shutil.copy2(current_source, final_output_path)
                 # Ensure it's treated as ipod (m4r) just in case, but copy is usually enough if codec is aac
            else:
                # Use standard full file conversion
                converter.convert_to_m4r(current_source, final_output_path)
            
            progress_bar.progress(100)
            status_text.success("Done!")
            
            # C. Offer Download
            suffix = "_cut" if enable_trim else ""
            dl_filename = f"{original_name}{suffix}.m4r"
            
            with open(final_output_path, "rb") as f:
                st.download_button(
                    label=f"⬇️ Download {dl_filename}",
                    data=f,
                    file_name=dl_filename,
                    mime="audio/mp4"
                )
                
        except Exception as e:
            st.error(f"Processing Error: {e}")

def download_yt(url):
    # We need a persistent directory for session-based downloads (simplified for demo)
    # In a real deployed app, using tempfile per request is better, but here we want to keep it 
    # for the next interaction (Cut UI). 
    # Streamlit Cloud re-runs the script on interaction. 
    # We will use /tmp or a dedicated folder that persists *during the session*.
    # CAUTION: Streamlit share filesystems are ephemeral but usually persist during session slightly.
    
    dl_dir = "downloads"
    if not os.path.exists(dl_dir):
        os.makedirs(dl_dir)
        
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(dl_dir, '%(title)s.%(ext)s'),
        'noplaylist': True,
        # Tweak options to avoid 403 Forbidden on cloud servers
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web'],
            }
        },
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info) # Full path
        title = info.get('title', 'video')
        
    return filename, title

if __name__ == "__main__":
    main()
