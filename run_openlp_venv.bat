@echo off
setlocal
set "ROOT=%~dp0"
"%ROOT%venv\Scripts\python.exe" "%ROOT%run_openlp.py" %*
endlocal
