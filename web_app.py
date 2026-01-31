import streamlit as st
import tempfile
import os
from core.converter import AudioConverter

def main():
    st.set_page_config(page_title="Apple Ringtone Converter", page_icon="🎵", layout="centered")
    
    st.title("🎵 Apple Ringtone Converter")
    st.markdown("""
    Upload your video or audio files and convert them to **iPhone Ringtone (.m4r)** format.
    *Direct lossy-to-lossless conversion or high-quality re-encoding.*
    """)

    uploaded_file = st.file_uploader("Choose a file", type=['mp4', 'mkv', 'avi', 'mov', 'mp3', 'wav', 'flac', 'm4a'])

    if uploaded_file:
        st.divider()
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Options")
            output_ext = st.selectbox("Output Format", [".m4r", ".m4a"], format_func=lambda x: "iPhone Ringtone (.m4r)" if x==".m4r" else "High Quality Audio (.m4a)")
        
        with col2:
            st.subheader("Trimming")
            enable_trim = st.checkbox("Enable Trimming")
            if enable_trim:
                start_time = st.text_input("Start Time", "00:00:00", help="HH:MM:SS")
                end_time = st.text_input("End Time", "00:00:30", help="HH:MM:SS")
            else:
                start_time, end_time = None, None

        if st.button("Convert Now", type="primary", use_container_width=True):
            process_conversion(uploaded_file, output_ext, enable_trim, start_time, end_time)

def process_conversion(uploaded_file, output_ext, enable_trim, start_time, end_time):
    converter = AudioConverter()
    if not converter.ffmpeg_path:
        st.error("FFmpeg not found on server.")
        return

    with st.spinner("Processing..."):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Save upload
            ext = os.path.splitext(uploaded_file.name)[1]
            in_path = os.path.join(tmpdir, f"input{ext}")
            with open(in_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            out_path = os.path.join(tmpdir, f"output{output_ext}")
            
            try:
                converter.convert_to_m4r(
                    input_path=in_path,
                    output_path=out_path,
                    start_time=start_time if enable_trim else None,
                    end_time=end_time if enable_trim else None
                )
                
                # Download button
                with open(out_path, "rb") as f:
                    st.success("Conversion successful!")
                    st.download_button(
                        label=f"⬇️ Download {os.path.splitext(uploaded_file.name)[0]}{output_ext}",
                        data=f,
                        file_name=f"{os.path.splitext(uploaded_file.name)[0]}{output_ext}",
                        mime="audio/mp4"
                    )
            except Exception as e:
                st.error(f"Error: {e}")

if __name__ == "__main__":
    main()
