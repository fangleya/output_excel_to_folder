@echo off
chcp 65001 >nul
title Excel导出工具 - 一键加密打包脚本

:: ========================== 配置区域（可根据需要修改） ==========================
set VENV_DIR=venv
set SPEC_FILE=Excel导出工具.spec
set BACKUP_DIR=src_backup_%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set BACKUP_DIR=%BACKUP_DIR: =0%
:: ==============================================================================

echo ========================================================
echo     Excel导出工具 - Cython+PyInstaller 一键打包
echo ========================================================
echo.

:: -------------------------- 1. 检查虚拟环境 --------------------------
echo [1/7] 检查虚拟环境...
if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo ❌ 错误：未找到虚拟环境 "%VENV_DIR%"
    echo 请先在项目根目录执行：python -m venv %VENV_DIR%
    echo 并安装依赖：pip install -r requirements.txt
    pause
    exit /b 1
)
echo ✅ 虚拟环境检查通过
echo.

:: -------------------------- 2. 激活虚拟环境 --------------------------
echo [2/7] 激活虚拟环境...
call "%VENV_DIR%\Scripts\activate.bat"
if errorlevel 1 (
    echo ❌ 错误：虚拟环境激活失败
    pause
    exit /b 1
)
echo ✅ 虚拟环境激活成功
echo.

:: -------------------------- 3. 备份源代码（防止编译失败丢失） --------------------------
echo [3/7] 备份源代码到 "%BACKUP_DIR%"...
if exist "src" (
    xcopy "src" "%BACKUP_DIR%\src\" /E /I /Y >nul
    if errorlevel 1 (
        echo ⚠️  警告：源码备份失败，但继续执行（请手动备份）
    ) else (
        echo ✅ 源码备份成功
    )
) else (
    echo ❌ 错误：未找到 src 目录，请确认脚本在项目根目录运行
    pause
    exit /b 1
)
echo.

:: -------------------------- 4. Cython 编译加密 --------------------------
echo [4/7] 执行 Cython 核心代码加密编译...
if not exist "cython_setup.py" (
    echo ❌ 错误：未找到 cython_setup.py 编译脚本
    pause
    exit /b 1
)
python setup.py build_ext --inplace
if errorlevel 1 (
    echo ❌ 错误：Cython 编译失败
    echo 请检查：1. 是否安装了 MSVC 编译器 2. Python 版本是否兼容
    pause
    exit /b 1
)
echo ✅ Cython 编译成功
echo.

:: -------------------------- 5. 清理编译中间文件 --------------------------
echo [5/7] 清理编译中间文件...
:: 删除所有 .c 中间文件
del /s /q "*.c" >nul 2>&1
:: 删除 build 临时目录
if exist "build" rmdir /s /q "build"
:: 删除 setup.py 生成的 dist 目录（非最终打包目录）
if exist "cython_setup.py" if exist "dist" if not exist "%SPEC_FILE%" rmdir /s /q "dist"
echo ✅ 中间文件清理完成
echo.

:: -------------------------- 6. PyInstaller 打包 --------------------------
echo [6/7] 执行 PyInstaller 打包...
if not exist "%SPEC_FILE%" (
    echo ❌ 错误：未找到 spec 文件 "%SPEC_FILE%"
    echo 请先运行：pyi-makespec -w -n Excel导出工具 main.py
    echo 并按文档修改 spec 配置
    pause
    exit /b 1
)
pyinstaller "%SPEC_FILE%"
if errorlevel 1 (
    echo ❌ 错误：PyInstaller 打包失败
    pause
    exit /b 1
)
echo ✅ PyInstaller 打包成功
echo.

:: -------------------------- 7. 完成提示 --------------------------
echo ========================================================
echo     🎉 打包全部完成！
echo ========================================================
echo.
echo 📂 最终程序位置：
echo    %cd%\dist\Excel导出工具\
echo.
echo ⚠️  重要提示：
echo    1. 源码已备份到：%BACKUP_DIR%
echo    2. 请先测试打包后的程序功能正常，再删除备份
echo    3. 如需重新打包，请先从备份恢复 src 目录的 py 文件
echo.
:: 自动打开打包结果目录
explorer "%cd%\dist"
pause