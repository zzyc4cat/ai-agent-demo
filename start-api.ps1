# 启动本地知识库 API（http://127.0.0.1:8000）
# 用法：右键“使用 PowerShell 运行”，或 .\start-api.ps1
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

$python = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    Write-Host "未找到 .venv，请先运行 .\start.ps1 初始化环境" -ForegroundColor Red
    exit 1
}

$env:PYTHONPATH = "src"
$env:PYTHONIOENCODING = "utf-8"
Write-Host "API 启动中：http://127.0.0.1:8000  （Ctrl+C 停止）" -ForegroundColor Green
& $python -m uvicorn api_server:app --app-dir src --host 127.0.0.1 --port 8000
