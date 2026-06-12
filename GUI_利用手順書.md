# PDF2OCR GUI アプリ 利用手順書

スキャンPDFをドラッグ＆ドロップでテキスト化するGUIアプリ **pdf2ocr_gui.py / PDF2OCR.exe** の
インストールから利用までを、Windows初心者の方向けに順を追って説明します。

> **Version:** v1.2.2 | **Last Updated:** 2026-06-12 | **対象OS:** Windows 10 / 11

---

## 目次

1. [このアプリでできること](#1-このアプリでできること)
2. [事前準備（必要なソフト）](#2-事前準備必要なソフト)
3. [環境チェック（推奨）](#3-環境チェック推奨)
4. [使い方A：Pythonで起動する](#4-使い方apythonで起動する)
5. [使い方B：exe化して起動する](#5-使い方bexe化して起動する)
6. [アプリの操作方法](#6-アプリの操作方法)
7. [よくあるトラブルと解決法](#7-よくあるトラブルと解決法)
8. [仕様一覧](#8-仕様一覧)
9. [よくある質問（Q&A）](#9-よくある質問qa)

---

## 1. このアプリでできること

- スキャンしたPDF（画像化されたPDF）を **文字データ（テキスト）** に変換します
- **ドラッグ＆ドロップ** または **ボタン操作** でファイルを指定できます
- **複数のPDFをまとめて処理** できます（フォルダ単位の指定も可）
- 日本語・英語に対応（高精度設定：DPI 300 / `jpn+eng`）
- 変換結果は **PDFと同じ名前の .txt ファイル** として保存されます

```
┌──────────────┐      ┌───────────┐      ┌──────────────┐
│ スキャンPDF   │  →   │  PDF2OCR  │  →   │  テキスト(.txt) │
│ （画像）      │      │  （OCR）   │      │              │
└──────────────┘      └───────────┘      └──────────────┘
```

---

## 2. 事前準備（必要なソフト）

このアプリを動かすには、以下の3つが必要です。

| ソフト | 役割 | 入手先 |
|--------|------|--------|
| **Python** | アプリの実行（.py版のみ） | https://www.python.org/downloads/ |
| **Tesseract-OCR** | 文字認識エンジン（**日本語パック必須**） | https://github.com/UB-Mannheim/tesseract/wiki |
| **Poppler** | PDF→画像変換 | https://github.com/oschwartz10612/poppler-windows/releases |

### 2-1. Tesseract-OCR のインストール

1. 上記URLからインストーラ（`tesseract-ocr-w64-setup-5.x.x.exe`）をダウンロード
2. インストール時、言語選択画面で必ず **「Japanese」にチェック** を入れる
3. インストール先はデフォルト（`C:\Program Files\Tesseract-OCR`）のままでOK

> 💡 PATHを通さなくても、本アプリは標準インストール先を自動検出します。
> ただしコマンドで `tesseract` を使いたい場合は[7-4](#7-4-tesseract-が-path-に通っていないwarn)を参照してください。

### 2-2. Poppler のインストール

1. 上記URLから `Release-xx.xx.x-0.zip` をダウンロードして解凍
2. 解凍したフォルダ内の `Library\bin` のパスを環境変数 PATH に追加

> 💡 `winget install oschwartz10612.Poppler` でも導入できます。

### 2-3. Pythonパッケージのインストール

PowerShell で以下を実行します（.exe版を使う場合も、ビルド時に必要です）。

```powershell
pip install pytesseract pillow pdf2image tkinterdnd2
```

| パッケージ | 役割 |
|-----------|------|
| pytesseract | Tesseractを Python から呼び出す |
| pillow | 画像処理 |
| pdf2image | PDF を画像に変換 |
| tkinterdnd2 | **ドラッグ＆ドロップ機能**（無くても起動は可能） |

---

## 3. 環境チェック（推奨）

必要なソフトが揃っているか、付属のチェックスクリプトで確認できます。

```powershell
powershell -ExecutionPolicy Bypass -File .\check_windows_environment.ps1
```

すべて `[OK]` が並べば準備完了です。`[NG]` がある場合は、表示されるヒントに従って導入してください。

> 実行時に「スクリプトを実行できません」と出る場合は[7-1](#7-1-スクリプトを実行できません署名エラー)を参照。

---

## 4. 使い方A：Pythonで起動する

最も手軽な方法です。Pythonがインストール済みであることが前提です。

### 手順

1. PowerShell を開き、アプリのあるフォルダへ移動します
   ```powershell
   cd "C:\Users\＜ユーザー名＞\Documents\PDF2OCR"
   ```

2. アプリを起動します
   ```powershell
   python pdf2ocr_gui.py
   ```

3. ウィンドウが表示されたら成功です。[6章の操作方法](#6-アプリの操作方法)へ進んでください。

> 💡 `python` で動かない場合は `py pdf2ocr_gui.py` を試してください。

---

## 5. 使い方B：exe化して起動する

Pythonコマンドを使わず、**ダブルクリックで起動できるアプリ**にする方法です。
他のPCへ配布したい場合にも便利です。

### 手順

1. PowerShell を開き、アプリのあるフォルダへ移動します
   ```powershell
   cd "C:\Users\＜ユーザー名＞\Documents\PDF2OCR"
   ```

2. ビルドスクリプトを実行します
   ```powershell
   .\build_exe.bat
   ```

3. 数分待つと「完了！」と表示され、`dist\PDF2OCR.exe` が作成されます

4. `dist` フォルダ内の **PDF2OCR.exe をダブルクリック** すると起動します

### バッチがうまく動かない場合（手動ビルド）

```powershell
pip install pyinstaller tkinterdnd2
python -m PyInstaller --noconfirm --onefile --windowed --name PDF2OCR --collect-data tkinterdnd2 pdf2ocr_gui.py
```

> ⚠️ exe化しても、**実行するPCには Tesseract-OCR と Poppler が必要** です（これらはexeに含まれません）。

---

## 6. アプリの操作方法

アプリ画面の各部と操作の流れです。

```
┌─────────────────────────────────────────────┐
│  ここに PDF ファイル / フォルダを              │  ← ① ドロップゾーン
│  ドラッグ＆ドロップ                           │
├─────────────────────────────────────────────┤
│ [PDFファイルを選択] [フォルダを選択] [クリア]  │  ← ② 選択ボタン
├─────────────────────────────────────────────┤
│  処理対象のPDF                                │  ← ③ ファイルリスト
│   C:\...\sample1.pdf                         │
│   C:\...\sample2.pdf                         │
├─────────────────────────────────────────────┤
│  保存先                                       │  ← ④ 保存先設定
│   ○ PDFと同じフォルダに保存                    │
│   ○ 指定フォルダに保存: [______] [参照...]    │
├─────────────────────────────────────────────┤
│  ファイル 1/2: sample1.pdf - ページ 3/10...   │  ← ⑤ 進捗表示
│  ▓▓▓▓▓▓▓░░░░░░░░░░                            │
├─────────────────────────────────────────────┤
│  [    OCR処理を開始    ]  [ 停止 ]            │  ← ⑥ 実行ボタン
└─────────────────────────────────────────────┘
```

### 操作の流れ

1. **① ドロップ** または **② ボタン** でPDFを追加する
   - フォルダを指定すると、その中の全PDFが自動で登録されます
2. **④ 保存先** を選ぶ（通常は「PDFと同じフォルダ」でOK）
3. **⑥「OCR処理を開始」** を押す
4. **⑤ 進捗** を見ながら待つ（途中で止めたい場合は「停止」）
5. 完了すると **保存先を知らせるダイアログ** が表示されます
   - 「はい」を押すと保存先フォルダが開きます

---

## 7. よくあるトラブルと解決法

### 7-1. 「スクリプトを実行できません」（署名エラー）

PowerShellで `.ps1` を実行した際に、`デジタル署名されていません` と出る場合：

```powershell
powershell -ExecutionPolicy Bypass -File .\check_windows_environment.ps1
```

このように `-ExecutionPolicy Bypass` を付けて実行してください。

### 7-2. 「No such file or directory」（ファイルが見つからない）

実行しようとしたフォルダにファイルが無い状態です。`dir` で確認し、正しいフォルダへ `cd` で移動してください。

```powershell
dir pdf2ocr_gui.py    # 表示されればOK
```

### 7-3. バッチ実行時に文字化け・コマンドエラー

`'m' is not recognized...` のようなエラーが出る場合、バッチファイルが壊れています。
最新版を取得し直してください（古いファイルは削除してから）。

```powershell
Remove-Item .\build_exe.bat
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/quasrg-design/PDF2OCR/main/build_exe.bat" -OutFile ".\build_exe.bat"
```

それでも不安な場合は[5章の手動ビルド](#バッチがうまく動かない場合手動ビルド)を使ってください。

### 7-4. Tesseract が PATH に通っていない（WARN）

環境チェックで `[WARN] PATH` が出ても、**本アプリは自動検出するため動作します**。
コマンドラインで `tesseract` を直接使いたい場合のみ、PATHを追加してください。

```powershell
[System.Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\Program Files\Tesseract-OCR", "User")
```

（設定後、PowerShellを開き直してください）

### 7-5. 起動時に「Tesseract が見つかりません」ダイアログが出る

アプリ起動直後に以下のダイアログが表示された場合、Tesseract-OCR が未インストールです。

```
【入手先】
https://github.com/UB-Mannheim/tesseract/wiki

【インストール手順】
1. 上記URLからインストーラをダウンロード
2. インストール時の言語選択で「Japanese」を必ずチェック
3. インストール完了後、アプリを再起動してください。
```

ダイアログの手順に従ってインストール後、アプリを再起動してください。

> 💡 アプリは `C:\Program Files\Tesseract-OCR` など標準的なインストール先を自動検出します。
> PATH の設定は不要です。

### 7-6. 起動時に「Poppler が見つかりません」ダイアログが出る

アプリ起動時に以下のダイアログが表示された場合、Poppler が未インストールまたは PATH が未設定です。

```
PDF→画像変換に必要な Poppler がインストールされていないか、
PATH が通っていません。

【入手先】
https://github.com/oschwartz10612/poppler-windows/releases

【インストール手順】
1. Release-xx.xx.x-0.zip をダウンロード
2. 任意のフォルダに解凍
3. 解凍フォルダ内の「Library\bin」を環境変数 PATH に追加

設定後、アプリを再起動してください。
```

**具体的な PATH の設定方法：**

1. 解凍先（例: `C:\poppler\Library\bin`）を確認する
2. PowerShell で以下を実行する
   ```powershell
   [System.Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\poppler\Library\bin", "User")
   ```
3. PowerShell を開き直してアプリを再起動する

> 💡 `winget install oschwartz10612.Poppler` でもインストールできます（自動でPATH設定されます）。

### 7-7. ドラッグ＆ドロップができない

`tkinterdnd2` が未インストールです。次を実行してください（ボタン操作は無くても可能です）。

```powershell
pip install tkinterdnd2
```

### 7-8. 日本語が認識されない / 文字化けする

Tesseractの日本語パックが入っていません。インストーラを再実行し「Japanese」を選択してください。

---

## 8. 仕様一覧

| 項目 | 内容 |
|------|------|
| 対応OS | Windows 10 / 11 |
| 入力 | PDFファイル（複数可）、フォルダ |
| 出力 | テキストファイル（.txt、UTF-8） |
| OCR解像度 | DPI 300（高精度） |
| 認識言語 | 日本語＋英語（jpn+eng） |
| 処理方式 | 1ページずつ変換・OCR（メモリ節約） |
| 中断 | 「停止」ボタンで可能 |
| 保存先 | PDFと同じフォルダ／指定フォルダ |
| 依存ソフト | Tesseract-OCR、Poppler |
| 依存パッケージ | pytesseract, pillow, pdf2image, tkinterdnd2(任意) |

---

---

## 9. よくある質問（Q&A）

### Q1. exe を実行しても何も起動しない

**A.** ウイルス対策ソフトが実行をブロックしている可能性があります。
以下を確認してください：

1. タスクバーのウイルス対策アイコンを右クリック →「一時的に無効化」を試す
2. それでも起動しない場合は Python 版（`python pdf2ocr_gui.py`）を使用してください

### Q2. 起動するたびに「Tesseract が見つかりません」が出る

**A.** Tesseract-OCR が正しくインストールされていません。
インストーラで「Japanese」言語を選択して再インストールしてください。

> ※ アプリは `C:\Program Files\Tesseract-OCR` を自動検出します。PATH 設定は不要です。

### Q3. 起動するたびに「Poppler が見つかりません」が出る

**A.** Poppler の PATH が通っていません。以下のどちらかで対処してください：

**方法A: winget でインストール（自動でPATH設定）**
```powershell
winget install oschwartz10612.Poppler
```

**方法B: 手動で PATH を追加**
```powershell
[System.Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\poppler\Library\bin", "User")
```
（`C:\poppler\Library\bin` は実際の解凍先パスに合わせてください）

設定後、PowerShell を開き直してアプリを再起動してください。

### Q4. OCR結果のテキストが文字化けしている

**A.** 以下の原因が考えられます：

| 原因 | 対処 |
|------|------|
| 日本語パックが未インストール | Tesseract インストーラで「Japanese」を選択して再インストール |
| スキャン画像の解像度が低い | 元のスキャン設定を300dpi以上に変更して再スキャン |
| 手書き文字が含まれている | Tesseract は手書きには対応していません |

### Q5. 処理が途中で止まる / エラーになる

**A.** エラーダイアログに表示されるメッセージを確認してください。
「停止」ボタンで中断した場合は、そこまでの結果が保存されています。

### Q6. 複数のPDFをまとめて処理できますか？

**A.** できます。2通りの方法があります：
- **ファイルを複数選択**：「PDFファイルを選択」ボタンでCtrlキーを押しながら複数選択
- **フォルダを指定**：「フォルダを選択」でフォルダを指定すると、その中の全PDFを自動登録

### Q7. 保存先のテキストファイルはどこに作られますか？

**A.** デフォルトでは「PDFと同じフォルダ」に `ファイル名.txt` として保存されます。
「保存先」欄で「指定フォルダに保存」を選ぶと、任意の場所に変更できます。

### Q8. exeファイルを別のPCで使えますか？

**A.** PDF2OCR.exe 自体はコピーするだけで動きますが、実行するPCに以下が必要です：

- **Tesseract-OCR**（日本語パック付き）
- **Poppler**

Python のインストールは不要です。

### Q9. 環境チェックスクリプトを実行すると「スクリプトを実行できません」と出る

**A.** PowerShell のセキュリティポリシーによるものです。以下のように実行してください：

```powershell
powershell -ExecutionPolicy Bypass -File .\check_windows_environment.ps1
```

### Q10. OCR の精度を上げたい

**A.** 以下を試してください：

1. **元のPDFをより高解像度でスキャンする**（300dpi以上推奨）
2. **スキャン時に白黒やグレースケールで保存する**（カラーより文字認識が安定）
3. **傾きのないスキャンにする**（斜めスキャンは認識率が下がります）

---

## 関連ドキュメント

- **README.md** … プロジェクト全体の概要
- **check_windows_environment.ps1** … 環境チェックスクリプト
- **Pytesseract_Complete_Guide.docx** … OCRの詳細解説
- **pytesseract_cheatsheet.py** … コードのクイックリファレンス

ご不明点があれば、各ドキュメントもあわせてご参照ください。
