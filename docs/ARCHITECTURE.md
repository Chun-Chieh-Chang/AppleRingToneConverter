# 系統架構設計規範 (System Architecture & SSOT)

本文檔定義 **Apple Ringtone Converter** 的核心軟體架構、設計原則與模組邊界。

---

## 🏛️ 1. 設計原則 (Design Principles)

- **SSOT (Single Source of Truth，單一事實來源)**：
  - 所有通用業務邏輯（如時間格式化 `format_seconds`、字串解析 `parse_seconds`）統一集中於 `core/utils.py`。
  - 桌面端 (`main.py`)、網頁端 (`streamlit_app.py`) 與測試套件 (`tests/test_validation.py`) 統一自 `core.utils` 匯入，消除重複實作與邏輯漂移。
- **MECE (Mutually Exclusive, Collectively Exhaustive，相互獨立、完全窮盡)**：
  - 核心轉換引擎與 UI 表現層完全分離。
  - 桌面端與網頁端均依賴底層 `AudioConverter` 與 `utils`，保證跨平台運作之一致性。
- **防禦性降級 (Defensive Graceful Degradation)**：
  - 桌面端對 OpenCV 與 winsound 進行條件式匯入；若環境缺乏視訊解碼庫，系統自動切換至純音訊預覽，絕不崩潰。

---

## 🧩 2. 模組邊界與架構分層

```mermaid
graph TD
    subgraph UI_Layer [表現層 (Presentation Layer)]
        Web[streamlit_app.py<br/>網頁版介面]
        Desktop[main.py<br/>Tkinter 桌面版介面]
    end

    subgraph Core_Layer [核心業務層 (Core Logic)]
        Utils[core/utils.py<br/>SSOT 時間解析與轉換]
        Converter[core/converter.py<br/>AudioConverter 轉檔引擎]
    end

    subgraph Engine_Layer [底層處理層 (Engines & Hardware)]
        FFmpeg[FFmpeg / FFprobe]
        CV2[OpenCV / PIL 影格渲染]
        AudioAPI[HTML5 Audio / winsound]
    end

    subgraph Quality_Layer [品質確效層 (Quality Assurance)]
        Tests[tests/test_validation.py<br/>軟體確效套件]
        CI[GitHub Actions CI/CD]
    end

    Web --> Utils
    Web --> Converter
    Desktop --> Utils
    Desktop --> Converter
    Converter --> FFmpeg
    Desktop --> CV2
    Desktop --> AudioAPI
    Web --> AudioAPI
    Tests --> Utils
    Tests --> Converter
    CI --> Tests
```

---

## 🔄 3. 即時預覽與試聽管線 (Preview Pipeline)

1. **媒體探測 (`get_media_info`)**：
   - 透過 FFprobe/FFmpeg 提取總時長 (`duration`) 與流類型 (`has_video`, `has_audio`)。
2. **視訊畫面影格預覽**：
   - **桌面端**：使用 OpenCV 讀取目標秒數影格，經 Pillow 保持長寬比等比縮放，實時投射至 Tkinter 畫布。拖曳滑桿時毫秒級跳轉。
   - **網頁端**：使用 Streamlit `st.video` 原生視訊解碼播放。
3. **無損片段試聽 (`extract_preview_audio`)**：
   - 依據使用者指定的起訖時間，以極速參數裁切 30 秒輕量試聽檔（WAV/MP3）。
   - 桌面端調用 Windows 異步 API `winsound.PlaySound`，不阻塞主 UI 執行緒。

---

## 🛡️ 4. 軟體確效體系 (Validation Architecture)

- **自動確效腳本**：`tests/test_validation.py`
  - 時間解析跨模組物件一致性驗證。
  - 正弦波音訊探測、試聽截取與 M4R 鈴聲規格編碼確效。
  - 測試視訊串流解析與預覽截取確效。
- **持續整合 (CI/CD)**：
  - 於 `.github/workflows/main.yml` 中執行 Ubuntu 環境依賴安裝、靜態語法檢查與完整 pytest 確效。
