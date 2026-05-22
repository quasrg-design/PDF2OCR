"""
Pytesseract クイックリファレンス
よく使う機能をまとめたチートシート

Version: v1.1.0
Last Updated: 2026-05-22
"""

# ========================================
# 1. インストール（最初に一度だけ実行）
# ========================================

"""
### Linux (Ubuntu/Debian)
$ sudo apt-get update
$ sudo apt-get install tesseract-ocr tesseract-ocr-jpn
$ pip install pytesseract pillow pdf2image

### macOS (Homebrew)
$ brew install tesseract tesseract-lang
$ pip install pytesseract pillow pdf2image

### Windows
1. https://github.com/UB-Mannheim/tesseract/wiki からインストーラダウンロード
2. インストール時に「Japanese」言語を選択
3. pip install pytesseract pillow pdf2image

### Windows 事前チェック（推奨）
インストール状況をまとめて確認するスクリプトが付属しています：
PS> powershell -ExecutionPolicy Bypass -File .\check_windows_environment.ps1
Python / pytesseract / Pillow / pdf2image / Tesseract-OCR / 言語パック
/ Poppler の有無と、確認日・コンピュータ名・ユーザー名を画面表示します。
"""

# ========================================
# 2. 基本的な使い方
# ========================================

# 単一画像からテキスト抽出
from PIL import Image
import pytesseract

text = pytesseract.image_to_string(Image.open('page.png'), lang='jpn')
print(text)

# PDFをテキストに変換
from pdf2image import convert_from_path

images = convert_from_path('document.pdf', dpi=300)
for image in images:
    text = pytesseract.image_to_string(image, lang='jpn')
    print(text)


# ========================================
# 3. よく使う言語オプション
# ========================================

lang='eng'                  # 英語のみ
lang='jpn'                  # 日本語のみ
lang='jpn+eng'              # 日本語＋英語（最も推奨）
lang='jpn+eng+chi_sim'      # 日本語＋英語＋中国語簡体字
lang='osd'                  # 自動言語検出


# ========================================
# 4. PSM（ページ分割モード）
# ========================================

# デフォルト（ほとんどの場合これで十分）
text = pytesseract.image_to_string(image, config='--psm 6')

# その他のモード
--psm 0   # モードを自動検出
--psm 3   # 完全に不規則なテキスト
--psm 4   # 複数のテキストブロック（可変フォント）
--psm 6   # 単一ブロックのテキスト（デフォルト）
--psm 7   # 単一行のテキスト
--psm 11  # スパース（散らばった）テキスト
--psm 13  # テキストと計算式が混在


# ========================================
# 5. 実践的な例
# ========================================

# 例1: PDFの最初の5ページだけを処理
from pdf2image import convert_from_path

images = convert_from_path('large_doc.pdf', dpi=300, first_page=1, last_page=5)
all_text = ""
for image in images:
    all_text += pytesseract.image_to_string(image, lang='jpn+eng')


# 例2: 複数のPDFを一括処理
import os
from pathlib import Path

pdf_dir = Path('./pdfs')
for pdf_file in pdf_dir.glob('*.pdf'):
    images = convert_from_path(str(pdf_file), dpi=300)
    
    output_file = pdf_file.stem + '_extracted.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        for image in images:
            text = pytesseract.image_to_string(image, lang='jpn+eng')
            f.write(text)
    
    print(f"✓ {output_file}")


# 例3: 画像の品質を上げてOCR精度を向上
from PIL import ImageFilter, ImageEnhance

def enhance_image(image):
    # ノイズ除去
    image = image.filter(ImageFilter.MedianFilter())
    
    # コントラスト向上
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)
    
    return image

image = Image.open('page.png')
enhanced = enhance_image(image)
text = pytesseract.image_to_string(enhanced, lang='jpn')


# 例4: スキャン品質に応じてDPI調整
import os
from pdf2image import convert_from_path

def smart_dpi_selection(pdf_path):
    """ファイルサイズから適切なDPIを選択"""
    file_size_mb = os.path.getsize(pdf_path) / (1024 * 1024)
    
    if file_size_mb > 50:
        dpi = 150  # 大きなファイルは低DPI
    elif file_size_mb > 20:
        dpi = 200
    else:
        dpi = 300  # 小さいファイルは高DPI
    
    return dpi

dpi = smart_dpi_selection('document.pdf')
images = convert_from_path('document.pdf', dpi=dpi)


# ========================================
# 6. エラーハンドリング
# ========================================

try:
    images = convert_from_path('document.pdf', dpi=300)
    
    for page_num, image in enumerate(images, 1):
        try:
            text = pytesseract.image_to_string(image, lang='jpn+eng')
            print(f"ページ {page_num}: OK ({len(text)}文字)")
        except Exception as e:
            print(f"ページ {page_num}: エラー ({e})")
            continue

except FileNotFoundError:
    print("PDFファイルが見つかりません")
except Exception as e:
    print(f"エラー: {e}")


# ========================================
# 7. パフォーマンス最適化
# ========================================

