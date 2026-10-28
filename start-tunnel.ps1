# 启动 Cloudflare Quick Tunnel（临时公网地址，重启会变）
# 前置：本机 API 已通过 .\start-api.ps1 启动在 8000 端口
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

$exe = Join-Path $root "tools\cloudflared.exe"
if (-not (Test-Path $exe)) {
    Write-Host "缺少 tools\cloudflared.exe，请先下载：" -ForegroundColor Red
    Write-Host "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
    exit 1
}

Write-Host "隧道启动中，稍后会在输出里看到 https://xxx.trycloudflare.com" -ForegroundColor Green
& $exe tunnel --url http://127.0.0.1:8000 --no-autoupdate
