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
### 執行方式
- **選項 A：可攜式獨立免安裝版 (推薦)**
  - 進入 `dist/` 資料夾雙擊執行 `AppleRingtoneConverter.exe`，免裝 Python 環境即可使用。
  - 開發者亦可執行 `python build_portable.py` 隨時重新打包最新版本。
- **選項 B：原始碼執行**
  - 點擊 `run_app.bat` 或在終端機輸入 `python main.py`。

---

## 🛠️ 專案結構 (MECE Principle & SSOT)
- `core/`:
  - `converter.py`: 核心影音轉檔引擎 (FFmpeg / FFprobe 封裝)
  - `utils.py`: SSOT 時間解析與格式化唯一真相來源
- `main.py`: 桌面版 Tkinter 介面 (具備 OpenCV 影格即時同步與 winsound 試聽)
- `streamlit_app.py`: 網頁版 Streamlit 介面 (具備即時播放器與時間軸滑桿)
- `tests/`: 軟體自動確效套件 (`test_validation.py`)
- `docs/`: 系統架構規範 (`ARCHITECTURE.md`) 與使用者指南 (`USER_GUIDE.md`)
- `wiki/`: 專案知識庫與治理標準 (`HOME.md`)
- `build_portable.py`: 一鍵打包可攜式二進位執行檔腳本
- `run_app.bat`: Windows 快速啟動腳本
- `.github/`: GitHub Actions 自動化 CI/CD 確效工作流


---

## 🛠️ 技術棧
- **核心處理**: Python, FFmpeg
- **桌面介面**: Tkinter
- **網頁介面**: Streamlit
- **自動化**: GitHub Actions
