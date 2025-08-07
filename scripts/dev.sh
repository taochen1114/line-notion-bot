#!/bin/bash

# Line Bot Notion API 開發啟動腳本

set -e

# 顏色定義
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 檢查 Python 環境
check_python() {
    print_info "檢查 Python 環境..."
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 未安裝"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    print_info "Python 版本: $PYTHON_VERSION"
    
    if [[ $(echo "$PYTHON_VERSION >= 3.9" | bc -l) -eq 0 ]]; then
        print_warning "建議使用 Python 3.9 或更高版本"
    fi
}

# 檢查虛擬環境
check_venv() {
    print_info "檢查虛擬環境..."
    
    if [ ! -d "venv" ]; then
        print_info "建立虛擬環境..."
        python3 -m venv venv
    fi
    
    print_info "啟動虛擬環境..."
    source venv/bin/activate
    
    print_info "升級 pip..."
    pip install --upgrade pip
}

# 安裝依賴
install_dependencies() {
    print_info "安裝 Python 依賴..."
    pip install -r requirements.txt
}

# 檢查環境變數
check_env() {
    print_info "檢查環境變數..."
    
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            print_warning ".env 檔案不存在，複製 .env.example"
            cp .env.example .env
            print_warning "請編輯 .env 檔案並填入正確的設定值"
        else
            print_error ".env.example 檔案不存在"
            exit 1
        fi
    fi
    
    # 檢查必要的環境變數
    source .env
    
    REQUIRED_VARS=("LINE_CHANNEL_ACCESS_TOKEN" "LINE_CHANNEL_SECRET" "NOTION_API_TOKEN" "NOTION_DATABASE_ID")
    
    for var in "${REQUIRED_VARS[@]}"; do
        if [ -z "${!var}" ] || [ "${!var}" = "your_${var,,}_here" ]; then
            print_warning "環境變數 $var 未設定或使用預設值"
        fi
    done
}

# 執行測試
run_tests() {
    print_info "執行測試..."
    
    if command -v pytest &> /dev/null; then
        pytest tests/ -v
    else
        print_warning "pytest 未安裝，跳過測試"
    fi
}

# 啟動開發伺服器
start_server() {
    print_info "啟動開發伺服器..."
    print_info "伺服器將在 http://localhost:8080 啟動"
    print_info "按 Ctrl+C 停止伺服器"
    
    python -m app.main
}

# 主函數
main() {
    print_info "Line Bot Notion API 開發環境啟動"
    
    check_python
    check_venv
    install_dependencies
    check_env
    
    # 詢問是否執行測試
    read -p "是否執行測試？(y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        run_tests
    fi
    
    start_server
}

# 執行主函數
main "$@"