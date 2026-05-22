# Pytesseract 完全ガイド - 目次

スキャンPDFのOCR処理を効率的に行うための完全なドキュメント一式です。

> **Version:** v1.1.0 | **Last Updated:** 2026-05-22

## 📦 含まれるファイル

### 1. **Pytesseract_Complete_Guide.docx** （メインドキュメント）
詳細な解説書（44KB）

**内容:**
- Pytesseractとは
- 環境構築手順（Linux/macOS/Windows）
- 基本的な使い方
- PDFからの画像抽出とOCR処理
- トークン消費の削減効果
- 実装例とベストプラクティス
- トラブルシューティング
- パフォーマンス最適化

**推奨用途:** 詳しく学びたい方、初めて使う方

### 2. **pytesseract_sample_code.py** （実装例）
すぐに実行できるPythonコード

**含まれる関数:**
- `setup_tesseract_path()` - Tesseractのセットアップ
- `check_tesseract_installation()` - インストール確認
- `image_to_text()` - 画像からのテキスト抽出
- `pdf_to_text()` - PDFの完全な処理
- `pdf_to_text_with_page_range()` - ページ範囲指定
- `batch_pdf_processing()` - 複数PDFの一括処理
- `preprocess_image()` - 画像前処理

**推奨用途:** コード実装時に参考にする

### 3. **setup_pytesseract.sh** （自動セットアップスクリプト）
環境構築を自動化するBashスクリプト

**実行方法:**
```bash
chmod +x setup_pytesseract.sh
./setup_pytesseract.sh
```

**自動実行内容:**
- Tesseract-OCRのインストール
- 言語パッケージ（日本語など）のインストール
- Pythonパッケージのインストール
- インストール確認
- 動作テスト

**推奨用途:** 初回セットアップ

### 4. **pytesseract_cheatsheet.py** （クイックリファレンス）
よく使う機能をまとめたチートシート

**内容:**
- インストール方法の一覧
- 基本的な使い方（コード例）
- 言語オプション
- PSM（ページ分割モード）
- よくある例
- エラーハンドリング
- パフォーマンス最適化
- FAQ
- トークン消費計算

**推奨用途:** 用途を決めてすぐ実装したい方

### 5. **check_windows_environment.ps1** （Windows環境チェックスクリプト）
Windowsで必要なプログラム類のインストール状況を事前確認するPowerShellスクリプト

**実行方法:**
```powershell
powershell -ExecutionPolicy Bypass -File .\check_windows_environment.ps1
```

**確認内容:**
- 確認日 / コンピュータ名 / ユーザー名
- OS / PowerShell バージョン
- Python / pip
- Python パッケージ（pytesseract / Pillow / pdf2image）
- Tesseract-OCR とインストール先
- 言語パック（jpn / eng）の有無
- Poppler（pdf2image が依存）

**推奨用途:** Windowsユーザーがセットアップ前に環境を確認したいとき

---

## 🚀 クイックスタート

### 1. インストール

**方法A: 自動セットアップ（推奨）**
```bash
chmod +x setup_pytesseract.sh
./setup_pytesseract.sh
```

**方法B: 手動セットアップ**

Linux (Ubuntu):
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-jpn
pip install pytesseract pillow pdf2image
```

macOS:
```bash
brew install tesseract tesseract-lang
pip install pytesseract pillow pdf2image
```

Windows:
1. https://github.com/UB-Mannheim/tesseract/wiki からインストーラをダウンロード
2. インストール時に「Japanese」言語を選択
3. `pip install pytesseract pillow pdf2image`

**インストール後の事前チェック（推奨）:**
```powershell
powershell -ExecutionPolicy Bypass -File .\check_windows_environment.ps1
```
必要なプログラム・パッケージ・言語パックが揃っているかを確認できます。

### 2. 最初のOCR処理

**シンプルな例:**
```python
from pytesseract_sample_code import pdf_to_text

# PDFをテキストに変換
result = pdf_to_text('document.pdf')

