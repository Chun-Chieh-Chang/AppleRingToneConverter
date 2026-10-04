import streamlit as st
import tempfile
import os
import re
from core.converter import AudioConverter
from core.utils import format_seconds, parse_seconds

def apply_custom_theme():
    st.markdown("""
    <style>
    /* Premium Glassmorphic Design Palette */
    .stApp {
        background: radial-gradient(circle at 50% 0%, #f1f5f9 0%, #f8fafc 100%);
    }
    .preview-card {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(226, 232, 240, 0.8);
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.05);
        margin-bottom: 20px;
    }
    .time-badge {
        display: inline-block;
        background: #eff6ff;
        color: #2563eb;
        font-family: monospace;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 8px;
        border: 1px solid #bfdbfe;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    st.set_page_config(
        page_title="Apple Ringtone Converter",
        page_icon="🎵",
        layout="centered"
    )
    apply_custom_theme()

    st.title("🎵 Apple Ringtone Converter")
    st.markdown("""
    將影音檔案轉換為 **iPhone 鈴聲 (.m4r)**。
    即時**視訊畫面/音訊預覽**與**直觀片段試聽**，輕鬆定位副歌起訖。
    """)

    converter = AudioConverter()
    if not converter.ffmpeg_path:
        st.error("⚠️ 伺服器未檢測到 FFmpeg，請確保 FFmpeg 已安裝。")
        return

    uploaded_file = st.file_uploader(
        "選擇來源檔案 (影片或音樂)",
        type=['mp4', 'mkv', 'avi', 'mov', 'webm', 'mp3', 'wav', 'flac', 'm4a']
    )

    if uploaded_file:
        # Cache file to session temp
        ext = os.path.splitext(uploaded_file.name)[1].lower()
        if "current_file_name" not in st.session_state or st.session_state.current_file_name != uploaded_file.name:
            st.session_state.current_file_name = uploaded_file.name
            st.session_state.file_bytes = uploaded_file.getvalue()
            # Clear previous preview clip
            st.session_state.pop("preview_audio_bytes", None)

            # Analyze file
            with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp_f:
                tmp_f.write(st.session_state.file_bytes)
                tmp_path = tmp_f.name

            try:
                info = converter.get_media_info(tmp_path)
                st.session_state.media_info = info
                st.session_state.temp_source_path = tmp_path
                total_dur = max(1.0, info.get("duration", 30.0))
                st.session_state.total_duration = total_dur
                st.session_state.start_seconds = 0
                st.session_state.end_seconds = min(30, int(total_dur))
            except Exception as e:
                st.error(f"檔案解析失敗: {e}")
                st.session_state.total_duration = 30.0
                st.session_state.media_info = {"duration": 30.0, "has_video": False, "has_audio": True}

        info = st.session_state.get("media_info", {"duration": 30.0, "has_video": False, "has_audio": True})
        total_duration = st.session_state.get("total_duration", 30.0)

        # Preview Section
        st.markdown("### 👁️ 即時視訊/音訊預覽 (Live Media Preview)")
        with st.container():
            if info.get("has_video"):
                # Direct video playback for browser supported formats
                if ext in ['.mp4', '.webm', '.mov']:
                    st.video(st.session_state.file_bytes)
                else:
                    st.info("提示：該視訊格式瀏覽器無法直接播放畫面，已提供音訊串流預覽。")
                    st.audio(st.session_state.file_bytes)
            else:
                st.audio(st.session_state.file_bytes)

        st.divider()

        # Options & Trimming Section
        col_opt1, col_opt2 = st.columns(2)
        with col_opt1:
            st.subheader("⚙️ 輸出格式")
            output_ext = st.selectbox(
                "選擇格式",
                [".m4r", ".m4a"],
                format_func=lambda x: "iPhone 鈴聲 (.m4r)" if x==".m4r" else "高品質音訊 (.m4a)"
            )

        with col_opt2:
            st.subheader("✂️ 剪輯設置")
            enable_trim = st.checkbox("啟用時間剪輯", value=True)

        start_time_str = "00:00:00"
        end_time_str = format_seconds(min(30, int(total_duration)))

        if enable_trim:
            st.markdown("#### ⏱️ 起訖時間軸調節")
            fixed_30s = st.checkbox("🔒 鎖定 30 秒鈴聲長度 (推薦 iPhone 最佳規格)", value=True, key="fixed_30s_check")

            # Range Slider for intuitive visual adjustment
            current_s = st.session_state.get("start_seconds", 0)
            current_e = st.session_state.get("end_seconds", min(30, int(total_duration)))

            if fixed_30s:
                # Single start slider that automatically shifts end by 30s
                max_start = max(0, int(total_duration - 30)) if total_duration > 30 else 0
                selected_start = st.slider(
                    "拖拉設定鈴聲起點 (長度固定 30 秒):",
                    min_value=0,
                    max_value=max_start,
                    value=min(current_s, max_start),
                    format="%d 秒",
                    help="拖曳滑桿即時決定鈴聲開始時間"
                )
                selected_end = min(int(total_duration), selected_start + 30)
                st.session_state.start_seconds = selected_start
                st.session_state.end_seconds = selected_end
            else:
                # Dual range slider
                slider_range = st.slider(
                    "自訂起訖區間 (拖拉左右雙滑塊):",
                    min_value=0,
                    max_value=max(1, int(total_duration)),
                    value=(min(current_s, int(total_duration)), min(current_e, int(total_duration))),
                    format="%d 秒"
                )
                st.session_state.start_seconds = slider_range[0]
                st.session_state.end_seconds = slider_range[1]

            start_time_str = format_seconds(st.session_state.start_seconds)
            end_time_str = format_seconds(st.session_state.end_seconds)
            clip_length = st.session_state.end_seconds - st.session_state.start_seconds

            # Visual Badges
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f"**起點:** `{start_time_str}`")
            with c2:
                st.markdown(f"**終點:** `{end_time_str}`")
            with c3:
                st.markdown(f"**鈴聲總長度:** `{clip_length} 秒`")

            # Instant Auditory Preview Button
            st.markdown("#### 🎧 直觀聽覺試聽")
            if st.button("▶️ 立即試聽選定鈴聲片段 (Preview Selection)", type="secondary", use_container_width=True):
                with st.spinner("正在極速擷取試聽片段..."):
                    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as prev_f:
                        prev_output = prev_f.name
                    try:
                        converter.extract_preview_audio(
                            input_path=st.session_state.temp_source_path,
                            start_time=start_time_str,
                            end_time=end_time_str,
                            output_path=prev_output
                        )
                        with open(prev_output, "rb") as pf:
                            st.session_state.preview_audio_bytes = pf.read()
                        try:
                            os.remove(prev_output)
                        except:
                            pass
                    except Exception as pe:
                        st.error(f"試聽生成失敗: {pe}")

            if "preview_audio_bytes" in st.session_state:
                st.info(f"正在播放選定片段: {start_time_str} ➜ {end_time_str}")
                st.audio(st.session_state.preview_audio_bytes, format="audio/mp3")

        st.divider()

        # Final Action Button
        if st.button("🚀 開始轉檔並下載鈴聲", type="primary", use_container_width=True):
            process_conversion(
                uploaded_file=uploaded_file,
                output_ext=output_ext,
                enable_trim=enable_trim,
                start_time=start_time_str,
                end_time=end_time_str,
                source_path=st.session_state.get("temp_source_path")
            )

def process_conversion(uploaded_file, output_ext, enable_trim, start_time, end_time, source_path=None):
    converter = AudioConverter()
    if not converter.ffmpeg_path:
        st.error("FFmpeg not found on server.")
        return

    with st.spinner("正在高規格編碼轉檔中..."):
        with tempfile.TemporaryDirectory() as tmpdir:
            ext = os.path.splitext(uploaded_file.name)[1]
            if source_path and os.path.exists(source_path):
                in_path = source_path
            else:
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
                base_name = os.path.splitext(uploaded_file.name)[0]
                with open(out_path, "rb") as f:
                    data_bytes = f.read()
                    st.success("🎉 轉檔成功！點擊下方按鈕儲存鈴聲至手機或電腦：")
                    st.download_button(
                        label=f"⬇️ 下載 {base_name}{output_ext}",
                        data=data_bytes,
                        file_name=f"{base_name}{output_ext}",
                        mime="audio/mp4" if output_ext == ".m4r" else "audio/x-m4a",
                        use_container_width=True
                    )
            except Exception as e:
                st.error(f"轉檔過程發生錯誤: {e}")

if __name__ == "__main__":
    main()
