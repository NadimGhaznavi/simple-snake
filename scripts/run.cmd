@echo off
setlocal
set "APP_DIR=%~dp0.."
if exist "%APP_DIR%\.venv\Scripts\python.exe" goto run
rem A deployed copy with a missing runtime needs repair, not another installation.
if exist "%APP_DIR%\.installation-manifest.json" goto missing
set "APP_DIR=%LOCALAPPDATA%\Programs\SimpleSnake"
if not defined LOCALAPPDATA set "APP_DIR=%USERPROFILE%\AppData\Local\Programs\SimpleSnake"
if not exist "%APP_DIR%\.venv\Scripts\python.exe" goto missing

:run
pushd "%APP_DIR%" || exit /b 1
".venv\Scripts\python.exe" -B -m simplesnake %*
set "APP_EXIT=%ERRORLEVEL%"
popd
exit /b %APP_EXIT%

:missing
echo Simple Snake's Python runtime was not found in "%APP_DIR%\.venv". 1>&2
echo Run install.cmd from the source scripts folder, or follow the source setup instructions. 1>&2
echo For a custom installation directory, use its scripts\run.cmd. 1>&2
exit /b 1
