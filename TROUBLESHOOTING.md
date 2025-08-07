# 故障排除指南

## 常見安裝問題

### 1. Python 3.12 相容性問題

**問題**: `aiohttp` 套件編譯失敗，出現 `ob_digit` 錯誤

**解決方案**:
```bash
# 方法 1: 使用 Python 3.12 相容版本（推薦）
pip install -r requirements-py312.txt
# 這會安裝更新版本的 line-bot-sdk 和相容的 aiohttp

# 方法 2: 使用修復腳本（自動檢測版本）
./scripts/fix-install.sh

# 方法 3: 降級到 Python 3.11
pyenv install 3.11.7
pyenv local 3.11.7

# 方法 4: 使用 conda 環境
conda create -n line-bot python=3.11
conda activate line-bot
```

### 2. 依賴衝突問題

**問題**: `line-bot-sdk` 與 `aiohttp` 版本衝突

**解決方案**:
```bash
# 移除衝突的 aiohttp 版本要求
# line-bot-sdk 3.5.0 需要 aiohttp==3.8.5
pip install -r requirements.txt
```

### 3. Pydantic 版本問題

**問題**: `BaseSettings` 導入錯誤

**解決方案**:
已在 `requirements.txt` 中加入 `pydantic-settings==2.1.0`

### 3. 虛擬環境問題

**問題**: 套件安裝衝突

**解決方案**:
```bash
# 清理並重建虛擬環境
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. macOS 編譯問題

**問題**: C 編譯器錯誤

**解決方案**:
```bash
# 安裝 Xcode Command Line Tools
xcode-select --install

# 設定編譯器環境變數
export CC=clang
export CXX=clang++
```

### 5. 記憶體不足問題

**問題**: 編譯時記憶體不足

**解決方案**:
```bash
# 增加 swap 空間或使用預編譯套件
pip install --no-cache-dir -r requirements.txt
```

## 開發環境問題

### 1. 環境變數未載入

**問題**: `.env` 檔案中的變數無法讀取

**解決方案**:
```bash
# 檢查 .env 檔案格式
cat .env

# 確保沒有多餘的空格或引號
LINE_CHANNEL_ACCESS_TOKEN=your_token_here
# 不要: LINE_CHANNEL_ACCESS_TOKEN = "your_token_here"
```

### 2. 模組導入錯誤

**問題**: `ModuleNotFoundError`

**解決方案**:
```bash
# 確保在專案根目錄執行
export PYTHONPATH=$PWD:$PYTHONPATH

# 或使用 -m 參數
python -m app.main
```

### 3. 端口被佔用

**問題**: `Address already in use`

**解決方案**:
```bash
# 查找佔用端口的程序
lsof -i :8080

# 終止程序
kill -9 <PID>

# 或使用不同端口
export PORT=8081
```

## 部署問題

### 1. Docker 建置失敗

**問題**: Docker 映像建置錯誤

**解決方案**:
```bash
# 清理 Docker 快取
docker system prune -a

# 使用多階段建置
docker build --no-cache -t line-notion-bot .
```

### 2. GCP 認證問題

**問題**: 無法存取 GCP 服務

**解決方案**:
```bash
# 重新認證
gcloud auth login
gcloud auth application-default login

# 檢查專案設定
gcloud config list
```

### 3. Secret Manager 存取錯誤

**問題**: 無法讀取密鑰

**解決方案**:
```bash
# 檢查服務帳號權限
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:SERVICE_ACCOUNT_EMAIL" \
  --role="roles/secretmanager.secretAccessor"
```

## API 整合問題

### 1. Line Bot 無回應

**檢查清單**:
- [ ] Webhook URL 設定正確
- [ ] Channel Access Token 有效
- [ ] Channel Secret 正確
- [ ] 應用程式正在運行
- [ ] 防火牆設定允許流量

**除錯步驟**:
```bash
# 檢查應用程式日誌
gcloud logs read --service=line-notion-bot --limit=50

# 測試 Webhook 端點
curl -X POST https://your-service-url/webhook \
  -H "Content-Type: application/json" \
  -d '{"events":[]}'
```

### 2. Notion API 連線失敗

**檢查清單**:
- [ ] Integration Token 正確
- [ ] 資料庫已分享給 Integration
- [ ] 資料庫 ID 正確
- [ ] 網路連線正常

**除錯步驟**:
```bash
# 測試 Notion API 連線
curl -X GET https://api.notion.com/v1/databases/DATABASE_ID \
  -H "Authorization: Bearer NOTION_TOKEN" \
  -H "Notion-Version: 2022-06-28"
```

### 3. 搜尋結果為空

**可能原因**:
- 資料庫中沒有匹配的內容
- 搜尋關鍵字過於具體
- 資料庫權限設定問題

**解決方案**:
- 檢查資料庫內容
- 嘗試更廣泛的搜尋詞
- 確認 Integration 有讀取權限

## 效能問題

### 1. 回應時間過長

**優化建議**:
- 增加 Cloud Run 的 CPU 和記憶體配置
- 實作快取機制
- 優化 Notion API 查詢
- 使用連線池

### 2. 記憶體使用過高

**解決方案**:
```yaml
# 在 cloudbuild.yaml 中調整資源限制
--memory: "1Gi"
--cpu: "2"
```

## 監控和除錯

### 1. 啟用詳細日誌

```bash
# 設定環境變數
export DEBUG=true
export LOG_LEVEL=DEBUG
```

### 2. 健康檢查

```bash
# 檢查應用程式狀態
curl https://your-service-url/health

# 檢查根端點
curl https://your-service-url/
```

### 3. 即時日誌監控

```bash
# 即時查看日誌
gcloud logs tail --service=line-notion-bot

# 過濾錯誤日誌
gcloud logs read --service=line-notion-bot \
  --filter="severity>=ERROR" --limit=20
```

## 聯繫支援

如果以上解決方案都無法解決問題，請：

1. 收集錯誤日誌
2. 記錄重現步驟
3. 檢查環境配置
4. 開啟 GitHub Issue 或聯繫維護者

---

**提示**: 在報告問題時，請提供詳細的錯誤訊息和環境資訊，這將有助於快速診斷和解決問題。