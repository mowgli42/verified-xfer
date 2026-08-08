@echo off
setlocal EnableExtensions
REM End-to-end local demo (LocalBackend) using four temporary folders.
REM Mirrors examples\local-demo.sh for Windows cmd.exe operators.

set "DEMO=%TEMP%\verified-xfer-demo-%RANDOM%%RANDOM%"
echo Demo root: %DEMO%

mkdir "%DEMO%\source" 2>nul
mkdir "%DEMO%\staging" 2>nul
mkdir "%DEMO%\results" 2>nul
mkdir "%DEMO%\retrieved" 2>nul
echo sample payload>"%DEMO%\source\payload.txt"
echo run: 42>"%DEMO%\source\meta.txt"

REM YAML with forward slashes (safer than backslashes in YAML)
set "DEMO_FWD=%DEMO:\=/%"
set "CFG=%DEMO%\config.yaml"
(
  echo backend: local
  echo source_dir: "%DEMO_FWD%/source"
  echo staging_dir: "%DEMO_FWD%/staging"
  echo results_dir: "%DEMO_FWD%/results"
  echo retrieve_to: "%DEMO_FWD%/retrieved"
) > "%CFG%"

set "WRAP=%~dp0verified-xfer.bat"

echo === STAGE (dry-run) ===
call "%WRAP%" stage -c "%CFG%" --dry-run
if errorlevel 1 exit /b 1

echo === STAGE ===
call "%WRAP%" stage -c "%CFG%"
if errorlevel 1 exit /b 1

echo === Simulate test producing results ===
echo PASS>"%DEMO%\results\test.log"
echo 42>"%DEMO%\results\answer.txt"

echo === RETRIEVE ===
call "%WRAP%" retrieve -c "%CFG%"
if errorlevel 1 exit /b 1

echo === Retrieved contents ===
dir /b "%DEMO%\retrieved"
type "%DEMO%\retrieved\test.log"

echo Demo complete.  Temp dir left at %DEMO% (remove manually).
exit /b 0