# 大きなPDFはページ範囲で分割処理
def process_large_pdf(pdf_path, pages_per_batch=10):
    from pdf2image import convert_from_path
    
    # 総ページ数を取得
    all_images = convert_from_path(pdf_path, first_page=1, last_page=1)
    total_pages = len(all_images)
    
    all_text = ""
    
    for start_page in range(1, total_pages + 1, pages_per_batch):
        end_page = min(start_page + pages_per_batch - 1, total_pages)
        
        images = convert_from_path(
            pdf_path,
            dpi=300,
            first_page=start_page,
            last_page=end_page
        )
        
        for image in images:
            text = pytesseract.image_to_string(image, lang='jpn+eng')
            all_text += text
    
    return all_text


# ========================================
# 8. Claude へのテキスト送信時の効率化
# ========================================

def prepare_for_claude(text, max_chars=100000):
    """
    Claude用にテキストを準備
    - 長さ制限
    - 形式統一
    - プロンプト追加
    """
    
    # テキスト長制限
    if len(text) > max_chars:
        text = text[:max_chars] + f"\n\n... (残り {len(text) - max_chars} 文字は省略)"
    
    # Claudeへのプロンプト例
    prompt = f"""以下のスキャン文書から抽出されたテキストです。
内容を要約してください。

---

{text}

---

要約："""
    
    return prompt


# ========================================
# 9. よくある質問と解決方法
# ========================================

"""
Q: 「TesseractNotFoundError」が出る
A: Tesseractがインストールされていません
   - Windows: インストーラからインストール
   - Linux: sudo apt-get install tesseract-ocr
   - macOS: brew install tesseract

Q: 日本語が認識されない
A: 日本語言語パッケージが必要です
   - Linux: sudo apt-get install tesseract-ocr-jpn
   - macOS: brew install tesseract-lang
   - Windows: インストール時に「Japanese」を選択

Q: OCR精度が低い
A: 以下を試してください
   - DPIを上げる（150 → 300）
   - PSMを変更（--psm 6 → --psm 3）
   - 画像を前処理する

Q: 処理が遅い
A: 以下で高速化できます
   - DPIを下げる（300 → 150）
   - ページ範囲指定で分割処理
   - 不要な言語を除外（lang='jpn' のみ）

Q: Claudeのトークン削減効果は？
A: スキャンPDF → Pytesseract → Claude のフロー
   - 従来: 32,000～48,000トークン
   - Pytesseract使用: 2,500～3,500トークン
   - 削減率: 92～97%
"""


# ========================================
# 10. トークン消費の計算
# ========================================

def estimate_tokens(pdf_path, method='pytesseract'):
    """
    推定トークン消費量を計算
    """
    import os
    from pdf2image import convert_from_path
    
    # PDF情報を取得
    file_size = os.path.getsize(pdf_path) / (1024 * 1024)
    images = convert_from_path(pdf_path, dpi=300, first_page=1, last_page=1)
    
    if method == 'direct':
        # Claude直接アップロード（画像処理）
        # ページ数推定: ファイルサイズから計算
        estimated_pages = max(1, int(file_size / 0.5))  # 1ページ ≈ 0.5MB
        tokens_per_page = 1600  # 画像: 1,600トークン/ページ
        total_tokens = estimated_pages * tokens_per_page
        
        print(f"Claude直接アップロード:")
        print(f"  推定ページ数: {estimated_pages}")
        print(f"  推定トークン: {total_tokens:,}")
        
    elif method == 'pytesseract':
        # Pytesseract → テキスト送信
        # 推定: 1万文字 = 2,500～3,500トークン
        estimated_chars = estimated_pages * 400  # 1ページ ≈ 400文字
        tokens_per_1000chars = 250  # 日本語: 約250トークン/1000文字
        total_tokens = int(estimated_chars / 1000 * tokens_per_1000chars)
        
        print(f"Pytesseract + Claude:")
        print(f"  推定文字数: {estimated_chars:,}")
        print(f"  推定トークン: {total_tokens:,}")
        print(f"  削減率: {(1 - total_tokens / (estimated_pages * 1600)) * 100:.1f}%")


# ========================================
# 11. よく使うコマンド集
# ========================================

"""
# インストール確認
tesseract --version

# 利用可能な言語確認
tesseract --list-langs

# 単一画像をOCR処理
pytesseract image_to_string('input.png')

# OCR結果の信頼度スコア取得
pytesseract image_to_data('input.png')

# PDFから画像抽出（一時的に）
pdftoppm input.pdf page -png

# 複数ページを処理
for i in {1..100}; do
  python3 -c "from pdf2image import convert_from_path; \\
  import pytesseract; \\
  img = convert_from_path('doc.pdf', first_page=$i, last_page=$i)[0]; \\
  print(pytesseract.image_to_string(img, lang='jpn'))" >> output.txt
done
"""


# ========================================
# 12. 参考リンク
# ========================================

"""
公式ドキュメント:
- Pytesseract: https://github.com/madmaze/pytesseract
- Tesseract: https://github.com/UB-Mannheim/tesseract/wiki

日本語関連:
- Tesseract 日本語言語パック: https://github.com/tesseract-ocr/tesseract/wiki/Data-Files

セットアップ:
- Linux/macOS: 本プロジェクトの setup_pytesseract.sh を実行
- Windows: 本プロジェクトの check_windows_environment.ps1 で事前確認

サンプルコード:
- 本プロジェクトの pytesseract_sample_code.py を参照

詳細ガイド:
- Pytesseract_Complete_Guide.docx を参照
"""
