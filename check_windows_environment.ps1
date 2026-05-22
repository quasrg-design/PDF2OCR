# =====================================================================
# PDF2OCR - Windows環境チェックスクリプト
# =====================================================================
# 用途: Pytesseract / PDF2OCR を実行するために必要な
#       Windowsプログラム類がインストールされているかを確認します
#
# Version: v1.1.0
# Last Updated: 2026-05-22
#
# 実行方法:
#   PowerShellを起動し、以下のコマンドを実行してください
#     powershell -ExecutionPolicy Bypass -File .\check_windows_environment.ps1
# =====================================================================

# 文字化け対策（コンソールをUTF-8に）
try {
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    $OutputEncoding            = [System.Text.Encoding]::UTF8
} catch {}

# ---------------------------------------------------------------------
# 表示用ヘルパー関数
# ---------------------------------------------------------------------
function Write-Header {
    param([string]$Text)
    Write-Host ""
    Write-Host ("=" * 70) -ForegroundColor Cyan
    Write-Host $Text -ForegroundColor Cyan
    Write-Host ("=" * 70) -ForegroundColor Cyan
}

function Write-Section {
    param([string]$Text)
    Write-Host ""
    Write-Host ("-" * 70) -ForegroundColor DarkCyan
    Write-Host $Text -ForegroundColor Yellow
    Write-Host ("-" * 70) -ForegroundColor DarkCyan
}

function Write-OK {
    param([string]$Name, [string]$Detail = "")
    if ($Detail) {
        Write-Host ("  [OK]    {0,-25} {1}" -f $Name, $Detail) -ForegroundColor Green
    } else {
        Write-Host ("  [OK]    {0}" -f $Name) -ForegroundColor Green
    }
}

function Write-NG {
    param([string]$Name, [string]$Detail = "")
    if ($Detail) {
        Write-Host ("  [NG]    {0,-25} {1}" -f $Name, $Detail) -ForegroundColor Red
    } else {
        Write-Host ("  [NG]    {0}" -f $Name) -ForegroundColor Red
    }
}

function Write-Warn {
    param([string]$Name, [string]$Detail = "")
    if ($Detail) {
        Write-Host ("  [WARN]  {0,-25} {1}" -f $Name, $Detail) -ForegroundColor Yellow
    } else {
        Write-Host ("  [WARN]  {0}" -f $Name) -ForegroundColor Yellow
    }
}

function Write-Info {
    param([string]$Name, [string]$Detail = "")
    Write-Host ("  [INFO]  {0,-25} {1}" -f $Name, $Detail) -ForegroundColor White
}

# ---------------------------------------------------------------------
# 集計用カウンタ
# ---------------------------------------------------------------------
$script:okCount   = 0
$script:ngCount   = 0
$script:warnCount = 0
$script:missing   = New-Object System.Collections.ArrayList

function Add-Result {
    param([string]$Status, [string]$Name, [string]$Hint = "")
    switch ($Status) {
        "OK"   { $script:okCount++ }
        "NG"   { $script:ngCount++;   [void]$script:missing.Add(@{ Name = $Name; Hint = $Hint }) }
        "WARN" { $script:warnCount++; [void]$script:missing.Add(@{ Name = $Name; Hint = $Hint }) }
    }
}

# ---------------------------------------------------------------------
# 0. ヘッダー情報
# ---------------------------------------------------------------------
Write-Header "PDF2OCR - Windows環境チェック"

$checkDate    = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$computerName = $env:COMPUTERNAME
$userName     = $env:USERNAME
$userDomain   = $env:USERDOMAIN

Write-Host ""
Write-Host "  確認日       : $checkDate"
Write-Host "  コンピュータ名 : $computerName"
Write-Host "  ユーザー名   : $userName"
if ($userDomain) {
    Write-Host "  ドメイン     : $userDomain"
}

# ---------------------------------------------------------------------
# 1. OS / PowerShell 情報
# ---------------------------------------------------------------------
Write-Section "1. OS / PowerShell 情報"

try {
    $os = Get-CimInstance -ClassName Win32_OperatingSystem -ErrorAction Stop
    Write-Info "OS"           ("{0} ({1})" -f $os.Caption, $os.Version)
    Write-Info "アーキテクチャ" $os.OSArchitecture
} catch {
    Write-Warn "OS情報" "取得できませんでした"
}

Write-Info "PowerShell"   $PSVersionTable.PSVersion.ToString()
Write-Info "実行ポリシー" (Get-ExecutionPolicy).ToString()

