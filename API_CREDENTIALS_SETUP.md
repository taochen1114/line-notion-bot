# API 憑證申請完整指南

本指南將一步一步教您如何申請所有必要的 API 憑證來運行 Line Bot 串接 Notion API 專案。

## 📋 需要申請的憑證清單

- ✅ Line Bot 開發者帳號和頻道憑證
- ✅ Notion Integration Token 和資料庫 ID
- ✅ Google Cloud Platform 專案和服務帳號

---

## 🤖 第一部分：Line Bot 憑證申請

### 步驟 1：註冊 Line Developers 帳號

1. **前往 Line Developers Console**
   - 網址：https://developers.line.biz/
   - 點擊右上角「Log in」

2. **使用 Line 帳號登入**
   - 如果沒有 Line 帳號，請先下載 Line App 註冊
   - 使用您的 Line 帳號和密碼登入

3. **同意開發者條款**
   - 閱讀並同意 Line Developers 使用條款
   - 點擊「Agree」完成註冊

### 步驟 2：建立 Provider

1. **建立新的 Provider**
   - 登入後點擊「Create a new provider」
   - Provider 是管理您所有 Line 服務的容器

2. **填寫 Provider 資訊**
   - **Provider name**: 輸入您的公司或專案名稱（例如：「My Company」）
   - 點擊「Create」

### 步驟 3：建立 Messaging API Channel

1. **建立新頻道**
   - 在 Provider 頁面點擊「Create a Messaging API channel」

2. **填寫頻道基本資訊**
   - **Channel name**: 您的 Bot 名稱（例如：「Notion Knowledge Bot」）
   - **Channel description**: Bot 的功能描述（例如：「搜尋 Notion 知識庫的智慧助手」）
   - **Category**: 選擇「Education」或「Productivity」
   - **Subcategory**: 選擇適合的子分類
   - **Email address**: 您的聯絡信箱

3. **上傳 Bot 圖示（可選）**
   - 建議上傳 512x512 像素的 PNG 圖片
   - 這將成為您 Bot 的頭像

4. **完成建立**
   - 同意條款並點擊「Create」

### 步驟 4：取得 Line Bot 憑證

建立完成後，您需要取得兩個重要的憑證：

#### 4.1 取得 Channel Secret

1. **進入頻道設定**
   - 點擊剛建立的頻道名稱

2. **找到 Channel Secret**
   - 切換到「Basic settings」頁籤
   - 找到「Channel secret」欄位
   - 點擊「Show」查看密鑰
   - **複製並保存這個值** → 這就是 `LINE_CHANNEL_SECRET`

#### 4.2 取得 Channel Access Token

1. **切換到 Messaging API 頁籤**
   - 點擊「Messaging API」頁籤

2. **產生 Access Token**
   - 找到「Channel access token」區域
   - 點擊「Issue」按鈕產生 Token
   - **複製並保存這個值** → 這就是 `LINE_CHANNEL_ACCESS_TOKEN`

### 步驟 5：設定 Webhook（稍後完成）

1. **啟用 Webhook**
   - 在「Messaging API」頁籤中
   - 將「Use webhook」設為「Enabled」

2. **Webhook URL 設定**
   - 暫時留空，部署完成後再填入
   - 格式將是：`https://your-service-url/webhook`

---

## 📚 第二部分：Notion API 憑證申請

### 步驟 1：建立 Notion Integration

1. **前往 Notion Developers**
   - 網址：https://www.notion.so/my-integrations
   - 使用您的 Notion 帳號登入

2. **建立新的 Integration**
   - 點擊「+ New integration」

3. **填寫 Integration 資訊**
   - **Name**: 輸入整合名稱（例如：「Line Bot Integration」）
   - **Logo**: 可選擇上傳 Logo
   - **Associated workspace**: 選擇要整合的 Notion 工作區
   - **Type**: 選擇「Internal」（內部使用）

4. **設定權限**
   - **Content Capabilities**: 勾選「Read content」
   - **Comment Capabilities**: 可以不勾選
   - **User Capabilities**: 可以不勾選

