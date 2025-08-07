# Line Bot 串接 Notion API

一個使用 Python FastAPI 開發的 Line Bot，可以搜尋 Notion 知識庫並回傳結果給用戶。

## 功能特色

- 🤖 **Line Bot 整合**: 透過 Line 平台與用戶互動
- 📚 **Notion 知識庫搜尋**: 搜尋 Notion 資料庫中的頁面和內容
- 🔍 **智慧搜尋**: 支援標題、內容和標籤搜尋
- ☁️ **雲端部署**: 部署到 Google Cloud Run
- 📊 **日誌監控**: 整合 Google Cloud Logging
- 🔒 **安全性**: 使用 Secret Manager 管理敏感資訊

## 系統架構

```
Line 用戶 → Line Platform → Webhook → GCP Cloud Run → FastAPI → Notion API
```

## 技術棧

- **後端框架**: FastAPI (Python 3.9+)
- **Line Bot SDK**: line-bot-sdk
- **Notion API**: notion-client
- **部署平台**: Google Cloud Run
- **日誌**: Google Cloud Logging
- **密鑰管理**: Google Secret Manager

## 快速開始

### 1. 環境準備

```bash
# 複製專案
git clone <repository-url>
cd line-notion-bot

# 如果遇到安裝問題，請先執行修復腳本
./scripts/fix-install.sh

# 或手動建立環境
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# 安裝依賴
pip install -r requirements.txt
```

**⚠️ Python 3.12 相容性提醒**：
如果您使用 Python 3.12，可能會遇到套件編譯問題。解決方案：
- **推薦**: 執行 `./scripts/fix-install.sh` 自動修復（會自動選擇相容版本）
- **手動**: 使用 `pip install -r requirements-py312.txt`
- **備選**: 使用 Python 3.11: `pyenv install 3.11.7 && pyenv local 3.11.7`

### 2. 申請 API 憑證

在設定環境變數之前，您需要申請各種 API 憑證：

**📖 完整申請指南**: [`API_CREDENTIALS_SETUP.md`](API_CREDENTIALS_SETUP.md)

這個指南將一步一步教您如何申請：
- 🤖 Line Bot 開發者帳號和頻道憑證
- 📚 Notion Integration Token 和資料庫 ID
- ☁️ Google Cloud Platform 專案和服務帳號

### 3. 環境變數設定

完成憑證申請後，複製 `.env.example` 為 `.env` 並填入相關資訊：

```bash
cp .env.example .env
```

編輯 `.env` 檔案，填入您申請到的憑證：

```env
# Line Bot 設定
LINE_CHANNEL_ACCESS_TOKEN=your_line_channel_access_token
LINE_CHANNEL_SECRET=your_line_channel_secret

# Notion API 設定
NOTION_API_TOKEN=secret_your_notion_integration_token
NOTION_DATABASE_ID=your_notion_database_id

# GCP 設定
GCP_PROJECT_ID=your_gcp_project_id
GOOGLE_APPLICATION_CREDENTIALS=./service-account-key.json

# 應用程式設定
ENVIRONMENT=development
DEBUG=true
```

### 4. 本地開發

```bash
# 使用開發腳本啟動（推薦）
./scripts/dev.sh

# 或手動啟動開發伺服器
python -m app.main

# 或使用 uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

### 5. 測試 API

```bash
# 健康檢查
curl http://localhost:8080/health

# 根路徑
curl http://localhost:8080/
```

## 部署到 Google Cloud Platform

### 1. 準備 GCP 環境

```bash
# 登入 GCP
gcloud auth login

# 設定專案
gcloud config set project YOUR_PROJECT_ID

# 啟用必要的 API
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable secretmanager.googleapis.com
```

### 2. 設定 Secret Manager

```bash
# 建立 secrets
echo -n "your_line_channel_access_token" | gcloud secrets create line-channel-access-token --data-file=-
echo -n "your_line_channel_secret" | gcloud secrets create line-channel-secret --data-file=-
echo -n "your_notion_api_token" | gcloud secrets create notion-api-token --data-file=-
echo -n "your_notion_database_id" | gcloud secrets create notion-database-id --data-file=-
```

### 3. 部署應用程式

```bash
# 使用 Cloud Build 部署
gcloud builds submit --config cloudbuild.yaml

# 或手動部署
gcloud run deploy line-notion-bot \
  --source . \
  --region asia-east1 \
  --allow-unauthenticated
