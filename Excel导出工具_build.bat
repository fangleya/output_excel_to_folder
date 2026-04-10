@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
title Excel导出工具 - 一键加密打包脚本

:: ========================== 配置区域（请根据你的环境修改） ==========================
:: 1. 选择虚拟环境类型：conda 或 venv
set ENV_TYPE=conda

:: 2. 如果 ENV_TYPE=conda，请填写你的 Anaconda 虚拟环境名称（例如：base, py39, qt_dev 等）
set CONDA_ENV_NAME=env_python310

:: 3. 如果 ENV_TYPE=venv，请填写 venv 目录名称（通常为 venv）
set VENV_DIR=venv

:: 4. 其他配置
set SPEC_FILE=Excel导出工具.spec
set BACKUP_DIR=src_backup_%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set BACKUP_DIR=%BACKUP_DIR: =0%
:: ==============================================================================

echo ========================================================
echo     Excel导出工具 - Cython+PyInstaller 一键打包
echo     虚拟环境类型：if "%ENV_TYPE%"=="conda" ( %CONDA_ENV_NAME% ) else ( %VENV_DIR% )
echo ========================================================
echo.

:: -------------------------- 1. 检查并激活虚拟环境 --------------------------
echo [1/7] 检查并激活虚拟环境...

if /i "%ENV_TYPE%"=="conda" (
    echo    模式：Anaconda 虚拟环境
    echo    环境名称：%CONDA_ENV_NAME%

    :: 检查 conda 是否可用
    where conda >nul 2>&1
    if errorlevel 1 (
        echo ❌ 错误：未找到 conda 命令
        echo 请确认：1. 已安装 Anaconda/Miniconda 2. 已将 conda 加入系统 PATH
        pause
        exit /b 1
    )

    :: 尝试激活 conda 环境
    echo    正在激活环境...
    :: 方法1：尝试使用 conda activate（需要 conda init 配置过）
    call conda activate "%CONDA_ENV_NAME%" 2>nul
    if errorlevel 1 (
        :: 方法2：如果方法1失败，尝试使用 activate.bat 直接激活（兼容旧版 Anaconda）
        :: 查找 Anaconda 安装路径
        for /f "delims=" %%i in ('where conda') do set CONDA_PATH=%%i
        :: 去掉 Scripts\conda.exe 获取根目录
        set CONDA_ROOT=!CONDA_PATH:Scripts\conda.exe=!
        if exist "!CONDA_ROOT!Scripts\activate.bat" (
            call "!CONDA_ROOT!Scripts\activate.bat" "%CONDA_ENV_NAME%"
        ) else (
            echo ❌ 错误：无法激活 conda 环境 "%CONDA_ENV_NAME%"
            echo 请尝试：1. 打开 Anaconda Prompt 手动激活环境 2. 运行 conda init cmd.exe 初始化
            pause
            exit /b 1
        )
    )

    :: 验证环境是否激活成功（检查 python 路径是否包含环境名）
    python -c "import sys; print(sys.executable)" | findstr /i "%CONDA_ENV_NAME%" >nul
    if errorlevel 1 (
        echo ⚠️  警告：环境激活验证可能失败，请确认后续步骤正常
        echo    当前 Python 路径：
        python -c "import sys; print(sys.executable)"
    ) else (
        echo ✅ Anaconda 虚拟环境 "%CONDA_ENV_NAME%" 激活成功
    )

) else if /i "%ENV_TYPE%"=="venv" (
    echo    模式：标准 venv 虚拟环境
    if not exist "%VENV_DIR%\Scripts\activate.bat" (
        echo ❌ 错误：未找到虚拟环境 "%VENV_DIR%"
        pause
        exit /b 1
    )
    call "%VENV_DIR%\Scripts\activate.bat"
    echo ✅ venv 虚拟环境激活成功
) else (
    echo ❌ 错误：未知的 ENV_TYPE：%ENV_TYPE%，请选择 conda 或 venv
    pause
    exit /b 1
)
echo.

:: -------------------------- 2. 验证依赖是否安装 --------------------------
echo [2/7] 验证核心依赖...
python -c "import PySide6, Cython, PyInstaller" 2>nul
if errorlevel 1 (
    echo ❌ 错误：核心依赖未完全安装
    echo 请在激活的环境中执行：pip install -r requirements.txt
    pause
    exit /b 1
)
echo ✅ 依赖检查通过
echo.

:: -------------------------- 3. 备份源代码 --------------------------
echo [3/7] 备份源代码到 "%BACKUP_DIR%"...
if exist "src" (
    xcopy "src" "%BACKUP_DIR%\src\" /E /I /Y >nul
    if errorlevel 1 (
        echo ⚠️  警告：源码备份失败，但继续执行
    ) else (
        echo ✅ 源码备份成功
    )
) else (
    echo ❌ 错误：未找到 src 目录
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
python cython_setup.py build_ext --inplace
if errorlevel 1 (
    echo ❌ 错误：Cython 编译失败
    echo 请检查：1. 是否安装了 MSVC 编译器 2. Python 版本是否兼容
    pause
    exit /b 1
)
echo ✅ Cython 加密成功
echo.

:: -------------------------- 5. 清理中间文件 --------------------------
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
pyinstaller --clean "%SPEC_FILE%"
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