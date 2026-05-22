"""
Pytesseract OCR 実装サンプルコード
スキャンPDFをテキストに変換するための完全な実装例

使用前に以下をインストール：
  pip install pytesseract pillow pdf2image --break-system-packages
  
そして、Tesseract-OCRをインストール：
  Linux: sudo apt-get install tesseract-ocr tesseract-ocr-jpn
  macOS: brew install tesseract
  Windows: https://github.com/UB-Mannheim/tesseract/wiki からダウンロード
          （インストール状況は check_windows_environment.ps1 で確認できます）
"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional, List
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import traceback

# ========================================
# ロギング設定
# ========================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ========================================
# 基本的なOCR処理
# ========================================

def setup_tesseract_path():
    """
    Tesseractのパスを設定（Windows環境対応）
    """
    if sys.platform == 'win32':
        # Windowsの場合、明示的にパスを指定
        tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        if os.path.exists(tesseract_path):
            pytesseract.pytesseract.pytesseract_cmd = tesseract_path
            logger.info(f"Tesseractパスを設定: {tesseract_path}")
        else:
            logger.warning(f"Tesseractが見つかりません: {tesseract_path}")
            logger.info("インストール: https://github.com/UB-Mannheim/tesseract/wiki")


def check_tesseract_installation():
    """
    Tesseractがインストールされているか確認
    """
    try:
        version = pytesseract.get_tesseract_version()
        logger.info(f"✓ Tesseractインストール確認: {version}")
        return True
    except Exception as e:
        logger.error(f"✗ Tesseractが見つかりません: {e}")
        return False


def image_to_text(image_path: str, lang: str = 'jpn+eng') -> Optional[str]:
    """
    画像ファイルからテキストを抽出
    
    Args:
        image_path: 画像ファイルパス
        lang: 使用言語（デフォルト：日本語＋英語）
    
    Returns:
        抽出されたテキスト、またはエラー時はNone
    """
    try:
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"ファイルが見つかりません: {image_path}")
        
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image, lang=lang, config='--psm 6')
        
        logger.info(f"✓ テキスト抽出完了: {len(text)}文字")
        return text
    
    except Exception as e:
        logger.error(f"✗ 画像処理エラー: {e}")
        return None


# ========================================
# PDF処理関数
# ========================================

def pdf_to_text(
    pdf_path: str,
    lang: str = 'jpn+eng',
    dpi: int = 300,
    output_dir: Optional[str] = None
) -> Optional[str]:
    """
    PDFファイルをテキストに変換
    
    Args:
        pdf_path: PDFファイルパス
        lang: 使用言語（デフォルト：日本語＋英語）
        dpi: 解像度（デフォルト：300 DPI）
        output_dir: 中間画像の保存先（オプション）
    
    Returns:
        抽出されたテキスト、またはエラー時はNone
    """
    try:
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"ファイルが見つかりません: {pdf_path}")
        
        logger.info(f"PDF処理開始: {pdf_path} (DPI: {dpi})")
        
        # PDFを画像に変換
        images = convert_from_path(pdf_path, dpi=dpi)
        logger.info(f"PDF→画像変換完了: {len(images)}ページ")
        
        all_text = ""
        
        for page_num, image in enumerate(images, 1):
            try:
                # ページごとのOCR処理
                page_text = pytesseract.image_to_string(
                    image,
                    lang=lang,
                    config='--psm 6'
                )
                
                all_text += f"\n--- ページ {page_num} ({len(page_text)}文字) ---\n"
                all_text += page_text
                
                logger.info(f"ページ {page_num:3d}/{len(images)}: {len(page_text):5d}文字抽出")
            
            except Exception as e:
                logger.warning(f"ページ {page_num} のエラー: {e}")
                all_text += f"\n--- ページ {page_num} (エラー) ---\nOCR処理失敗\n"
                continue
        
        logger.info(f"✓ PDF処理完了: 全{len(all_text)}文字")
        return all_text
    
    except Exception as e:
        logger.error(f"✗ PDF処理エラー: {e}")
        traceback.print_exc()
        return None


def pdf_to_text_with_page_range(
    pdf_path: str,
    first_page: int = 1,
    last_page: Optional[int] = None,
    lang: str = 'jpn+eng',
    dpi: int = 300
) -> Optional[str]:
    """
    PDFの特定ページ範囲をテキストに変換
    
    Args:
        pdf_path: PDFファイルパス
        first_page: 開始ページ（1から始まる）
        last_page: 終了ページ（Noneの場合は最後まで）
        lang: 使用言語
        dpi: 解像度
    
    Returns:
        抽出されたテキスト
    """
    try:
        logger.info(f"ページ範囲指定でPDF処理: {first_page}～{last_page}")
        
        # 指定範囲の画像を取得
        images = convert_from_path(
            pdf_path,
            dpi=dpi,
            first_page=first_page,
            last_page=last_page
        )
        
        all_text = ""
        
        for i, image in enumerate(images, start=first_page):
            page_text = pytesseract.image_to_string(image, lang=lang, config='--psm 6')
            all_text += f"\n--- ページ {i} ---\n{page_text}"
            logger.info(f"ページ {i}: {len(page_text)}文字")
        
        return all_text
    
    except Exception as e:
        logger.error(f"✗ ページ範囲処理エラー: {e}")
        return None


# ========================================
# バッチ処理
# ========================================

def batch_pdf_processing(
    pdf_directory: str,
    lang: str = 'jpn+eng',
    dpi: int = 300,
    output_suffix: str = '_extracted.txt'
) -> dict:
    """
    ディレクトリ内の全PDFを処理
    
    Args:
        pdf_directory: PDFファイルが格納されているディレクトリ
        lang: 使用言語
        dpi: 解像度
        output_suffix: 出力ファイルの接尾辞
    
    Returns:
        処理結果の辞書
    """
    results = {
        'success': 0,
        'error': 0,
        'files': []
    }
    
    pdf_dir_path = Path(pdf_directory)
    pdf_files = list(pdf_dir_path.glob('*.pdf'))
    
    if not pdf_files:
        logger.warning(f"PDFファイルが見つかりません: {pdf_directory}")
        return results
    
    logger.info(f"バッチ処理開始: {len(pdf_files)}個のPDFファイル")
    
    for pdf_file in pdf_files:
        logger.info(f"\n処理中: {pdf_file.name}")
        
        try:
            # OCR処理
            extracted_text = pdf_to_text(str(pdf_file), lang=lang, dpi=dpi)
            
            if extracted_text:
                # 出力ファイルに保存
                output_file = pdf_file.stem + output_suffix
                output_path = pdf_dir_path / output_file
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(extracted_text)
                
                logger.info(f"✓ {output_file} に保存 ({len(extracted_text)}文字)")
                results['success'] += 1
                results['files'].append({
                    'pdf': pdf_file.name,
                    'output': output_file,
                    'characters': len(extracted_text)
                })
            else:
                logger.error(f"✗ {pdf_file.name}: テキスト抽出失敗")
                results['error'] += 1
        
        except Exception as e:
            logger.error(f"✗ {pdf_file.name}: {e}")
            results['error'] += 1
    
    logger.info(f"\n=== バッチ処理完了 ===")
    logger.info(f"成功: {results['success']}, エラー: {results['error']}")
    
    return results


# ========================================
# 画像前処理（品質向上）
# ========================================

def preprocess_image(image_path: str, output_path: Optional[str] = None) -> Image:
    """
    OCR精度を上げるための画像前処理
    
    Args:
        image_path: 入力画像パス
        output_path: 処理済み画像の保存先（オプション）
    
    Returns:
        処理済み画像オブジェクト
    """
    try:
        # OpenCVがある場合のみ実行
        import cv2
        import numpy as np
        
        logger.info(f"画像前処理開始: {image_path}")
        
        # グレースケール化
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        
        # ノイズ除去
        denoised = cv2.fastNlMeansDenoising(img, h=10)
        
        # コントラスト調整（CLAHE）
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)
        
        # 二値化
        _, binary = cv2.threshold(
            enhanced, 0, 255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )
        
        result_img = Image.fromarray(binary)
        
        if output_path:
            result_img.save(output_path)
            logger.info(f"✓ 前処理済み画像を保存: {output_path}")
        
        return result_img
    
    except ImportError:
        logger.warning("OpenCVがインストールされていません")
        logger.info("pip install opencv-python でインストール可能")
        # OpenCVなしの簡易処理
        img = Image.open(image_path)
        return img.convert('L')  # グレースケール化のみ
    
    except Exception as e:
        logger.error(f"✗ 画像前処理エラー: {e}")
        return Image.open(image_path)


# ========================================
# 実行例
# ========================================

def example_basic():
    """基本的な使用例"""
    print("\n" + "="*60)
    print("例1: 単一の画像ファイルからテキスト抽出")
    print("="*60)
    
    # 画像ファイルがあれば実行
    # result = image_to_text('scanned_page.png')
    print("スキップ（サンプル画像がないため）")


def example_pdf():
    """PDF処理の例"""
    print("\n" + "="*60)
    print("例2: PDFファイルをテキストに変換")
    print("="*60)
    
    # PDFファイルがあれば実行
    # result = pdf_to_text('document.pdf')
    # if result:
    #     with open('output.txt', 'w', encoding='utf-8') as f:
    #         f.write(result)
    print("スキップ（サンプルPDFがないため）")


def example_batch():
    """バッチ処理の例"""
    print("\n" + "="*60)
    print("例3: ディレクトリ内の複数PDFを処理")
    print("="*60)
    
    # 実際のディレクトリパスに変更
    # results = batch_pdf_processing('./pdf_folder/')
    # print(f"処理完了: 成功 {results['success']}, エラー {results['error']}")
    print("スキップ（サンプルディレクトリがないため）")


def example_page_range():
    """ページ範囲指定の例"""
    print("\n" + "="*60)
    print("例4: PDFの特定ページだけを処理")
    print("="*60)
    
    # 最初の5ページのみを処理
    # result = pdf_to_text_with_page_range(
    #     'large_document.pdf',
    #     first_page=1,
    #     last_page=5
    # )
    print("スキップ（サンプルPDFがないため）")


# ========================================
# メイン関数
# ========================================

def main():
    """メイン処理"""
    print("\n" + "="*60)
    print("Pytesseract OCR サンプル実行")
    print("="*60)
    
    # Tesseractのセットアップ
    setup_tesseract_path()
    
    # インストール確認
    if not check_tesseract_installation():
        print("\nTesseract-OCRがインストールされていません。")
        print("詳細はドキュメントを参照してください。")
        return
    
    # 言語パッケージの確認
    print("\n利用可能な言語パッケージを確認中...")
    try:
        # 簡単な画像でテスト
        test_text = pytesseract.image_to_string(
            Image.new('RGB', (100, 100), color='white'),
            lang='jpn+eng'
        )
        print("✓ 言語パッケージ確認成功")
    except Exception as e:
        print(f"✗ 言語パッケージエラー: {e}")
        print("日本語パッケージをインストールしてください")
        return
    
    # 各処理の例を実行
    example_basic()
    example_pdf()
    example_batch()
    example_page_range()
    
    print("\n" + "="*60)
    print("実装完了！")
    print("="*60)
    print("""
使用方法：

1. 単一の画像からテキスト抽出：
   >>> text = image_to_text('image.png')

2. PDFをテキストに変換：
   >>> text = pdf_to_text('document.pdf')

3. PDFの特定ページだけを処理：
   >>> text = pdf_to_text_with_page_range('doc.pdf', first_page=1, last_page=5)

4. ディレクトリ内の全PDFを処理：
   >>> results = batch_pdf_processing('./pdfs/')

詳細はドキュメント「Pytesseract_Complete_Guide.docx」を参照してください。
    """)


if __name__ == '__main__':
    main()
