# 🎵 Apple Audio Converter (Video to Ringtone)

這是一個簡單好用的音訊轉檔工具，專門設計用來將網路影片或音樂檔案轉換為 iPhone 專用的 **.m4r 鈴聲格式**。

## ✨ 功能特色
- **格式支援廣泛**：支援 MP4, MKV, AVI, MOV, WEBM, MP3, FLAC, WAV 等多種常見影音格式。
- **直觀視覺與聽覺即時預覽**：
  - 視訊畫面即時預覽（拖動時間軸滑桿時即時同步影格畫面）。
  - 音訊播放器與即時 30 秒片段試聽（免轉檔直接先聽副歌）。
- **智慧轉檔**：
  - 支援**無損複製 (Direct Stream Copy)**：若來源音訊已是 AAC，則不重新編碼。
  - 支援**高品質重編碼**：自動轉換為 256k AAC。
- **精準時間軸剪輯**：直觀滑桿調節起訖點，支援 30 秒一鍵鎖定規格。
- **多端支援**：包含**桌面視窗版 (Tkinter + OpenCV)** 與**網頁版 (Streamlit)**。
- **自動化軟體確效**：內建 pytest 自動確效測試套件與 GitHub Actions CI/CD 防線。


---

## 🚀 線上使用 (Web Version)
點擊下方連結即可直接在瀏覽器中開始轉檔：
### [👉 點此開啟線上轉檔工具](https://appleringtoneconverter-arrhimpx7nqwc36secdbcu.streamlit.app/)

> **部署說明**：本專案已配置 `packages.txt` 與 `requirements.txt`，可直接於 Streamlit Cloud 部署。預設主程式路徑為 `streamlit_app.py`。

---

## 💻 本地安裝 (Desktop Version)
### 安裝步驟
1. 複製此專案：
   ```bash
   git clone https://github.com/Chun-Chieh-Chang/AppleRingToneConverter.git
   ```
2. 安裝套件：
   ```bash
   pip install -r requirements.txt
   ```
3. 確保電腦已安裝 **FFmpeg** (或將 `ffmpeg.exe` 放入專案的 `bin` 資料夾)。
4. 執行工具：
   - 點擊 `run_app.bat` 
   - 或執行 `python main.py`

---

## 🛠️ 專案結構 (MECE Principle)
- `core/`: 核心轉檔邏輯 (FFmpeg 封裝)
- `main.py`: 桌面版 Tkinter 介面
- `streamlit_app.py`: 網頁版 Streamlit 介面
- `run_app.bat`: Windows 快速啟動腳本
- `.github/`: GitHub Actions 自動化工作流

---

## 🛠️ 技術棧
- **核心處理**: Python, FFmpeg
- **桌面介面**: Tkinter
- **網頁介面**: Streamlit
- **自動化**: GitHub Actions
