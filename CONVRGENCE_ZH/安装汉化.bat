@echo off
rem CONVRGENCE Chinese patch - step 1 runs the MT engine, step 2 applies the human pass.
cd /d "%~dp0"
if not exist "CONVRGENCE.exe" goto wrongplace

echo [1/2] Starting apocalyptic_translatorZ. Follow its wizard, then close that window.
start "" /wait apocalyptic_translatorZ.exe
echo.
echo [2/2] Applying the hand-proofed pass (1549 DB overrides are already in place;
echo        this adds the 233 strings the MT tool cannot reach).
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\apply_extra.ps1" -Mode apply
echo.
echo Done. Read README.txt if anything was skipped.
pause
exit /b 0

:wrongplace
echo [ERROR] CONVRGENCE.exe not found here.
echo         Copy the whole contents of this package into the game root folder:
echo         ^<Steam library^>\steamapps\common\CONVRGENCE\
echo         then run this file again.
pause
exit /b 2
