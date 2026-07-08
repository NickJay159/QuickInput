@echo off
setlocal
chcp 65001 >nul

set "APP_VERSION=1.1.0"
set "SETUP_EXE=dist\QuickInput-%APP_VERSION%-setup.exe"

echo Preparing QuickInput %APP_VERSION% release build...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo Dependency installation failed.
    exit /b 1
)

echo.
echo Building application EXE...
python -m PyInstaller QuickInput.spec --clean --noconfirm
if errorlevel 1 (
    echo Application EXE build failed.
    exit /b 1
)

if exist icon.png (
    copy icon.png dist\ >nul 2>&1
)

echo.
echo Finding Inno Setup compiler...
set "ISCC="
for /f "delims=" %%I in ('where iscc.exe 2^>nul') do (
    if not defined ISCC set "ISCC=%%I"
)
if not defined ISCC if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not defined ISCC if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
if not defined ISCC if exist "%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe" set "ISCC=%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"

if not defined ISCC (
    echo Inno Setup compiler was not found.
    echo Install it first: winget install --id JRSoftware.InnoSetup --exact
    exit /b 1
)

echo Using Inno Setup: %ISCC%
"%ISCC%" installer\QuickInput.iss
if errorlevel 1 (
    echo Installer build failed.
    exit /b 1
)

echo.
echo Release build completed:
echo   dist\QuickInput.exe
echo   %SETUP_EXE%
