@echo off
setlocal EnableExtensions
REM Windows wrapper — interactive by default when config exists.
REM   verified-xfer.bat              → menu (1 Stage / 2 Retrieve)
REM   verified-xfer.bat web          → browser UI
REM   verified-xfer.bat stage        → one-shot upload
REM   verified-xfer.bat retrieve -c D:\lab\config.yaml


set PYTHONUNBUFFERED=1

where py >nul 2>&1
if %ERRORLEVEL%==0 (
  py -3 -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
  if %ERRORLEVEL%==0 (
    py -3 -m verified_xfer %*
    exit /b %ERRORLEVEL%
  )
)

where python >nul 2>&1
if %ERRORLEVEL%==0 (
  python -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
  if %ERRORLEVEL%==0 (
    python -m verified_xfer %*
    exit /b %ERRORLEVEL%
  )
)

where python3 >nul 2>&1
if %ERRORLEVEL%==0 (
  python3 -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
  if %ERRORLEVEL%==0 (
    python3 -m verified_xfer %*
    exit /b %ERRORLEVEL%
  )
)

echo FAIL       ^| Python 3.10+ not found  -^> install Python and add it to PATH
exit /b 1
