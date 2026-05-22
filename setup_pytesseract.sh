#!/bin/bash
# Pytesseract セットアップスクリプト
# このスクリプトはLinuxおよびmacOSで使用可能です

set -e  # エラーで止まる

echo "========================================"
echo "Pytesseract 環境構築スクリプト"
echo "========================================"
echo ""

# OSの判定
OS_TYPE=$(uname -s)

# ========================================
# Tesseract-OCRのインストール
# ========================================

install_tesseract() {
    echo "Tesseract-OCRのインストール中..."
    
    if [ "$OS_TYPE" = "Linux" ]; then
        echo "Linux環境でインストール..."
        
        # Ubuntuの場合
        if command -v apt-get &> /dev/null; then
            echo "パッケージリストを更新中..."
            sudo apt-get update
            
            echo "Tesseractをインストール中..."
            sudo apt-get install -y tesseract-ocr
            
            echo "日本語言語パッケージをインストール中..."
            sudo apt-get install -y tesseract-ocr-jpn
            
            echo "その他の言語パッケージをインストール中..."
            sudo apt-get install -y tesseract-ocr-eng tesseract-ocr-chi-sim
        
        # Fedora/CentOSの場合
        elif command -v yum &> /dev/null; then
            echo "Fedora/CentOSでインストール..."
            sudo yum install -y tesseract
            sudo yum install -y tesseract-langpack-jpn
        fi
    
    elif [ "$OS_TYPE" = "Darwin" ]; then
        echo "macOS環境でインストール..."
        
        # Homebrewの確認
        if ! command -v brew &> /dev/null; then
            echo "Homebrewがインストールされていません"
            echo "以下のコマンドでインストール："
            echo '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
            exit 1
        fi
        
        echo "Tesseractをインストール中..."
        brew install tesseract
        
        echo "言語パッケージをインストール中..."
        brew install tesseract-lang
    
    else
        echo "対応していないOSです: $OS_TYPE"
        echo "Windowsの場合は以下を参照："
        echo "https://github.com/UB-Mannheim/tesseract/wiki"
        exit 1
    fi
    
    echo "✓ Tesseract-OCRのインストール完了"
}

# ========================================
# Pythonパッケージのインストール
# ========================================

install_python_packages() {
    echo ""
    echo "Pythonパッケージをインストール中..."
    
    # pipのアップグレード
    echo "pipをアップグレード中..."
    pip install --upgrade pip
    
    # 必須パッケージ
    echo "必須パッケージをインストール中..."
    pip install pytesseract pillow pdf2image
    
    # オプションパッケージ
    echo ""
    echo "オプションパッケージのインストール"
    read -p "OpenCV（画像処理用）をインストールしますか？ [y/N]: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        pip install opencv-python
        echo "✓ OpenCVインストール完了"
    fi
    
    read -p "poppler（PDF→画像変換の高速化用）をインストールしますか？ [y/N]: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if [ "$OS_TYPE" = "Linux" ]; then
            sudo apt-get install -y poppler-utils
        elif [ "$OS_TYPE" = "Darwin" ]; then
            brew install poppler
        fi
        echo "✓ popplerインストール完了"
    fi
    
    echo "✓ Pythonパッケージのインストール完了"
}

# ========================================
# インストール確認
# ========================================

verify_installation() {
    echo ""
    echo "インストール確認中..."
    
    # Tesseractバージョン確認
    if command -v tesseract &> /dev/null; then
        echo "✓ Tesseract-OCR:"
        tesseract --version | head -1
    else
        echo "✗ Tesseract-OCRが見つかりません"
        return 1
    fi
    
    # Pythonパッケージ確認
    echo ""
    echo "✓ Pythonパッケージ:"
    
    python3 -c "import pytesseract; print(f'  - pytesseract: OK')" 2>/dev/null || echo "  - pytesseract: 見つかりません"
    python3 -c "import PIL; print(f'  - Pillow: OK')" 2>/dev/null || echo "  - Pillow: 見つかりません"
    python3 -c "import pdf2image; print(f'  - pdf2image: OK')" 2>/dev/null || echo "  - pdf2image: 見つかりません"
    
    # 日本語パッケージ確認
    echo ""
    echo "言語パッケージ確認："
    if [ "$OS_TYPE" = "Linux" ]; then
        if dpkg -l | grep tesseract-ocr-jpn > /dev/null; then
            echo "✓ 日本語パッケージ: インストール済み"
        else
            echo "✗ 日本語パッケージ: 未インストール"
        fi
    elif [ "$OS_TYPE" = "Darwin" ]; then
        if tesseract --list-langs | grep jpn > /dev/null; then
            echo "✓ 日本語パッケージ: インストール済み"
        else
            echo "✗ 日本語パッケージ: 未インストール"
        fi
    fi
}

# ========================================
# テスト実行
# ========================================

run_test() {
    echo ""
    echo "テスト実行中..."
    
    python3 << 'EOF'
import pytesseract
from PIL import Image
import io

# テスト用の画像を生成
test_image = Image.new('RGB', (100, 30), color='white')

try:
    # OCR処理テスト
    result = pytesseract.image_to_string(test_image, lang='eng')
    print("✓ Pytesseractのテスト: 成功")
except Exception as e:
    print(f"✗ Pytesseractのテスト: 失敗 ({e})")
EOF
}

# ========================================
# メイン処理
# ========================================

main() {
    echo "このセットアップスクリプトは以下をインストールします："
    echo "  1. Tesseract-OCR（OCRエンジン）"
    echo "  2. 言語パッケージ（日本語を含む）"
    echo "  3. Pythonパッケージ（pytesseract, Pillow, pdf2imageなど）"
    echo ""
    read -p "続行しますか？ [y/N]: " -n 1 -r
    echo
    
    if ! [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "セットアップをキャンセルしました"
        exit 0
    fi
    
    # インストール実行
    install_tesseract
    echo ""
    install_python_packages
    
    # 確認
    verify_installation
    
    # テスト
    run_test
    
    echo ""
    echo "========================================"
    echo "セットアップ完了！"
    echo "========================================"
    echo ""
    echo "次のステップ："
    echo "1. 以下のコマンドでサンプルコードを実行："
    echo "   python3 pytesseract_sample_code.py"
    echo ""
    echo "2. PDFを処理する場合："
    echo "   python3 -c \"from pytesseract_sample_code import pdf_to_text; print(pdf_to_text('your_file.pdf'))\""
    echo ""
    echo "詳細はドキュメント「Pytesseract_Complete_Guide.docx」を参照してください。"
}

# スクリプト実行
main
