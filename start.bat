@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo === 个人综合助手 · 一键启动 ===
python scripts\bootstrap.py
if errorlevel 1 (
  echo [错误] bootstrap 失败
  pause
  exit /b 1
)

echo [启动] streamlit run app.py
".venv\Scripts\streamlit.exe" run app.py
if errorlevel 1 (
  echo [错误] streamlit 退出异常
  pause
  exit /b 1
)
