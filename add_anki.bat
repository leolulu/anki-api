cd /d %~dp0
:retry
python main.py
if %errorlevel% neq 0 (
  echo Failed to run main.py. Retrying in one second...
  timeout /t 1 /nobreak >nul
  goto retry
)
pause