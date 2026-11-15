import logging
import os
import tempfile
from pathlib import Path

import streamlit as st

from core.converter import AudioConverter
from core.utils import format_seconds, parse_seconds
from locked_timeline import select_locked_start

logger = logging.getLogger(__name__)
LOCKED_DURATION = 30
AUDIO_FORMATS = {".mp3": "audio/mpeg", ".wav": "audio/wav", ".flac": "audio/flac", ".m4a": "audio/mp4"}


def format_trim_time(seconds):
    whole, fraction = f"{seconds:.2f}".split(".")
    time = format_seconds(int(whole))
    return time if fraction == "00" else f"{time}.{fraction}"


def apply_mobile_styles():
    st.markdown("""
    <style>
    @media (max-width: 768px) {
        [data-testid="stMain"] button,
        [data-testid="stCheckbox"] label,
        [data-testid="stSelectbox"] [data-baseweb="select"] > div {
            min-height: 44px;
        }
        [data-testid="stFileUploader"] button {
            min-width: 44px;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    st.set_page_config(
        page_title="Apple Ringtone Converter",
        page_icon="🎵",
        layout="centered"
    )
    apply_mobile_styles()

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
        ext = os.path.splitext(uploaded_file.name)[1].lower()
        file_bytes = uploaded_file.getvalue()
        if st.session_state.get("current_file_id") != uploaded_file.file_id:
            st.session_state.current_file_id = uploaded_file.file_id
            # Clear previous preview clip
            st.session_state.pop("preview_audio_bytes", None)

            st.session_state.media_info = None
            try:
                with tempfile.TemporaryDirectory() as tmpdir:
                    source_path = Path(tmpdir) / f"input{ext}"
                    source_path.write_bytes(file_bytes)
                    info = converter.get_media_info(str(source_path))
                st.session_state.media_info = info
                st.session_state.start_seconds = 0
                st.session_state.end_seconds = min(LOCKED_DURATION, info["duration"])
            except Exception:
                logger.exception("Failed to inspect uploaded media")

        info = st.session_state.media_info
        if not info or info["duration"] <= 0:
            st.error("無法讀取檔案長度，請重新選擇可播放的影音檔案。")
            return
        if not info["has_audio"]:
            st.error("這個檔案沒有音軌，請重新選擇含聲音的影片或音訊檔。")
            return
        total_duration = info["duration"]

        # Preview Section
        st.markdown("### 👁️ 即時視訊/音訊預覽 (Live Media Preview)")
        with st.container():
            if info.get("has_video"):
                # Direct video playback for browser supported formats
                if ext in ['.mp4', '.webm', '.mov']:
                    st.video(file_bytes)
                else:
                    st.info("提示：該視訊格式瀏覽器無法直接播放畫面，已提供音訊串流預覽。")
                    st.audio(file_bytes)
            else:
                st.audio(file_bytes, format=AUDIO_FORMATS.get(ext, "audio/mpeg"))

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
        end_time_str = format_trim_time(min(LOCKED_DURATION, total_duration))

        if enable_trim:
            st.markdown("#### ⏱️ 起訖時間軸調節")
            fixed_30s = st.checkbox("🔒 鎖定 30 秒鈴聲長度 (推薦 iPhone 最佳規格)", value=True, key="fixed_30s_check")

            # Range Slider for intuitive visual adjustment
            current_s = st.session_state.start_seconds
            current_e = st.session_state.end_seconds

            has_locked_timeline = fixed_30s and total_duration > LOCKED_DURATION
            if fixed_30s:
                selected_start = 0
                selected_end = min(total_duration, LOCKED_DURATION)
                if has_locked_timeline:
                    length = LOCKED_DURATION * 100
                    start = select_locked_start(
                        duration=round(total_duration * 100),
                        length=length,
                        start=round(current_s * 100),
                        key=f"locked_start_{uploaded_file.file_id}",
                    )
                    selected_start = start / 100
                    selected_end = (start + length) / 100
                elif total_duration < LOCKED_DURATION:
                    st.info("素材不足 30 秒，將保留完整長度。取消勾選鎖定可自訂剪輯。")
                else:
                    st.caption("目前可選起點為 0 秒，將使用前 30 秒。")
            else:
                selected_start, selected_end = st.slider(
                    "自訂起訖區間（拖曳左右滑塊）",
                    min_value=0.0,
                    max_value=float(total_duration),
                    value=(min(float(current_s), total_duration), min(float(current_e), total_duration)),
                    step=0.01,
                    key=f"custom_range_{uploaded_file.file_id}",
                    format="%.2f 秒",
                )

            refresh_preview = False
            if (selected_start, selected_end) != (current_s, current_e):
                previous_preview = st.session_state.pop("preview_audio_bytes", None)
                refresh_preview = has_locked_timeline and previous_preview is not None
            st.session_state.start_seconds = selected_start
            st.session_state.end_seconds = selected_end

            start_time_str = format_trim_time(selected_start)
            end_time_str = format_trim_time(selected_end)
            clip_length = selected_end - selected_start
            if start_time_str == end_time_str:
                st.warning("請將終點拖到起點之後，再試聽或轉檔。")
                return

            if not has_locked_timeline:
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown(f"**起點:** `{start_time_str}`")
                with c2:
                    st.markdown(f"**終點:** `{end_time_str}`")
                with c3:
                    st.markdown(f"**鈴聲總長度:** `{clip_length:.2f} 秒`")

            # Instant Auditory Preview Button
            st.markdown("#### 🎧 直觀聽覺試聽")
            preview_requested = st.button("▶️ 立即試聽選定鈴聲片段", type="secondary", width="stretch")
            if preview_requested or refresh_preview:
                with st.spinner("正在極速擷取試聽片段..."):
                    st.session_state.pop("preview_audio_bytes", None)
                    try:
                        with tempfile.TemporaryDirectory() as tmpdir:
                            source_path = Path(tmpdir) / f"input{ext}"
                            source_path.write_bytes(file_bytes)
                            preview_path = Path(tmpdir) / "preview.mp3"
                            converter.extract_preview_audio(
                                input_path=str(source_path),
                                start_time=start_time_str,
                                end_time=end_time_str,
                                output_path=str(preview_path),
                            )
                            st.session_state.preview_audio_bytes = preview_path.read_bytes()
                    except Exception:
                        logger.exception("Failed to generate preview")
                        st.error("無法產生試聽片段，請調整剪輯區間或重新選擇檔案。")

            if "preview_audio_bytes" in st.session_state:
                st.info(f"試聽片段 {start_time_str} ➜ {end_time_str}")
                st.audio(st.session_state.preview_audio_bytes, format="audio/mpeg")

        st.divider()

        # Final Action Button
        if st.button("🚀 開始轉檔並下載鈴聲", type="primary", width="stretch"):
            process_conversion(
                uploaded_file=uploaded_file,
                output_ext=output_ext,
                enable_trim=enable_trim,
                start_time=start_time_str,
                end_time=end_time_str,
            )

def process_conversion(uploaded_file, output_ext, enable_trim, start_time, end_time):
    converter = AudioConverter()
    if not converter.ffmpeg_path:
        st.error("伺服器目前無法執行轉檔，請稍後再試。")
        return

    with st.spinner("正在高規格編碼轉檔中..."):
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                ext = os.path.splitext(uploaded_file.name)[1].lower()
                in_path = Path(tmpdir) / f"input{ext}"
                in_path.write_bytes(uploaded_file.getvalue())
                out_path = Path(tmpdir) / f"output{output_ext}"
                converter.convert_to_m4r(
                    input_path=str(in_path),
                    output_path=str(out_path),
                    start_time=start_time if enable_trim else None,
                    end_time=end_time if enable_trim else None
                )

                data_bytes = out_path.read_bytes()
            base_name = os.path.splitext(uploaded_file.name)[0]
            st.success("🎉 轉檔成功，可下載檔案。")
            st.download_button(
                label=f"⬇️ 下載 {base_name}{output_ext}",
                data=data_bytes,
                file_name=f"{base_name}{output_ext}",
                mime="audio/mp4",
                width="stretch",
                on_click="ignore",
            )
        except Exception:
            logger.exception("Failed to convert uploaded media")
            st.error("無法完成轉檔，請調整剪輯區間或重新選擇檔案。")

if __name__ == "__main__":
    main()
