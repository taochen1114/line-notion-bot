#!/bin/bash

# Line Bot Notion API 部署腳本

set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 函數：印出彩色訊息
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 檢查必要工具
check_requirements() {
    print_info "檢查必要工具..."
    
    if ! command -v gcloud &> /dev/null; then
        print_error "gcloud CLI 未安裝，請先安裝 Google Cloud SDK"
        exit 1
    fi
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker 未安裝，請先安裝 Docker"
        exit 1
    fi
    
    print_info "必要工具檢查完成"
}

# 檢查 GCP 認證
check_gcp_auth() {
    print_info "檢查 GCP 認證..."
    
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        print_error "未登入 GCP，請執行 'gcloud auth login'"
        exit 1
    fi
    
    PROJECT_ID=$(gcloud config get-value project)
    if [ -z "$PROJECT_ID" ]; then
        print_error "未設定 GCP 專案，請執行 'gcloud config set project YOUR_PROJECT_ID'"
        exit 1
    fi
    
    print_info "GCP 認證檢查完成，專案：$PROJECT_ID"
}

# 啟用必要的 API
enable_apis() {
    print_info "啟用必要的 GCP API..."
    
    gcloud services enable run.googleapis.com
    gcloud services enable cloudbuild.googleapis.com
    gcloud services enable secretmanager.googleapis.com
    gcloud services enable logging.googleapis.com
    
    print_info "API 啟用完成"
}

# 檢查 Secrets
check_secrets() {
    print_info "檢查 Secret Manager 中的密鑰..."
    
    REQUIRED_SECRETS=("line-channel-access-token" "line-channel-secret" "notion-api-token" "notion-database-id")
    
    for secret in "${REQUIRED_SECRETS[@]}"; do
        if ! gcloud secrets describe "$secret" &> /dev/null; then
            print_warning "密鑰 '$secret' 不存在，請先建立"
            echo "建立方式：echo -n 'your_secret_value' | gcloud secrets create $secret --data-file=-"
        else
            print_info "密鑰 '$secret' 存在"
        fi
    done
}

# 建置和部署
deploy() {
    print_info "開始建置和部署..."
    
    # 使用 Cloud Build 部署
    gcloud builds submit --config cloudbuild.yaml
    
    print_info "部署完成"
}

# 取得服務 URL
get_service_url() {
    print_info "取得服務 URL..."
    
    SERVICE_URL=$(gcloud run services describe line-notion-bot --region=asia-east1 --format="value(status.url)")
    
    if [ -n "$SERVICE_URL" ]; then
        print_info "服務 URL: $SERVICE_URL"
        print_info "Webhook URL: $SERVICE_URL/webhook"
        print_info "健康檢查 URL: $SERVICE_URL/health"
    else
        print_error "無法取得服務 URL"
    fi
}

# 測試部署
test_deployment() {
    print_info "測試部署..."
    
    if [ -n "$SERVICE_URL" ]; then
        # 測試健康檢查端點
        if curl -f "$SERVICE_URL/health" &> /dev/null; then
            print_info "健康檢查通過"
        else
            print_error "健康檢查失敗"
        fi
        
        # 測試根端點
        if curl -f "$SERVICE_URL/" &> /dev/null; then
            print_info "根端點測試通過"
        else
            print_error "根端點測試失敗"
        fi
    else
        print_warning "跳過部署測試（無服務 URL）"
    fi
}

# 顯示後續步驟
show_next_steps() {
    print_info "部署完成！後續步驟："
    echo ""
    echo "1. 將 Webhook URL 設定到 Line Developers Console："
    echo "   $SERVICE_URL/webhook"
    echo ""
    echo "2. 測試 Line Bot 功能"
    echo ""
    echo "3. 查看日誌："
    echo "   gcloud logs read --service=line-notion-bot --limit=50"
    echo ""
    echo "4. 即時查看日誌："
    echo "   gcloud logs tail --service=line-notion-bot"
}

# 主函數
main() {
    print_info "開始 Line Bot Notion API 部署流程"
    
    check_requirements
    check_gcp_auth
    enable_apis
    check_secrets
    deploy
    get_service_url
    test_deployment
    show_next_steps
    
    print_info "部署流程完成"
}

# 執行主函數
main "$@"