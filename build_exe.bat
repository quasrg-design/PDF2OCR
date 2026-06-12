@echo off
rem =====================================================================
rem PDF2OCR GUI - Windows実行ファイル(.exe)ビルドスクリプト
rem
rem Version: v1.2.1
rem Last Updated: 2026-06-12
rem
rem 使い方:
rem   このファイルをダブルクリック、またはコマンドプロンプトで実行
rem   完了すると dist\PDF2OCR.exe が作成されます
rem
rem 注意:
rem   - exe化しても Tesseract-OCR と Poppler は別途インストールが必要です
rem   - 初回はパッケージのダウンロードに数分かかります
rem =====================================================================

echo ============================================
echo  PDF2OCR GUI - exe ビルド
echo ============================================
echo.

echo [1/3] 必要なパッケージをインストール中...
python -m pip install --upgrade pyinstaller tkinterdnd2 pytesseract pillow pdf2image
if errorlevel 1 goto :error

echo.
echo [2/3] exe をビルド中...
python -m PyInstaller --noconfirm --onefile --windowed --name PDF2OCR --collect-data tkinterdnd2 pdf2ocr_gui.py
if errorlevel 1 goto :error

echo.
echo [3/3] 完了！
echo.
echo   実行ファイル: dist\PDF2OCR.exe
echo.
echo   PDF2OCR.exe は単体で配布できますが、実行するPCには
echo   Tesseract-OCR と Poppler のインストールが必要です。
echo.
pause
exit /b 0

:error
echo.
echo エラーが発生しました。上記のメッセージを確認してください。
pause
exit /b 1
