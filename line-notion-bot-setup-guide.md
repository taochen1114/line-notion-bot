# Line Bot 串接 Notion API 完整設置指南

## 第一步：設置開發環境和專案結構

### 1.1 建立專案目錄結構

首先建立專案的基本目錄結構：

```bash
mkdir line-notion-bot
cd line-notion-bot

# 建立目錄結構
mkdir -p app/{models,services,utils}
mkdir tests
touch app/__init__.py
touch app/models/__init__.py
touch app/services/__init__.py
touch app/utils/__init__.py
touch tests/__init__.py
```

### 1.2 建立虛擬環境

```bash
# 建立虛擬環境
python3 -m venv venv

# 啟動虛擬環境
# macOS/Linux:
source venv/bin/activate
# Windows:
# venv\Scripts\activate
```

### 1.3 安裝必要套件

建立 `requirements.txt` 檔案並安裝套件。

## 第二步：申請 Line Bot 開發者帳號和設定頻道

### 2.1 註冊 Line Developers 帳號

1. 前往 [Line Developers Console](https://developers.line.biz/)
2. 使用您的 Line 帳號登入
3. 同意開發者條款

### 2.2 建立 Provider

1. 點擊「Create a new provider」
2. 輸入 Provider 名稱（例如：「My Company」）
3. 點擊「Create」

### 2.3 建立 Messaging API Channel

1. 在 Provider 頁面點擊「Create a Messaging API channel」
2. 填寫以下資訊：
   - **Channel name**: 您的 Bot 名稱
   - **Channel description**: Bot 的描述
   - **Category**: 選擇適合的分類
   - **Subcategory**: 選擇子分類
   - **Email address**: 您的聯絡信箱
3. 同意條款並點擊「Create」

### 2.4 取得重要資訊

建立完成後，記錄以下重要資訊：

1. **Channel Secret**:
   - 在「Basic settings」頁籤中找到
   - 點擊「Show」查看並複製

2. **Channel Access Token**:
   - 在「Messaging API」頁籤中
   - 點擊「Issue」產生 Token
   - 複製並妥善保存

### 2.5 設定 Webhook URL（稍後設定）

在「Messaging API」頁籤中：
- 將「Use webhook」設為 Enabled
- Webhook URL 將在部署後設定

## 第三步：建立 Notion Integration 和取得 API Token

### 3.1 建立 Notion Integration

1. 前往 [Notion Developers](https://www.notion.so/my-integrations)
2. 點擊「+ New integration」
3. 填寫以下資訊：
   - **Name**: 您的整合名稱（例如：「Line Bot Integration」）
   - **Logo**: 可選擇上傳 Logo
   - **Associated workspace**: 選擇要整合的工作區
4. 點擊「Submit」

### 3.2 取得 Integration Token

1. 建立完成後，複製「Internal Integration Token」
2. 這個 Token 以 `secret_` 開頭
3. 妥善保存此 Token

### 3.3 分享資料庫給 Integration

1. 開啟您要查詢的 Notion 資料庫頁面
2. 點擊右上角的「Share」
3. 在「Invite」欄位中輸入您的 Integration 名稱
4. 選擇您的 Integration 並點擊「Invite」
5. 確認權限設定（通常選擇「Can read」即可）

### 3.4 取得資料庫 ID

1. 開啟您的 Notion 資料庫
2. 複製頁面 URL
3. URL 格式：`https://www.notion.so/workspace/DATABASE_ID?v=VIEW_ID`
4. 提取其中的 `DATABASE_ID`（32 個字元的字串）

## 第四步：設定 GCP 專案和服務帳號

### 4.1 建立 GCP 專案

1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 點擊專案選擇器，然後點擊「NEW PROJECT」
3. 輸入專案名稱（例如：「line-notion-bot」）
4. 選擇組織（如果適用）
5. 點擊「CREATE」

### 4.2 啟用必要的 API

在 GCP Console 中啟用以下 API：

1. **Cloud Run API**
2. **Cloud Build API**
3. **Secret Manager API**
4. **Cloud Logging API**

啟用方式：
1. 前往「APIs & Services」>「Library」
2. 搜尋並啟用上述 API

### 4.3 建立服務帳號

1. 前往「IAM & Admin」>「Service Accounts」
2. 點擊「CREATE SERVICE ACCOUNT」
3. 填寫服務帳號資訊：
   - **Service account name**: `line-notion-bot-sa`
   - **Description**: 服務帳號描述
4. 點擊「CREATE AND CONTINUE」
5. 授予以下角色：
   - `Cloud Run Developer`
   - `Secret Manager Secret Accessor`
   - `Logging Writer`
6. 點擊「CONTINUE」然後「DONE」

### 4.4 建立服務帳號金鑰

1. 在服務帳號列表中找到剛建立的帳號
2. 點擊帳號名稱進入詳細頁面
3. 切換到「KEYS」頁籤
4. 點擊「ADD KEY」>「Create new key」
5. 選擇「JSON」格式
6. 點擊「CREATE」
7. 下載並妥善保存 JSON 金鑰檔案

### 4.5 設定本地環境

```bash
# 安裝 Google Cloud SDK（如果尚未安裝）
# macOS:
# brew install google-cloud-sdk

# 設定認證
export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/service-account-key.json"

# 登入 GCP
gcloud auth login

# 設定預設專案
gcloud config set project YOUR_PROJECT_ID
```

## 第五步：建立環境變數檔案

建立 `.env` 檔案來存放環境變數：

```bash
# Line Bot 設定
LINE_CHANNEL_ACCESS_TOKEN=your_line_channel_access_token
LINE_CHANNEL_SECRET=your_line_channel_secret

# Notion API 設定
NOTION_API_TOKEN=your_notion_integration_token
NOTION_DATABASE_ID=your_notion_database_id

# GCP 設定
GCP_PROJECT_ID=your_gcp_project_id
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/service-account-key.json

# 應用程式設定
PORT=8080
ENVIRONMENT=development
```

**重要提醒**：
- 將 `.env` 加入 `.gitignore` 檔案中
- 不要將敏感資訊提交到版本控制系統

## 第六步：安全性檢查清單

在開始開發前，請確認：

- [ ] Line Channel Secret 和 Access Token 已正確取得
- [ ] Notion Integration Token 已正確取得
- [ ] Notion 資料庫已分享給 Integration
- [ ] GCP 專案已建立並啟用必要 API
- [ ] 服務帳號已建立並下載金鑰
- [ ] 環境變數檔案已建立並設定正確
- [ ] 敏感資訊已加入 `.gitignore`

完成以上設定後，就可以開始進行程式開發了！

## 下一步

接下來我們將：
1. 建立專案的基本程式結構
2. 實作 Notion API 整合模組
3. 開發 Line Bot Webhook 處理器
4. 實作查詢功能和回應格式化
5. 部署到 GCP Cloud Run

每個步驟都會有詳細的程式碼範例和說明。