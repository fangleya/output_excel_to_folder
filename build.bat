:: build.bat - Windows 批处理一键打包
@echo off
chcp 65001 >nul
echo ========================================
echo      Excel数据清洗工具打包脚本
echo ========================================
echo.

:: 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python环境！
    echo 请确保Python已安装并添加到PATH环境变量
    pause
    exit /b 1
)

:: 检查项目结构
if not exist "src\main.py" (
    echo [错误] 找不到主程序文件 src\main.py
    echo 请确保在项目根目录运行此脚本
    pause
    exit /b 1
)

if not exist "resource\icon.ico" (
    echo [警告] 找不到图标文件 resource\icon.ico
)

:: 安装必要的依赖
echo [1/4] 正在检查并安装依赖包...
pip install PyInstaller>=5.9.0 --quiet
pip install xlwings>=0.29.1 --quiet
pip install openpyxl>=3.0.10 --quiet
pip install pandas>=1.5.0 --quiet
pip install numpy>=1.23.0 --quiet

:: 清理旧文件
echo [2/4] 正在清理旧的构建文件...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
for /r %%i in (__pycache__) do if exist %%i rmdir /s /q "%%i" 2>nul
del /q *.spec 2>nul

:: 执行打包
echo [3/4] 正在使用PyInstaller打包...
python build_simple.py

:: 完成提示
echo [4/4] 打包完成！
echo.
echo 生成的文件在 dist 目录中
echo 主要文件：dist\Excel数据清洗工具.exe
echo.
pause