5. **完成建立**
   - 點擊「Submit」

### 步驟 2：取得 Integration Token

1. **複製 Token**
   - 建立完成後，會顯示「Internal Integration Token」
   - 這個 Token 以 `secret_` 開頭
   - **複製並保存這個值** → 這就是 `NOTION_API_TOKEN`

### 步驟 3：準備 Notion 資料庫

#### 3.1 建立或選擇資料庫

1. **建立新資料庫（如果沒有）**
   - 在 Notion 中建立一個新頁面
   - 輸入 `/database` 選擇「Table - Full page」
   - 為資料庫命名（例如：「知識庫」）

2. **設定資料庫屬性**
   - **Name**: 標題欄位（預設存在）
   - **Tags**: 多選標籤欄位（可選）
   - **Content**: 文字內容欄位（可選）

#### 3.2 分享資料庫給 Integration

1. **開啟資料庫頁面**
   - 點擊您要查詢的 Notion 資料庫

2. **分享資料庫**
   - 點擊右上角的「Share」按鈕
   - 在「Invite」欄位中輸入您的 Integration 名稱
   - 選擇您剛建立的 Integration
   - 點擊「Invite」

3. **確認權限**
   - 選擇「Can read」權限（查詢用途）
   - 點擊「Invite」確認

### 步驟 4：取得資料庫 ID

1. **複製資料庫 URL**
   - 在瀏覽器中開啟您的 Notion 資料庫
   - 複製完整的 URL

2. **提取資料庫 ID**
   - URL 格式：`https://www.notion.so/workspace/DATABASE_ID?v=VIEW_ID`
   - 提取其中的 `DATABASE_ID`（32 個字元的字串）
   - 例如：`a1b2c3d4e5f6789012345678901234ab`
   - **保存這個值** → 這就是 `NOTION_DATABASE_ID`

---

## ☁️ 第三部分：Google Cloud Platform 憑證申請

### 步驟 1：建立 GCP 帳號

1. **前往 Google Cloud Console**
   - 網址：https://console.cloud.google.com/
   - 使用您的 Google 帳號登入

2. **啟用免費試用（如果是新用戶）**
   - Google Cloud 提供 $300 免費額度
   - 按照指示完成註冊

### 步驟 2：建立新專案

1. **建立專案**
   - 點擊頂部的專案選擇器
   - 點擊「NEW PROJECT」

2. **填寫專案資訊**
   - **Project name**: 輸入專案名稱（例如：「line-notion-bot」）
   - **Organization**: 選擇組織（如果適用）
   - **Location**: 選擇位置（如果適用）

3. **建立專案**
   - 點擊「CREATE」
   - 等待專案建立完成

4. **記錄專案 ID**
   - 專案建立後，記錄「Project ID」
   - **保存這個值** → 這就是 `GCP_PROJECT_ID`

### 步驟 3：啟用必要的 API

1. **前往 API Library**
   - 在左側選單中點擊「APIs & Services」>「Library」

2. **啟用以下 API**（逐一搜尋並啟用）：
   - **Cloud Run API**: 用於部署應用程式
   - **Cloud Build API**: 用於自動建置
   - **Secret Manager API**: 用於管理密鑰
   - **Cloud Logging API**: 用於日誌記錄

3. **啟用方式**
   - 搜尋 API 名稱
   - 點擊進入 API 頁面
   - 點擊「ENABLE」

### 步驟 4：建立服務帳號

1. **前往服務帳號頁面**
   - 點擊「IAM & Admin」>「Service Accounts」

2. **建立服務帳號**
   - 點擊「CREATE SERVICE ACCOUNT」

3. **填寫服務帳號資訊**
   - **Service account name**: `line-notion-bot-sa`
   - **Service account ID**: 會自動產生
   - **Description**: 輸入描述（例如：「Line Bot 服務帳號」）

4. **設定權限**
   - 點擊「CREATE AND CONTINUE」
   - 授予以下角色：
     - `Cloud Run Developer`
     - `Secret Manager Secret Accessor`
     - `Logging Writer`
     - `Storage Object Viewer`（如果需要）