# 結果を保存
with open('output.txt', 'w', encoding='utf-8') as f:
    f.write(result)
```

**複数PDFの一括処理:**
```python
from pytesseract_sample_code import batch_pdf_processing

results = batch_pdf_processing('./pdf_folder/')
print(f"完了: 成功 {results['success']}, エラー {results['error']}")
```

---

## 📊 トークン消費の削減効果

**シナリオ: 100ページのスキャンPDF×10個/月**

### 方法1: Claude.aiで直接アップロード
- トークン消費: 1,000ページ × 1,600 = **1,600,000トークン**
- 月額コスト: 約$16～20

### 方法2: Pytesseract + Claude（推奨）
- OCR処理: **無料**（Tesseract）
- テキスト送信: 35,000トークン
- 月額コスト: **ほぼ0円**

### 削減率: **97.8%**

---

## 📝 使用例別ガイド

### 用途1: 単一のスキャンPDFを処理
```python
from pytesseract_sample_code import pdf_to_text

text = pdf_to_text('document.pdf')
```
→ pytesseract_cheatsheet.py の「例1」を参照

### 用途2: 大量のスキャンPDFを処理
```python
from pytesseract_sample_code import batch_pdf_processing

results = batch_pdf_processing('./scanned_pdfs/')
```
→ pytesseract_sample_code.py の `batch_pdf_processing()` を参照

### 用途3: 特定ページだけを処理
```python
from pytesseract_sample_code import pdf_to_text_with_page_range

text = pdf_to_text_with_page_range('large_doc.pdf', first_page=1, last_page=5)
```
→ pytesseract_sample_code.py の `pdf_to_text_with_page_range()` を参照

### 用途4: OCR精度を最大化
→ Pytesseract_Complete_Guide.docx の「6. 実装例とベストプラクティス」を参照

---

## 🔧 トラブルシューティング

### よくある問題

**Q: TesseractNotFoundError**
- 原因: Tesseract-OCRがインストールされていない
- 解決:
  - Linux/macOS: `setup_pytesseract.sh` を実行
  - Windows: `check_windows_environment.ps1` で状況を確認後、インストーラを実行

**Q: 日本語が認識されない**
- 原因: 日本語言語パッケージがない
- 解決: `sudo apt-get install tesseract-ocr-jpn` (Linux)

**Q: OCR精度が低い**
- 原因: DPI設定やPSM設定の問題
- 解決: Pytesseract_Complete_Guide.docx の「6.2 品質向上のテクニック」を参照

詳細は pytesseract_cheatsheet.py の「11. よくある質問」を参照

---

## 📚 ドキュメント体系

```
初めて使う方の流れ:
1. setup_pytesseract.sh を実行 → インストール
2. pytesseract_cheatsheet.py で基本を確認
3. pytesseract_sample_code.py で実装
4. Pytesseract_Complete_Guide.docx で詳細を学習
```

```
すぐに実装したい方の流れ:
1. pytesseract_cheatsheet.py で該当する例を探す
2. コードをコピー＆ペースト
3. 必要に応じて pytesseract_sample_code.py で詳細を参照
```

```
詳しく学びたい方の流れ:
1. Pytesseract_Complete_Guide.docx を最初から読む
2. pytesseract_sample_code.py で実装パターンを確認
3. pytesseract_cheatsheet.py でリファレンスとして活用
```

---

## 🎯 推奨される使用パターン

### パターン1: コスト最適化
目的: Claude のトークン消費を最小化

```
スキャンPDF
    ↓
[Pytesseract で無料OCR]
    ↓
テキストファイル
    ↓
[Claude に送信 → 高トークン効率]
```

**推奨設定:**
- DPI: 300（精度重視） または 150（速度重視）
- lang: 'jpn+eng'
- PSM: '--psm 6'

### パターン2: 高速処理
目的: 処理速度を最大化

```
スキャンPDF
    ↓
