@echo off
setlocal
set "ROOT=%~dp0"
set "QT_OPENGL=software"
set "QTWEBENGINE_CHROMIUM_FLAGS=--disable-gpu --disable-gpu-compositing"
"%ROOT%venv\Scripts\python.exe" "%ROOT%run_openlp.py" %*
endlocal
