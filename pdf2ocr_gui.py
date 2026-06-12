# -*- coding: utf-8 -*-
"""
PDF2OCR GUI アプリケーション
スキャンPDFをドラッグアンドドロップでテキスト化するWindows向けGUIツール

Version: v1.2.0
Last Updated: 2026-06-12

必要なもの:
  - Python パッケージ: pytesseract / pillow / pdf2image
      pip install pytesseract pillow pdf2image
  - ドラッグアンドドロップ対応（任意・推奨）:
      pip install tkinterdnd2
  - Tesseract-OCR（日本語言語パック付き）
  - Poppler（pdf2image が利用）

実行方法:
  python pdf2ocr_gui.py
"""

import os
import sys
import threading
import traceback
from pathlib import Path

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# ドラッグアンドドロップは tkinterdnd2 があれば有効化（無くても起動可能）
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False

import pytesseract
from pdf2image import convert_from_path, pdfinfo_from_path

APP_NAME = "PDF2OCR"
APP_VERSION = "v1.2.0"
OCR_DPI = 300            # 高精度設定
OCR_LANG = "jpn+eng"     # 日本語＋英語


# ----------------------------------------------------------------------
# Tesseract のセットアップ（Windows で PATH が無くても動くように）
# ----------------------------------------------------------------------
def setup_tesseract() -> bool:
    """Tesseract を検出して pytesseract に設定する。見つかれば True。"""
    try:
        pytesseract.get_tesseract_version()
        return True
    except Exception:
        pass

    if sys.platform == "win32":
        candidates = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\Tesseract-OCR\tesseract.exe"),
        ]
        for path in candidates:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                try:
                    pytesseract.get_tesseract_version()
                    return True
                except Exception:
                    continue
    return False


