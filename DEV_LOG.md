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
