@echo off
chcp 65001 >nul
setlocal

echo ============================================
echo  Live2D Cubism 5.3 - 一键破解安装脚本
echo ============================================
echo.

set "LIVE2D_DIR=D:\Live2D Cubism 5.3"
set "CRACK_DIR=%LIVE2D_DIR%\app\dll64_crack"
set "ORIG_DLL=%LIVE2D_DIR%\app\dll64\rlm1603.dll"
set "BAT_FILE=%LIVE2D_DIR%\CubismEditor5.bat"

:: 检查 Live2D 是否存在
if not exist "%ORIG_DLL%" (
    echo [!] 找不到 %ORIG_DLL%
    echo     请确认 Live2D Cubism 5.3 已安装到 %LIVE2D_DIR%
    pause
    exit /b 1
)

:: 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [!] 找不到 Python，请先安装 Python 3
    pause
    exit /b 1
)

echo [1/4] 创建影子目录...
if not exist "%CRACK_DIR%" mkdir "%CRACK_DIR%"

echo [2/4] 复制 DLL 到影子目录并打补丁...
copy /y "%ORIG_DLL%" "%CRACK_DIR%\rlm1603.dll" >nul
python "%~dp0patch_rlm_v6.py" "%CRACK_DIR%\rlm1603.dll"
if errorlevel 1 (
    echo [!] 补丁失败！
    pause
    exit /b 1
)

echo [3/4] 修改启动脚本 (添加影子目录到 NATIVE_PATH)...
:: 备份原始 bat
if not exist "%BAT_FILE%.bak" copy /y "%BAT_FILE%" "%BAT_FILE%.bak" >nul

:: 使用 PowerShell 做精确替换
powershell -Command "(Get-Content '%BAT_FILE%') -replace 'set NATIVE_PATH=app\\dll64;', 'set NATIVE_PATH=app\\dll64_crack;app\\dll64;' | Set-Content '%BAT_FILE%'"

echo [4/4] 完成！
echo.
echo ============================================
echo  安装成功！
echo ============================================
echo.
echo  - 影子 DLL:  %CRACK_DIR%\rlm1603.dll (已补丁)
echo  - 原版 DLL:  %ORIG_DLL% (未修改, 供哈希校验)
echo  - 启动脚本: %BAT_FILE% (已修改 NATIVE_PATH)
echo.
echo  注意: .lic 文件不需要修改，使用原版即可！
echo.
echo  现在可以运行 CubismEditor5.bat 启动软件。
echo  标题栏应显示 [试用版 剩余 9999 天]
echo.
pause
