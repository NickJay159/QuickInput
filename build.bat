@echo off
setlocal
chcp 65001 >nul

echo 正在准备 QuickInput 构建环境...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo 依赖安装失败！
    pause
    exit /b 1
)

echo.
echo 开始编译...
python -m PyInstaller QuickInput.spec --clean --noconfirm
if errorlevel 1 (
    echo 编译失败！
    pause
    exit /b 1
)

if exist icon.png (
    copy icon.png dist\ >nul 2>&1
)

echo.
echo 编译成功：dist\QuickInput.exe
echo.
pause
