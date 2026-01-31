# 🎵 Apple Audio Converter (Video to Ringtone)

這是一個簡單好用的音訊轉檔工具，專門設計用來將網路影片或音樂檔案轉換為 iPhone 專用的 **.m4r 鈴聲格式**。

## ✨ 功能特色
- **格式支援廣泛**：支援 MP4, MKV, AVI, MOV, MP3, FLAC, WAV 等多種常見影音格式。
- **智慧轉檔**：
  - 支援**無損複製 (Direct Stream Copy)**：若來源音訊已是 AAC，則不重新編碼。
  - 支援**高品質重編碼**：自動轉換為 256k AAC。
- **精準剪輯**：內建時間剪輯功能，可自由設定鈴聲片段。
- **多端支援**：包含**桌面視窗版**與**網頁版**。

---

## 🚀 線上使用 (Web Version)
點擊下方連結即可直接在瀏覽器中開始轉檔：
### [👉 點此開啟線上轉檔工具](https://appleringtoneconverter-arrhimpx7nqwc36secdbcu.streamlit.app/)

> **部署說明**：本專案已配置 `packages.txt` 與 `requirements.txt`，可直接於 Streamlit Cloud 部署。部署時請將主程式路徑設為 `web_app.py`。

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
   - 或執行 `python desktop_app.py`

---

## 🛠️ 專案結構 (MECE Principle)
- `core/`: 核心轉檔邏輯 (FFmpeg 封裝)
- `desktop_app.py`: 桌面版 Tkinter 介面
- `web_app.py`: 網頁版 Streamlit 介面
- `run_app.bat`: Windows 快速啟動腳本
- `.github/`: GitHub Actions 自動化工作流

---

## 🛠️ 技術棧
- **核心處理**: Python, FFmpeg
- **桌面介面**: Tkinter
- **網頁介面**: Streamlit
- **自動化**: GitHub Actions