# ----------------------------------------------------------------------
# メインアプリケーション
# ----------------------------------------------------------------------
class Pdf2OcrApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_NAME} - スキャンPDFをテキスト化 ({APP_VERSION})")
        self.root.geometry("680x560")
        self.root.minsize(560, 480)

        self.pdf_files: list[Path] = []
        self.processing = False
        self.stop_requested = False
        self.output_results: list[Path] = []

        self._build_ui()

        if not setup_tesseract():
            messagebox.showerror(
                "Tesseract が見つかりません",
                "Tesseract-OCR がインストールされていないか、見つかりませんでした。\n\n"
                "https://github.com/UB-Mannheim/tesseract/wiki から\n"
                "インストーラをダウンロードし、「Japanese」言語を選択して\n"
                "インストールしてください。",
            )

    # ------------------------------------------------------------------
    # UI 構築
    # ------------------------------------------------------------------
    def _build_ui(self):
        pad = {"padx": 10, "pady": 5}

        # --- ドロップゾーン ---
        drop_text = (
            "ここに PDF ファイル / フォルダを\nドラッグ＆ドロップ"
            if DND_AVAILABLE
            else "（ドラッグ＆ドロップを使うには tkinterdnd2 をインストールしてください）\n"
                 "pip install tkinterdnd2"
        )
        self.drop_zone = tk.Label(
            self.root,
            text=drop_text,
            relief="ridge",
            borderwidth=2,
            height=4,
            bg="#eef5ff",
            fg="#33557a",
            font=("Meiryo UI", 11),
        )
        self.drop_zone.pack(fill="x", **pad)

        if DND_AVAILABLE:
            self.drop_zone.drop_target_register(DND_FILES)
            self.drop_zone.dnd_bind("<<Drop>>", self._on_drop)

        # --- ファイル選択ボタン列 ---
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(fill="x", **pad)

        tk.Button(btn_frame, text="PDFファイルを選択", command=self._select_files).pack(
            side="left", padx=(0, 5)
        )
        tk.Button(btn_frame, text="フォルダを選択", command=self._select_folder).pack(
            side="left", padx=5
        )
        tk.Button(btn_frame, text="リストをクリア", command=self._clear_list).pack(
            side="left", padx=5
        )

        # --- ファイルリスト ---
        list_frame = tk.LabelFrame(self.root, text="処理対象のPDF")
        list_frame.pack(fill="both", expand=True, **pad)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        self.file_listbox = tk.Listbox(
            list_frame, yscrollcommand=scrollbar.set, font=("Meiryo UI", 9)
        )
        self.file_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        scrollbar.config(command=self.file_listbox.yview)

        # --- 保存先設定 ---
        out_frame = tk.LabelFrame(self.root, text="保存先")
        out_frame.pack(fill="x", **pad)

        self.output_mode = tk.StringVar(value="same")
        tk.Radiobutton(
            out_frame,
            text="PDFと同じフォルダに保存（同名の .txt）",
            variable=self.output_mode,
            value="same",
        ).pack(anchor="w", padx=5)

        custom_row = tk.Frame(out_frame)
        custom_row.pack(fill="x", padx=5, pady=(0, 5))
        tk.Radiobutton(
            custom_row,
            text="指定フォルダに保存:",
            variable=self.output_mode,
            value="custom",
        ).pack(side="left")
        self.output_dir_var = tk.StringVar(value="")
        tk.Entry(custom_row, textvariable=self.output_dir_var).pack(
            side="left", fill="x", expand=True, padx=5
        )
        tk.Button(custom_row, text="参照...", command=self._select_output_dir).pack(
            side="left"
        )

        # --- 進捗表示 ---
        progress_frame = tk.Frame(self.root)
        progress_frame.pack(fill="x", **pad)

        self.progress_label = tk.Label(
            progress_frame, text="待機中", anchor="w", font=("Meiryo UI", 9)
        )
        self.progress_label.pack(fill="x")
        self.progress_bar = ttk.Progressbar(progress_frame, mode="determinate")
        self.progress_bar.pack(fill="x", pady=(2, 0))

        # --- 実行ボタン列 ---
        run_frame = tk.Frame(self.root)
        run_frame.pack(fill="x", **pad)

        self.run_button = tk.Button(
            run_frame,
            text="OCR処理を開始",
            command=self._start_processing,
            bg="#2e7d32",
            fg="white",
            font=("Meiryo UI", 10, "bold"),
            height=2,
        )
        self.run_button.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.stop_button = tk.Button(
            run_frame, text="停止", command=self._request_stop, state="disabled", height=2
        )
        self.stop_button.pack(side="left")

    # ------------------------------------------------------------------
    # ファイル追加系
    # ------------------------------------------------------------------
    def _on_drop(self, event):
        paths = self.root.tk.splitlist(event.data)
        self._add_paths(paths)

    def _select_files(self):
        paths = filedialog.askopenfilenames(
            title="PDFファイルを選択", filetypes=[("PDFファイル", "*.pdf")]
        )
        if paths:
            self._add_paths(paths)

    def _select_folder(self):
        folder = filedialog.askdirectory(title="PDFが入ったフォルダを選択")
        if folder:
            self._add_paths([folder])

    def _select_output_dir(self):
        folder = filedialog.askdirectory(title="保存先フォルダを選択")
        if folder:
            self.output_dir_var.set(folder)
            self.output_mode.set("custom")

    def _add_paths(self, paths):
        added = 0
        for raw in paths:
            p = Path(raw)
            if p.is_dir():
                for pdf in sorted(p.glob("*.pdf")):
                    added += self._add_single(pdf)
            elif p.suffix.lower() == ".pdf" and p.exists():
                added += self._add_single(p)
        if added == 0:
            messagebox.showinfo("情報", "追加できるPDFファイルがありませんでした。")
        self._refresh_listbox()

    def _add_single(self, path: Path) -> int:
        if path not in self.pdf_files:
            self.pdf_files.append(path)
            return 1
        return 0

    def _clear_list(self):
        if self.processing:
            return
        self.pdf_files.clear()
        self._refresh_listbox()

    def _refresh_listbox(self):
        self.file_listbox.delete(0, tk.END)
        for p in self.pdf_files:
            self.file_listbox.insert(tk.END, str(p))
        self._set_progress_text(f"{len(self.pdf_files)} 件のPDFが登録されています")

    # ------------------------------------------------------------------
    # 進捗表示（ワーカースレッドから安全に呼ぶ）
    # ------------------------------------------------------------------
    def _set_progress_text(self, text):
        self.root.after(0, lambda: self.progress_label.config(text=text))

    def _set_progress_value(self, value, maximum):
        def update():
            self.progress_bar.config(maximum=maximum, value=value)
        self.root.after(0, update)

    # ------------------------------------------------------------------
    # 処理本体
    # ------------------------------------------------------------------
    def _start_processing(self):
        if self.processing:
            return
        if not self.pdf_files:
            messagebox.showwarning("警告", "処理するPDFファイルを追加してください。")
            return
        if self.output_mode.get() == "custom":
            out_dir = self.output_dir_var.get().strip()
            if not out_dir or not Path(out_dir).is_dir():
                messagebox.showwarning("警告", "有効な保存先フォルダを指定してください。")
                return

        self.processing = True
        self.stop_requested = False
        self.output_results = []
        self.run_button.config(state="disabled")
        self.stop_button.config(state="normal")

        threading.Thread(target=self._worker, daemon=True).start()

    def _request_stop(self):
        self.stop_requested = True
        self._set_progress_text("停止要求を受け付けました。現在のページ処理後に停止します...")

    def _output_path_for(self, pdf_path: Path) -> Path:
        if self.output_mode.get() == "custom":
            out_dir = Path(self.output_dir_var.get().strip())
        else:
            out_dir = pdf_path.parent
        return out_dir / (pdf_path.stem + ".txt")

    def _worker(self):
        errors: list[str] = []
        total_files = len(self.pdf_files)

        try:
            for file_index, pdf_path in enumerate(self.pdf_files, start=1):
                if self.stop_requested:
                    break

                try:
                    info = pdfinfo_from_path(str(pdf_path))
                    total_pages = int(info.get("Pages", 0))
                except Exception as e:
                    errors.append(f"{pdf_path.name}: PDF情報の取得に失敗 ({e})")
                    continue

                if total_pages <= 0:
                    errors.append(f"{pdf_path.name}: ページ数を取得できませんでした")
                    continue

                texts: list[str] = []
                failed = False

                # メモリ節約のため1ページずつ変換してOCR
                for page in range(1, total_pages + 1):
                    if self.stop_requested:
                        break

                    self._set_progress_text(
                        f"ファイル {file_index}/{total_files}: {pdf_path.name} "
                        f"- ページ {page}/{total_pages} を処理中..."
                    )
                    self._set_progress_value(page - 1, total_pages)

                    try:
                        images = convert_from_path(
                            str(pdf_path), dpi=OCR_DPI,
                            first_page=page, last_page=page,
                        )
                        page_text = pytesseract.image_to_string(
                            images[0], lang=OCR_LANG
                        )
                        texts.append(f"--- ページ {page} ---\n{page_text}\n")
                    except Exception as e:
                        errors.append(f"{pdf_path.name} p.{page}: {e}")
                        failed = True
                        break

                    self._set_progress_value(page, total_pages)

                if self.stop_requested or failed:
                    if self.stop_requested:
                        break
                    continue

                # テキスト保存
                out_path = self._output_path_for(pdf_path)
                try:
                    out_path.write_text("".join(texts), encoding="utf-8")
                    self.output_results.append(out_path)
                except Exception as e:
                    errors.append(f"{pdf_path.name}: 保存に失敗 ({e})")

        except Exception:
            errors.append(traceback.format_exc())
        finally:
            self.root.after(0, lambda: self._on_finished(errors))

    # ------------------------------------------------------------------
    # 完了処理（保存先確認ダイアログ）
    # ------------------------------------------------------------------
    def _on_finished(self, errors: list[str]):
        self.processing = False
        self.run_button.config(state="normal")
        self.stop_button.config(state="disabled")

        done = len(self.output_results)
        if self.stop_requested:
            summary = f"停止しました（完了: {done} 件）"
        else:
            summary = f"処理が完了しました（成功: {done} 件 / エラー: {len(errors)} 件）"
        self._set_progress_text(summary)
        self.progress_bar.config(value=0)

        message_lines = [summary, ""]
        if self.output_results:
            message_lines.append("保存先:")
            for p in self.output_results:
                message_lines.append(f"  {p}")
        if errors:
            message_lines.append("")
            message_lines.append("エラー:")
            for e in errors[:10]:
                message_lines.append(f"  {e}")
            if len(errors) > 10:
                message_lines.append(f"  ...ほか {len(errors) - 10} 件")

        if self.output_results:
            message_lines.append("")
            message_lines.append("保存先フォルダを開きますか？")
            if messagebox.askyesno("処理完了 - 保存先の確認", "\n".join(message_lines)):
                folder = self.output_results[0].parent
                if sys.platform == "win32":
                    os.startfile(str(folder))  # noqa: S606 - ユーザー操作によるフォルダ表示
                else:
                    import subprocess
                    subprocess.Popen(["xdg-open", str(folder)])
        else:
            messagebox.showwarning("処理結果", "\n".join(message_lines))


# ----------------------------------------------------------------------
# エントリポイント
# ----------------------------------------------------------------------
def main():
    if DND_AVAILABLE:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()
    Pdf2OcrApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
