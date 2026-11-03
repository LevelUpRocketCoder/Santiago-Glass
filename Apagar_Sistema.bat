@echo off
title Apagando Santiago Glass
echo ==========================================
echo    Cerrando el sistema Santiago Glass...
echo ==========================================
echo.
FOR /F "tokens=5" %%T IN ('netstat -a -n -o ^| findstr :8000') DO (
    taskkill /F /PID %%T >nul 2>&1
)
echo Sistema cerrado correctamente.
timeout /t 3 >nul
