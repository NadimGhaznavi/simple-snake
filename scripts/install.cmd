@echo off
cd /d "%~dp0.."
python -B scripts\install.py install %*