# ---------------------------------------------------------------------
# 2. Python のチェック
# ---------------------------------------------------------------------
Write-Section "2. Python"

$pythonCmd = $null
foreach ($cmd in @("python", "python3", "py")) {
    $found = Get-Command $cmd -ErrorAction SilentlyContinue
    if ($found) { $pythonCmd = $cmd; break }
}

if ($pythonCmd) {
    try {
        $pyVersion = & $pythonCmd --version 2>&1
        Write-OK "Python" "$pyVersion (コマンド: $pythonCmd)"
        Add-Result "OK" "Python"
    } catch {
        Write-NG "Python" "コマンドは見つかりましたが実行に失敗しました"
        Add-Result "NG" "Python" "https://www.python.org/downloads/ から再インストールしてください"
    }
} else {
    Write-NG "Python" "インストールされていません"
    Add-Result "NG" "Python" "https://www.python.org/downloads/ からダウンロードしてください（バージョン3.8以上推奨）"
}

# pip
if ($pythonCmd) {
    try {
        $pipVersion = & $pythonCmd -m pip --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-OK "pip" $pipVersion
            Add-Result "OK" "pip"
        } else {
            Write-NG "pip" "利用できません"
            Add-Result "NG" "pip" "python -m ensurepip --upgrade を実行してください"
        }
    } catch {
        Write-NG "pip" "利用できません"
        Add-Result "NG" "pip" "python -m ensurepip --upgrade を実行してください"
    }
} else {
    Write-Warn "pip" "Pythonが無いためスキップ"
}

# ---------------------------------------------------------------------
# 3. Python パッケージのチェック
# ---------------------------------------------------------------------
Write-Section "3. Python パッケージ"

$requiredPackages = @(
    @{ Name = "pytesseract"; Import = "pytesseract"; Hint = "pip install pytesseract" },
    @{ Name = "Pillow";      Import = "PIL";         Hint = "pip install pillow" },
    @{ Name = "pdf2image";   Import = "pdf2image";   Hint = "pip install pdf2image" }
)

if ($pythonCmd) {
    foreach ($pkg in $requiredPackages) {
        $checkCode = "import importlib, sys; " +
                     "spec = importlib.util.find_spec('$($pkg.Import)'); " +
                     "sys.exit(0 if spec else 1)"
        & $pythonCmd -c $checkCode 2>$null
        if ($LASTEXITCODE -eq 0) {
            $verCode = "import $($pkg.Import) as m; " +
                       "print(getattr(m, '__version__', 'unknown'))"
            $ver = & $pythonCmd -c $verCode 2>$null
            Write-OK $pkg.Name "v$ver"
            Add-Result "OK" $pkg.Name
        } else {
            Write-NG $pkg.Name "未インストール"
            Add-Result "NG" $pkg.Name $pkg.Hint
        }
    }
} else {
    foreach ($pkg in $requiredPackages) {
        Write-Warn $pkg.Name "Pythonが無いためスキップ"
        Add-Result "WARN" $pkg.Name $pkg.Hint
    }
}

# ---------------------------------------------------------------------
# 4. Tesseract-OCR のチェック
# ---------------------------------------------------------------------
Write-Section "4. Tesseract-OCR"

$tesseractCmd = Get-Command tesseract -ErrorAction SilentlyContinue
$tesseractPath = $null

if ($tesseractCmd) {
    $tesseractPath = $tesseractCmd.Source
} else {
    # 既定のインストール先を順番に確認
    $candidatePaths = @(
        "C:\Program Files\Tesseract-OCR\tesseract.exe",
        "C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        "$env:LOCALAPPDATA\Programs\Tesseract-OCR\tesseract.exe",
        "$env:USERPROFILE\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
    )
    foreach ($p in $candidatePaths) {
        if (Test-Path $p) { $tesseractPath = $p; break }
    }
}

