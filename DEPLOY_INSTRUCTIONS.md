# 如何將此工具部署為網頁版 (Streamlit Cloud)

原本的工具是基於 Python Tkinter 的桌面程式，無法直接在網頁上執行。
我已經為您新增了網頁版介面 (`streamlit_app.py`)，您可以透過以下步驟將其免費部署到 Streamlit Cloud，讓其成為網頁工具。

## 1. 準備工作 (已完成)
我已經在這份專案中新增了必要的檔案：
- `streamlit_app.py`: 網頁版的程式介面。
- `packages.txt`: 告訴雲端伺服器需要安裝 `ffmpeg` (處理音訊的核心工具)。
- `requirements.txt`: 新增了 `streamlit` 依賴。

## 2. 推送到 GitHub
這一步您需要做的是將此資料夾上傳到 GitHub 為一個新的 Repository。

1. 在 GitHub 上建立一個新的 Public Repository。
2. 將這些檔案 push 到該 Repository。

## 3. 部署到 Streamlit Cloud
1. 前往 [Streamlit Cloud](https://share.streamlit.io/) 並使用 GitHub 帳號登入。
2. 點擊 **"New app"**。
3. 選擇您剛剛建立的 GitHub Repository。
4. **Main file path** 選擇 `streamlit_app.py`。
5. 點擊 **"Deploy!"**。

系統會自動依據 `packages.txt` 安裝 FFmpeg，並依據 `requirements.txt` 安裝 Python 套件。
幾分鐘後，您的網頁版轉檔工具就會上線了！

## 本地測試
如果您想在本地電腦測試網頁版：
1. 開啟終端機 (Terminal)。
2. 安裝套件：`pip install -r requirements.txt`
3. 執行網頁版：`streamlit run streamlit_app.py`
