# Development Log - Apple Ringtone Converter

## [2026-03-21] Fixed 30s Clipping Feature

### 任務描述
設定起點或終點的時間，固定擷取 30 秒。

### 失敗嘗試 & 錯誤原因
- **同步邏輯初版**：最初未考慮到 `st.session_state` 在 `on_change` 回調中的行為。若僅在回調中修改變數而未更新 `st.session_state` 中的鍵值，頁面重新渲染時會被舊值覆蓋，導致輸入不穩定。
- **解析邏輯**：最初僅支援 `HH:MM:SS` 格式，若使用者輸入 `90` 或 `01:30` 會引發錯誤。

### 最終矯正措施 & 優化
- **Session State 管理**：引入 `st.session_state` 來持久化起點與終點時間，並透過 `on_change` 回調與 `st.text_input` 的 `key` 機制實現雙向同步。
- **強健的解析邏輯**：新增 `parse_seconds` 函數，支援 `SS`, `MM:SS`, `HH:MM:SS` 多種輸入格式，並自動補齊。
- **Snap-to-30s**：在「固定 30 秒」切換開關加入回調，確保開啟時立即基於起點同步終點。

### 驗證結果
- 通過單元測試腳本 `tmp_test_time.py` 驗證起點/終點同步邏輯，並確認負數時間防禦（自動設為 00:00:00）。

## [2026-10-04] 即時預覽與播放畫面 (Real-time Visual & Auditory Preview)

### 任務描述
新增即時可預覽與播放的畫面，同時支援 Streamlit 網頁版 與 Tkinter 桌面版。若是影片則呈現畫面影像預覽/播放，若是音訊則呈現音訊播放/波形體驗，並提供視覺化時間滑桿與 30 秒片段試聽，方便使用者直觀決定起訖剪輯位置。

### 根因與架構考量 (RCA & Architecture)
- 原先使用者僅能以字串輸入時間 (`HH:MM:SS`)，無法直觀感受畫面關鍵影格或音樂副歌時間點。
- 平台解碼差異：瀏覽器原生無法解碼 MKV/AVI 等格式，需在伺服器端做好相容性處理；桌面版 Tkinter 原生缺乏音訊視訊播放控制項，需藉助 OpenCV 與 Windows 原生/輕量音訊處理模組達成零外部複雜依賴的即時畫面渲染與片段試聽。

### 矯正與預防措施 (CAPA)
- `core/converter.py`：新增 `get_media_info` 解析媒體總長度與串流類型 (Video/Audio)；新增 `extract_preview_audio` 支援快速生成輕量試聽檔。
- `streamlit_app.py`：提供原生媒體播放器 (Video/Audio)、整合直觀時間範圍滑桿與「🎧 試聽選定鈴聲片段」功能。
- `main.py`：使用 OpenCV + Pillow 即時抓取對應秒數的視訊畫面影格呈現在介面中，並透過時間軸拉桿連動更新影格；加入音訊片段試聽播放控制。

### 驗證結果
- 建立軟體確效測試套件 `tests/test_validation.py`，涵蓋音訊媒體解析、視訊媒體解析、30秒區間試聽生成、M4R鈴聲編碼輸出、邊界時間格式轉換等，3 項確效測試 100% 通過。
- 整合 GitHub Actions 雲端 CI/CD 自動化確效流程。


