@echo off
rem Revert the 233 extra strings. The machine-translated part is reverted by the MT tool itself.
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\apply_extra.ps1" -Mode restore
echo.
echo To also revert the machine-translated text, either
echo   - run apocalyptic_translatorZ.exe again and use its BACKUP restore, or
echo   - Steam: Library ^> CONVRGENCE ^> Properties ^> Installed Files ^> Verify integrity
echo.
pause
