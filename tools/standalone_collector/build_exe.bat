@echo off
setlocal
chcp 65001 >nul 2>nul
echo ==================================================================
echo           正在打包 ArknightsCollector 独立单文件版 (.exe)
echo ==================================================================
echo.

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

where pyinstaller >nul 2>nul
if %errorlevel% neq 0 (
    echo [提示] 未找到 pyinstaller 命令，尝试从虚拟环境运行...
    set "PYINSTALLER_EXE=E:\miniconda3\envs\arknightsclip-test-pytest\Scripts\pyinstaller.exe"
) else (
    set "PYINSTALLER_EXE=pyinstaller"
)

"%PYINSTALLER_EXE%" --onefile --clean --name "ArknightsCollector" --distpath "dist" --workpath "build" --specpath "build" "collector.py"

if %errorlevel% equ 0 (
    echo.
    echo ==================================================================
    echo [OK] 打包成功！
    echo 可执行文件路径: %SCRIPT_DIR%dist\ArknightsCollector.exe
    echo ==================================================================
) else (
    echo [FAIL] 打包失败，请检查上方日志。
)

pause
endlocal