5. **完成建立**
   - 點擊「CONTINUE」然後「DONE」

### 步驟 5：建立服務帳號金鑰

1. **進入服務帳號詳細頁面**
   - 在服務帳號列表中點擊剛建立的帳號

2. **建立金鑰**
   - 切換到「KEYS」頁籤
   - 點擊「ADD KEY」>「Create new key」

3. **選擇金鑰格式**
   - 選擇「JSON」格式
   - 點擊「CREATE」

4. **下載金鑰檔案**
   - 金鑰檔案會自動下載
   - 將檔案重新命名為 `service-account-key.json`
   - 將檔案放在專案根目錄
   - **記錄檔案路徑** → 這就是 `GOOGLE_APPLICATION_CREDENTIALS`

---

## 🔧 第四部分：設定環境變數

### 步驟 1：建立 .env 檔案

1. **複製範例檔案**
   ```bash
   cp .env.example .env
   ```

2. **編輯 .env 檔案**
   使用文字編輯器開啟 `.env` 檔案

### 步驟 2：填入所有憑證

將您剛才取得的所有憑證填入 `.env` 檔案：

```env
# Line Bot 設定
LINE_CHANNEL_ACCESS_TOKEN=你的Line頻道存取權杖
LINE_CHANNEL_SECRET=你的Line頻道密鑰

# Notion API 設定
NOTION_API_TOKEN=secret_你的Notion整合權杖
NOTION_DATABASE_ID=你的Notion資料庫ID

# GCP 設定
GCP_PROJECT_ID=你的GCP專案ID
GOOGLE_APPLICATION_CREDENTIALS=./service-account-key.json

# 應用程式設定
PORT=8080
ENVIRONMENT=development
DEBUG=true
```

### 步驟 3：驗證設定

1. **檢查檔案格式**
   - 確保沒有多餘的空格
   - 確保沒有引號（除非值本身包含空格）
   - 確保每行格式為 `KEY=value`

2. **測試連線**
   ```bash
   # 啟動開發環境測試
   ./scripts/dev.sh
   ```

---

## ✅ 憑證申請檢查清單

完成所有步驟後，請確認您已取得：

### Line Bot 憑證
- [ ] `LINE_CHANNEL_ACCESS_TOKEN` - 以 `Bearer` 開頭的長字串
- [ ] `LINE_CHANNEL_SECRET` - 32 字元的字串

### Notion API 憑證
- [ ] `NOTION_API_TOKEN` - 以 `secret_` 開頭的字串
- [ ] `NOTION_DATABASE_ID` - 32 字元的資料庫 ID
- [ ] Notion 資料庫已分享給 Integration

### GCP 憑證
- [ ] `GCP_PROJECT_ID` - 您的 GCP 專案 ID
- [ ] `service-account-key.json` - 服務帳號金鑰檔案
- [ ] 必要的 API 已啟用

### 環境設定
- [ ] `.env` 檔案已建立並填入所有憑證
- [ ] 檔案格式正確，無語法錯誤

---

## 🚨 安全性提醒

1. **保護您的憑證**
   - 絕對不要將 `.env` 檔案提交到版本控制系統
   - 不要在公開場合分享這些憑證
   - 定期更新 Access Token

2. **檔案權限**
   ```bash
   # 設定 .env 檔案權限（僅自己可讀寫）
   chmod 600 .env
   chmod 600 service-account-key.json
   ```

3. **備份憑證**
   - 將憑證安全地備份到密碼管理器
   - 記錄憑證的建立日期和用途

---

## 🎯 下一步

完成所有憑證申請後，您可以：

1. **測試本地開發環境**
   ```bash
   ./scripts/dev.sh
   ```

2. **部署到 GCP**
   ```bash
   ./scripts/deploy.sh
   ```

3. **設定 Line Webhook URL**
   - 部署完成後，將 Cloud Run URL 設定到 Line Bot

如果遇到任何問題，請參考 [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md) 獲得詳細的解決方案。

---

**🎉 恭喜！您已經完成了所有 API 憑證的申請！**