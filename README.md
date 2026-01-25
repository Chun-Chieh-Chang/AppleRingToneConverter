# 🎵 Apple Audio Converter (Video to Ringtone)

這是一個簡單好用的音訊轉檔工具，專門設計用來將網路影片或音樂檔案轉換為 iPhone 專用的 **.m4r 鈴聲格式**。

## 🚀 線上直接使用 (Web Version)
無需安裝任何軟體，點擊下方連結即可直接在瀏覽器中開始轉檔：

### [👉 點此開啟線上轉檔工具](https://appleringtoneconverter-arrhimpx7nqwc36secdbcu.streamlit.app/)

---

## ✨ 功能特色
- **格式支援廣泛**：支援 MP4, MKV, AVI, MOV, MP3, FLAC, WAV 等多種常見影音格式。
- **智慧轉檔**：
  - 若來源音訊已經是 AAC 編碼，系統會執行**無損複製 (Direct Stream Copy)**，確保音質完全不流失且速度極快。
  - 若需重新編碼，則會自動轉換為 **256k 高音質 AAC**，確保鈴聲聽起來清晰悅耳。
- **完全免費**：基於開源技術構建。

## 💻 本地安裝 (Desktop Version)
如果您希望在自己的電腦上離線使用，此專案也包含 Python 桌面視窗版本。

### 安裝步驟
1. 複製此專案到本地：
   ```bash
   git clone https://github.com/Chun-Chieh-Chang/AppleRingToneConverter.git
   ```
2. 安裝必要套件：
   ```bash
   pip install -r requirements.txt
   ```
3. 確保您的電腦已安裝 **FFmpeg** 並設定好環境變數 (或是將 `ffmpeg.exe` 放入 `bin` 資料夾)。
4. 執行主程式：
   ```bash
   python main.py
   ```

## 🛠️ 技術對棧
- **核心處理**: Python, FFmpeg
- **桌面介面**: Tkinter (內建)
- **網頁介面**: Streamlit
