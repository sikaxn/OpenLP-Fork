@echo off
setlocal
set "ROOT=%~dp0"
set "PYTHON_EXE=%ROOT%venv\Scripts\python.exe"
set "DIST_EXE=%ROOT%dist\OpenLP\OpenLP.exe"

if exist "%PYTHON_EXE%" (
    set "PYTHON_CMD=%PYTHON_EXE%"
) else (
    where python >nul 2>&1
    if errorlevel 1 (
        echo Python not found. Create venv or install Python first.
        goto :end
    )
    set "PYTHON_CMD=python"
)

"%PYTHON_CMD%" -m PyInstaller --version >nul 2>&1
if errorlevel 1 (
    echo PyInstaller is not installed for "%PYTHON_CMD%".
    echo Install it with: "%PYTHON_CMD%" -m pip install pyinstaller
    goto :end
)

if exist "%DIST_EXE%" (
    echo Checking for running dist OpenLP process...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "$distExe = '%DIST_EXE%'; Get-Process -Name OpenLP -ErrorAction SilentlyContinue | Where-Object { $_.Path -eq $distExe } | Stop-Process -Force"
)

echo Building OpenLP with PyInstaller...
"%PYTHON_CMD%" -m PyInstaller --noconfirm --clean "%ROOT%OpenLP.spec"
if errorlevel 1 (
    echo Build failed.
    echo If this is PermissionError on dist\OpenLP, close Explorer windows or terminals using that folder and retry.
    goto :end
)

echo.
echo Build complete: "%ROOT%dist\OpenLP\OpenLP.exe"

:end
echo.
pause
endlocal
