import streamlit as st
import tempfile
import os
import shutil
import subprocess
from converter import AudioConverter

def main():
    st.set_page_config(page_title="Apple Audio Converter", page_icon="🎵")
    
    st.title("🎵 Apple Audio Converter (Web)")
    st.write("Convert video/audio files to iPhone Ringtone format (.m4r) with optional trimming.")

    # File uploader
    uploaded_file = st.file_uploader("Select a file (MP4, MKV, MP3, etc.)", type=['mp4', 'mkv', 'avi', 'mov', 'mp3', 'wav', 'flac', 'm4a'])

    if uploaded_file is not None:
        st.info(f"File loaded: {uploaded_file.name}")
        
        # Render the Cut & Convert UI directly
        render_cut_and_convert_ui(uploaded_file, is_path=False)

def render_cut_and_convert_ui(file_input, is_path):
    """
    Renders the UI for cutting and converting a file.
    """
    st.markdown("### ✂️ Edit & Convert")
    
    # 1. Trim Options
    enable_trim = st.checkbox("Enable Trimming / Cutting", value=False)
    
    start_time = "00:00:00"
    end_time = "00:00:30"
    
    if enable_trim:
        col1, col2 = st.columns(2)
        with col1:
            start_time = st.text_input("Start Time", value="00:00:00", help="Format: HH:MM:SS")
        with col2:
            end_time = st.text_input("End Time", value="00:00:30", help="Format: HH:MM:SS")
            
        st.caption("Enter the exact time range you want to keep. (Format: HH:MM:SS)")

    if st.button("Convert to M4R", type="primary"):
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
            # Should not happen in this simplified version, but keeping for robustness if reused locally
            input_path = file_input
            original_name = os.path.splitext(os.path.basename(file_input))[0]

        # B. Define Output Path
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
                
                # ffmpeg -i input -ss start -to end
                cmd = [
                    converter.ffmpeg_path, "-y",
                    "-i", current_source,
                    "-ss", start_time,
                    "-to", end_time,
                    "-vn", # No video
                    "-acodec", "aac", "-b:a", "256k", # Re-encode to ensure clean cut and format
                    trimmed_path
                ]
                
                subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                current_source = trimmed_path
                progress_bar.progress(50)
            
            # Step 2: Final Conversion/Container change to M4R
            status_text.text("Finalizing M4R...")
            
            if enable_trim:
                 # Just copy to m4r since we already encoded to aac above
                 shutil.copy2(current_source, final_output_path)
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

if __name__ == "__main__":
    main()
