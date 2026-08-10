@echo off
chcp 65001 > nul
echo ============================================================
echo   Kotyol ERP - Local POS Print Agent Auto-Installer v1.4
echo ============================================================
echo.

echo [1/3] Eski agent jarayonlari to'xtatilmoqda...
powershell -Command "$procs = Get-WmiObject Win32_Process | Where-Object { $_.CommandLine -like '*pos_printer_agent*' }; foreach ($p in $procs) { Stop-Process -Id $p.ProcessId -Force }" > nul 2>&1

echo [2/3] Avtozagruzka papkasiga saqlanmoqda...
set SCRIPT_DIR=%~dp0
set VBS_PATH=%SCRIPT_DIR%start_pos_agent_silent.vbs
copy "%VBS_PATH%" "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\" /Y > nul

echo [3/3] Yangi Print Agent v1.4 fonda ishga tushirilmoqda...
wscript "%VBS_PATH%"

echo.
echo ============================================================
echo [OK] Print Agent muvaffaqiyatli yangilandi va fonda ishga tushdi!
echo.
echo Endi kompyuteringizdagi termoprinter (XP-80C) ga ulandi.
echo Dasturdan chek chiqarish tugmasini bosib ko'rishingiz mumkin!
echo ============================================================
echo.
pause