if ($tesseractPath) {
    Write-OK "Tesseract" "見つかりました: $tesseractPath"
    Add-Result "OK" "Tesseract-OCR"

    try {
        $tessVerOutput = & $tesseractPath --version 2>&1
        $tessVer = ($tessVerOutput | Select-Object -First 1).ToString()
        Write-Info "バージョン" $tessVer
    } catch {
        Write-Warn "バージョン" "取得できませんでした"
    }

    # PATH に通っているか
    if (-not $tesseractCmd) {
        Write-Warn "PATH" "tesseract.exe にPATHが通っていません（Python側で tesseract_cmd の指定が必要）"
        Add-Result "WARN" "Tesseract PATH" "システム環境変数のPATHに `"$([System.IO.Path]::GetDirectoryName($tesseractPath))`" を追加してください"
    }

    # 言語パック (jpn / eng)
    $tessDir = Split-Path $tesseractPath -Parent
    $tessdataDir = Join-Path $tessDir "tessdata"
    if (Test-Path $tessdataDir) {
        $hasJpn = Test-Path (Join-Path $tessdataDir "jpn.traineddata")
        $hasEng = Test-Path (Join-Path $tessdataDir "eng.traineddata")

        if ($hasEng) {
            Write-OK "言語パック (eng)"
            Add-Result "OK" "言語パック (eng)"
        } else {
            Write-NG "言語パック (eng)" "未インストール"
            Add-Result "NG" "言語パック (eng)" "Tesseractインストーラの追加コンポーネントから 'English' を選択してください"
        }

        if ($hasJpn) {
            Write-OK "言語パック (jpn)"
            Add-Result "OK" "言語パック (jpn)"
        } else {
            Write-NG "言語パック (jpn)" "未インストール"
            Add-Result "NG" "言語パック (jpn)" "Tesseractインストーラの追加コンポーネントから 'Japanese' を選択してください"
        }

        # インストール済み言語の一覧表示
        try {
            $langs = & $tesseractPath --list-langs 2>&1 | Where-Object { $_ -and ($_ -notmatch "List of available languages") }
            if ($langs) {
                Write-Info "利用可能な言語" ($langs -join ", ")
            }
        } catch {}
    } else {
        Write-Warn "tessdata" "ディレクトリが見つかりません: $tessdataDir"
        Add-Result "WARN" "tessdata" "Tesseractを再インストールしてください"
    }
} else {
    Write-NG "Tesseract" "インストールされていません"
    Add-Result "NG" "Tesseract-OCR" "https://github.com/UB-Mannheim/tesseract/wiki からインストーラを取得し、'Japanese' 言語を選択してインストールしてください"
}

# ---------------------------------------------------------------------
# 5. Poppler のチェック（pdf2image が依存）
# ---------------------------------------------------------------------
Write-Section "5. Poppler (pdf2image が利用)"

$popplerCmd = Get-Command pdftoppm -ErrorAction SilentlyContinue
if ($popplerCmd) {
    try {
        $popplerVerOutput = & pdftoppm -v 2>&1
        $popplerVer = ($popplerVerOutput | Select-Object -First 1).ToString()
        Write-OK "Poppler" "$popplerVer ($($popplerCmd.Source))"
        Add-Result "OK" "Poppler"
    } catch {
        Write-OK "Poppler" $popplerCmd.Source
        Add-Result "OK" "Poppler"
    }
} else {
    Write-NG "Poppler" "pdftoppm が見つかりません（PATH未設定の可能性）"
    Add-Result "NG" "Poppler" "https://github.com/oschwartz10612/poppler-windows/releases からダウンロードし、bin フォルダにPATHを通してください"
}

# ---------------------------------------------------------------------
# 6. サマリ
# ---------------------------------------------------------------------
Write-Section "サマリ"

Write-Host ""
Write-Host ("  OK    : {0}" -f $script:okCount)   -ForegroundColor Green
Write-Host ("  NG    : {0}" -f $script:ngCount)   -ForegroundColor Red
Write-Host ("  WARN  : {0}" -f $script:warnCount) -ForegroundColor Yellow
Write-Host ""

if ($script:ngCount -eq 0 -and $script:warnCount -eq 0) {
    Write-Host "  すべて揃っています。PDF2OCR をすぐに利用できます。" -ForegroundColor Green
} else {
    Write-Host "  対応が必要な項目:" -ForegroundColor Yellow
    Write-Host ""
    $i = 1
    foreach ($item in $script:missing) {
        Write-Host ("    {0}. {1}" -f $i, $item.Name) -ForegroundColor Yellow
        if ($item.Hint) {
            Write-Host ("       => {0}" -f $item.Hint) -ForegroundColor Gray
        }
        $i++
    }
}

Write-Host ""
Write-Host ("=" * 70) -ForegroundColor Cyan
Write-Host ("  確認日: {0}   /   {1}\{2}" -f $checkDate, $computerName, $userName) -ForegroundColor Cyan
Write-Host ("=" * 70) -ForegroundColor Cyan
Write-Host ""

# 終了コード: NGが1件でもあれば 1
if ($script:ngCount -gt 0) { exit 1 } else { exit 0 }