[Pytesseract で高速OCR（DPI150、PSM6）]
    ↓
テキストファイル（簡易版）
    ↓
[Claude に送信 → 簡易分析]
```

**推奨設定:**
- DPI: 150
- lang: 'jpn' のみ（不要言語を除外）
- マルチプロセッシング: 有効

### パターン3: 高精度処理
目的: OCR精度を最大化

```
スキャンPDF
    ↓
[画像前処理 → ノイズ除去、コントラスト調整]
    ↓
[Pytesseract で高精度OCR（DPI300、PSM3）]
    ↓
[後処理 → 誤り訂正]
    ↓
[Claude に送信 → 詳細分析]
```

**推奨設定:**
- DPI: 300
- 画像前処理: 有効
- PSM: '--psm 3' または '--psm 6'
- 後処理: 正規表現による形式チェック

---

## 📈 パフォーマンス指標

### 処理時間の目安（1ページあたり）
- Pytesseract（DPI300）: 2～3秒
- Pytesseract（DPI150）: 1～1.5秒
- Claude.ai直接アップロード: 30秒～1分

### トークン消費の目安
- スキャンPDFをClaude直接: 1,600トークン/ページ
- Pytesseract + Claude: 250トークン/1000文字

### 推奨環境
- CPU: 4コア以上
- メモリ: 4GB以上
- ストレージ: 100GB以上（大量処理時）

---

## ✅ 動作確認チェックリスト

- [ ] Tesseract-OCRがインストールされている
- [ ] 言語パッケージ（日本語）がインストールされている
- [ ] Pythonパッケージがインストールされている
- [ ] setup_pytesseract.sh の確認テストに成功（Linux/macOS）
- [ ] check_windows_environment.ps1 がすべてOKを返す（Windows）
- [ ] pytesseract_sample_code.py で実行確認
- [ ] PDFファイルでテスト実行成功

---

## 🔗 参考資料

- **公式リンク:**
  - Pytesseract: https://github.com/madmaze/pytesseract
  - Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
  - pdf2image: https://github.com/Belval/pdf2image

- **関連ドキュメント:**
  - Claude_Token_Consumption_Guide.docx
    （Claude 全般のトークン消費について）

---

## 💡 よくある質問

**Q: Pytesseractはどのくらい精度がありますか？**
A: 一般的に85～95%の精度が期待できます。スキャン品質が良いほど精度が高くなります。

**Q: 日本語と英語が混在した書類は処理できますか？**
A: はい、`lang='jpn+eng'` で処理できます。

**Q: オフラインで処理できますか？**
A: はい、Pytesseractはサーバー連携不要で、ローカルのみで処理できます。

**Q: 商用利用は可能ですか？**
A: はい、Tesseract-OCRはオープンソース（Apache License 2.0）で商用利用可能です。

**Q: GPUを使って高速化できますか？**
A: Tesseract 標準版は GPU 対応していません。CUDA 対応版の構築は可能ですが複雑です。

---

## 📞 サポート

質問やバグ報告は：
- Pytesseract GitHub Issues: https://github.com/madmaze/pytesseract/issues
- Tesseract GitHub Issues: https://github.com/UB-Mannheim/tesseract/issues

---

## 📄 ドキュメント作成日

2026年5月14日

最終更新: 2026年5月14日

---

## 🎓 学習順序（推奨）

1. このREADMEを読む（10分）
2. **Windowsユーザーは check_windows_environment.ps1 で環境を事前確認（2分）**
3. setup_pytesseract.sh（Linux/macOS）または手動セットアップ（Windows）（10～30分）
4. pytesseract_cheatsheet.py で基本を確認（10分）
5. pytesseract_sample_code.py でコピ＆ペーストで実装（5分）
6. Pytesseract_Complete_Guide.docx で詳細を学習（30～60分）

**総学習時間: 約1～2時間で実装可能**

---

本ドキュメント一式を活用して、効率的で経済的なOCR処理を実現してください！
