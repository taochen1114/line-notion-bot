#!/bin/bash

# Line Bot Notion API 安裝問題修復腳本

set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# 檢查 Python 版本
check_python_version() {
    print_step "檢查 Python 版本..."
    
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
    print_info "當前 Python 版本: $PYTHON_VERSION"
    
    # 檢查是否為 Python 3.12
    if [[ "$PYTHON_VERSION" == "3.12" ]]; then
        print_warning "檢測到 Python 3.12，將使用相容版本的套件"
        USE_PY312_REQUIREMENTS=true
    else
        USE_PY312_REQUIREMENTS=false
    fi
}

# 清理並重建虛擬環境
rebuild_venv() {
    print_step "重建虛擬環境..."
    
    if [ -d "venv" ]; then
        print_info "移除舊的虛擬環境..."
        rm -rf venv
    fi
    
    print_info "建立新的虛擬環境..."
    python3 -m venv venv
    
    print_info "啟動虛擬環境..."
    source venv/bin/activate
    
    print_info "升級 pip..."
    pip install --upgrade pip
}

# 安裝系統依賴 (macOS)
install_system_deps_macos() {
    print_step "檢查 macOS 系統依賴..."
    
    # 檢查 Xcode Command Line Tools
    if ! xcode-select -p &> /dev/null; then
        print_warning "Xcode Command Line Tools 未安裝"
        print_info "正在安裝 Xcode Command Line Tools..."
        xcode-select --install
        
        print_warning "請等待 Xcode Command Line Tools 安裝完成後再繼續"
        read -p "安裝完成後按 Enter 繼續..."
    else
        print_info "Xcode Command Line Tools 已安裝"
    fi
    
    # 檢查 Homebrew
    if ! command -v brew &> /dev/null; then
        print_warning "Homebrew 未安裝，建議安裝以管理系統依賴"
        print_info "安裝方式："
        echo '  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
    else
        print_info "Homebrew 已安裝"
    fi
}

# 使用預編譯套件安裝
install_with_wheels() {
    print_step "使用預編譯套件安裝依賴..."
    
    # 設定編譯器環境變數
    export CC=clang
    export CXX=clang++
    
    # 根據 Python 版本選擇 requirements 檔案
    if [[ "$USE_PY312_REQUIREMENTS" == "true" ]]; then
        REQUIREMENTS_FILE="requirements-py312.txt"
        print_info "使用 Python 3.12 相容版本的依賴..."
    else
        REQUIREMENTS_FILE="requirements.txt"
        print_info "使用標準版本的依賴..."
    fi
    
    # 使用預編譯套件安裝
    print_info "安裝依賴套件..."
    pip install --only-binary=all -r "$REQUIREMENTS_FILE"
}

# 備用安裝方法
fallback_install() {
    print_step "使用備用安裝方法..."
    
    print_info "清理 pip 快取..."
    pip cache purge
    
    # 根據 Python 版本選擇 requirements 檔案
    if [[ "$USE_PY312_REQUIREMENTS" == "true" ]]; then
        REQUIREMENTS_FILE="requirements-py312.txt"
        print_info "使用 Python 3.12 相容版本進行備用安裝..."
    else
        REQUIREMENTS_FILE="requirements.txt"
        print_info "使用標準版本進行備用安裝..."
    fi
    
    print_info "從 requirements 檔案安裝..."
    pip install --no-cache-dir -r "$REQUIREMENTS_FILE"
}

# 驗證安裝
verify_installation() {
    print_step "驗證安裝..."
    
    print_info "檢查核心套件..."
    python -c "import fastapi; print(f'FastAPI: {fastapi.__version__}')"
    python -c "import uvicorn; print(f'Uvicorn: {uvicorn.__version__}')"
    python -c "import pydantic; print(f'Pydantic: {pydantic.__version__}')"
    
    print_info "檢查 Line Bot SDK..."
    python -c "import linebot; print('Line Bot SDK: OK')"
    
    print_info "檢查 Notion 客戶端..."
    python -c "import notion_client; print('Notion Client: OK')"
    
    print_info "檢查應用程式導入..."
    python -c "from app.config import get_settings; print('App Config: OK')"
    python -c "from app.main import app; print('App Main: OK')"
    
    print_info "所有套件安裝成功！"
}

# 主函數
main() {
    print_info "Line Bot Notion API 安裝問題修復工具"
    echo
    
    # 檢查作業系統
    if [[ "$OSTYPE" == "darwin"* ]]; then
        install_system_deps_macos
    fi
    
    check_python_version
    rebuild_venv
    
    # 啟動虛擬環境
    source venv/bin/activate
    
    print_info "嘗試使用預編譯套件安裝..."
    if install_with_wheels; then
        print_info "預編譯套件安裝成功"
    else
        print_warning "預編譯套件安裝失敗，使用備用方法..."
        fallback_install
    fi
    
    verify_installation
    
    print_info "修復完成！"
    print_info "現在可以執行 './scripts/dev.sh' 啟動開發環境"
}

# 執行主函數
main "$@"