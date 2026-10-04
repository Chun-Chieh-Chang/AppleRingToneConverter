# Apple Ringtone Converter 專案知識庫 (Wiki)

歡迎來到 **Apple Ringtone Converter** 專案知識庫與治理標準中心。

---

## 📌 專案總覽
本專案提供跨平台、零依賴、高品質的 iPhone 鈴聲製作方案，涵蓋：
- **Web 雲端版**：以 Streamlit 架構部署，支援行動端與電腦端瀏覽器。
- **Desktop 桌面版**：以 Python Tkinter + OpenCV + Pillow 打造，支援視訊即時影格跳轉與 Windows 原生音訊試聽。
- **核心轉檔層**：基於 FFmpeg 高階封裝，支援直接無損複製 (Direct Stream Copy) 與 256k AAC 高品質重編碼。

---

## 🧭 治理標準與開發流程 (PDCA SOP)

所有開發與功能修訂均須嚴格遵守 **Plan -> Do -> Check -> Act** 閉環機制：
1. **Plan (計畫與診斷)**：
   - YAGNI 審查與第一性原理分析。
   - 識別潛在代碼脆弱點與 UI 違和處。
2. **Do (外科手術式精準實作)**：
   - 最小變更量，杜絕過度工程。
   - 貫徹 SSOT (單一事實來源) 與 MECE 原則。
3. **Check (強制確效檢核)**：
   - 執行 `tests/test_validation.py`，全數通過方可認定完成。
   - 檢查 Console 無任何紅色報錯。
4. **Act (審查、回滾預防與日誌)**：
   - 於 `DEV_LOG.md` 完整記載需求、RCA (根因分析) 與 CAPA (矯正預防措施)。
   - 獲得使用者明確許可後執行 Git Push。

---

## 🔗 相關文檔索引
- [系統架構與 SSOT 規範 (docs/ARCHITECTURE.md)](file:///d:/Self-developed_Apps/G3/AppleRingToneConverter/docs/ARCHITECTURE.md)
- [使用者操作指南 (docs/USER_GUIDE.md)](file:///d:/Self-developed_Apps/G3/AppleRingToneConverter/docs/USER_GUIDE.md)
- [開發維護日誌 (DEV_LOG.md)](file:///d:/Self-developed_Apps/G3/AppleRingToneConverter/DEV_LOG.md)
