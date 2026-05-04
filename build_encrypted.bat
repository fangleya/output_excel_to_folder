chcp 65001 >nul
@echo off
title Excel导出工具 - 加密单文件打包
echo ========================================
echo   Excel导出工具 - 加密单文件打包
echo   Cython加密 + PyInstaller单文件
echo ========================================
echo.
:: 激活 conda 环境（如果尚未激活）
echo [0] 激活 conda 环境...
call conda activate env_python310 2>nul
if errorlevel 1 (
    echo [警告] conda activate 失败，尝试继续...
)
echo.
echo [启动] 运行打包脚本...
echo.
python build_encrypted.py