```

### 4. 設定 Line Webhook URL

部署完成後，將 Cloud Run 的 URL 設定為 Line Bot 的 Webhook URL：

```
https://your-service-url/webhook
```

## API 端點

- `GET /` - 根路徑，返回服務狀態
- `GET /health` - 健康檢查端點
- `POST /webhook` - Line Bot Webhook 端點

## 使用方式

1. 將 Line Bot 加為好友
2. 直接輸入關鍵字進行搜尋
3. 輸入「幫助」查看使用說明

### 搜尋範例

```
用戶: Python
Bot: 🔍 搜尋「Python」找到 3 個結果：

1. 📄 Python 基礎教學
   Python 是一種高階程式語言...
   🏷️ #程式語言 #教學
   🔗 https://notion.so/...

2. 📄 Python Web 開發
   使用 FastAPI 建立 Web API...
   🏷️ #Python #Web開發
   🔗 https://notion.so/...
```

## 開發指南

### 專案結構

```
line-notion-bot/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 應用程式入口
│   ├── config.py            # 配置管理
│   ├── models/
│   │   ├── __init__.py
│   │   └── line_models.py   # Line 訊息模型
│   ├── services/
│   │   ├── __init__.py
│   │   ├── line_service.py  # Line Bot 服務
│   │   └── notion_service.py # Notion API 服務
│   └── utils/
│       ├── __init__.py
│       ├── formatter.py     # 回應格式化
│       └── logger.py        # 日誌工具
├── tests/                   # 測試檔案
├── requirements.txt         # Python 依賴
├── Dockerfile              # Docker 配置
├── cloudbuild.yaml         # GCP 建置配置
└── README.md
```

### 新增功能

1. 在 `app/services/` 中新增服務模組
2. 在 `app/models/` 中定義資料模型
3. 在 `app/main.py` 中新增 API 端點
4. 撰寫對應的測試

### 測試

```bash
# 執行測試
pytest

# 執行測試並產生覆蓋率報告
pytest --cov=app tests/
```

## 故障排除

### 常見安裝問題

1. **Python 3.12 相容性問題**
   - 執行 `./scripts/fix-install.sh` 自動修復
   - 或使用 Python 3.11: `pyenv install 3.11.7 && pyenv local 3.11.7`

2. **套件編譯錯誤 (aiohttp)**
   - 使用預編譯套件: `pip install --only-binary=all aiohttp`
   - 安裝 Xcode Command Line Tools: `xcode-select --install`

3. **虛擬環境問題**
   - 重建環境: `rm -rf venv && python3 -m venv venv`
   - 升級 pip: `pip install --upgrade pip`

### 常見運行問題

1. **模組導入錯誤**
   - 確保在專案根目錄執行: `python -m app.main`
   - 設定 PYTHONPATH: `export PYTHONPATH=$PWD:$PYTHONPATH`

2. **環境變數未載入**
   - 檢查 `.env` 檔案格式，避免多餘空格和引號
   - 確保變數名稱正確，無拼寫錯誤

3. **端口被佔用**
   - 查找佔用程序: `lsof -i :8080`
   - 終止程序: `kill -9 <PID>`
   - 使用不同端口: `export PORT=8081`

### API 整合問題

1. **Notion API 連線失敗**
   - 檢查 `NOTION_API_TOKEN` 是否正確
   - 確認 Integration 已分享給目標資料庫

2. **Line Bot 無回應**
   - 檢查 `LINE_CHANNEL_ACCESS_TOKEN` 和 `LINE_CHANNEL_SECRET`
   - 確認 Webhook URL 設定正確

3. **部署失敗**
   - 檢查 GCP 專案權限
   - 確認所有必要的 API 已啟用

**📖 詳細故障排除指南**: 請參考 [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md) 獲得更完整的解決方案。

### 日誌查看

```bash
# 查看 Cloud Run 日誌
gcloud logs read --service=line-notion-bot --limit=50

# 即時查看日誌
gcloud logs tail --service=line-notion-bot
```

## 貢獻指南

1. Fork 此專案
2. 建立功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交變更 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 開啟 Pull Request

## 授權條款

此專案採用 MIT 授權條款 - 詳見 [LICENSE](LICENSE) 檔案

## 聯絡資訊

如有問題或建議，請開啟 Issue 或聯繫專案維護者。