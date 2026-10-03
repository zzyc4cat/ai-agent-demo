# 个人综合助手 · 本机一键启动（PowerShell）
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "=== 个人综合助手 · 一键启动 ==="
python scripts\bootstrap.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "[错误] bootstrap 失败" -ForegroundColor Red
    exit 1
}

Write-Host "[启动] streamlit run app.py"
& ".\.venv\Scripts\streamlit.exe" run app.py
