@echo off
setlocal
set "ROOT=%~dp0"

if not exist "%ROOT%venv\Scripts\python.exe" (
    echo Virtual environment Python not found at "%ROOT%venv\Scripts\python.exe"
    goto :end
)

"%ROOT%venv\Scripts\python.exe" -m pytest %*

:end
echo.
pause
endlocal
