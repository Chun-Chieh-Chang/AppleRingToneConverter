import streamlit as st
import tempfile
import os
import shutil
from converter import AudioConverter

def main():
    st.set_page_config(page_title="Apple Audio Converter", page_icon="🎵")
    
    st.title("🎵 Apple Audio Converter (Web)")
    st.write("Convert video/audio files to iPhone Ringtone format (.m4r) with high quality.")

    # File uploader
    uploaded_file = st.file_uploader("Select a file (MP4, MKV, MP3, etc.)", type=['mp4', 'mkv', 'avi', 'mov', 'mp3', 'wav', 'flac', 'm4a'])

    if uploaded_file is not None:
        st.info(f"File loaded: {uploaded_file.name}")
        
        if st.button("Convert to M4R"):
            converter = AudioConverter()
            
            # Check for FFmpeg
            if not converter.ffmpeg_path:
                st.error("FFmpeg not found on the server. Please ensure it is installed.")
                return

            # Create a temporary directory to avoid conflicts
            with tempfile.TemporaryDirectory() as temp_dir:
                # Save uploaded file
                # specific extension helps ffmpeg probe sometimes, though often not needed
                ext = os.path.splitext(uploaded_file.name)[1]
                if not ext:
                    ext = ".tmp"
                    
                input_path = os.path.join(temp_dir, f"input{ext}")
                output_path = os.path.join(temp_dir, "output.m4r")
                
                with open(input_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                # Convert
                status_text = st.empty()
                status_text.text("Converting...")
                
                progress_bar = st.progress(0)
                
                # Mock progress since we don't have percentage from the current converter easily
                # You could enhance converter.py to yield progress percentage
                progress_bar.progress(50)
                
                try:
                    converter.convert_to_m4r(input_path, output_path)
                    progress_bar.progress(100)
                    status_text.success("Conversion Complete!")
                    
                    # Read result for download
                    with open(output_path, "rb") as f:
                        btn = st.download_button(
                            label="Download .m4r Ringtone",
                            data=f,
                            file_name=os.path.splitext(uploaded_file.name)[0] + ".m4r",
                            mime="audio/mp4"
                        )
                except Exception as e:
                    st.error(f"Conversion Error: {e}")

if __name__ == "__main__":
    main()
