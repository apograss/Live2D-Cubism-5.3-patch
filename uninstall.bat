@echo off
chcp 65001 >nul
setlocal

echo ============================================
echo  Live2D Cubism 5.3 - 一键还原脚本
echo ============================================
echo.

set "LIVE2D_DIR=D:\Live2D Cubism 5.3"
set "CRACK_DIR=%LIVE2D_DIR%\app\dll64_crack"
set "BAT_FILE=%LIVE2D_DIR%\CubismEditor5.bat"

echo [1/2] 删除影子目录...
if exist "%CRACK_DIR%" rmdir /s /q "%CRACK_DIR%"

echo [2/2] 还原启动脚本...
if exist "%BAT_FILE%.bak" (
    copy /y "%BAT_FILE%.bak" "%BAT_FILE%" >nul
    del "%BAT_FILE%.bak"
)

echo.
echo  已还原为官方原版状态。
echo.
pause
