# simple_build.py
import os
import sys
import PyInstaller.__main__


def build_project():
    """简化的打包脚本"""
    print("开始打包Excel数据清洗工具...")

    # 项目根目录
    project_root = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(project_root, "src")

    # PyInstaller参数
    pyinstaller_args = [
        "src/main.py",  # 主入口文件
        "--name=Excel数据清洗工具",
        "--windowed",  # 无控制台窗口
        "--onefile",  # 打包成单个exe
        f'--icon={os.path.join(project_root, "resource", "icon.ico")}',
        f'--add-data={os.path.join(project_root, "resource", "icon.ico")};resource',
        f'--add-data={os.path.join(src_dir, "cfg", "user_config.json")};src/cfg',
        f'--add-data={os.path.join(src_dir, "ui", "*.ui")};src/ui',
        f'--add-data={os.path.join(src_dir, "ui", "*.py")};src/ui',
        f'--add-data={os.path.join(src_dir, "file_list", "*.py")};src/file_list',
        f'--add-data={os.path.join(src_dir, "utils", "*.py")};src/utils',
        f'--add-data={os.path.join(src_dir, "core", "*.py")};src/core',
        "--hidden-import=PySide6",
        "--hidden-import=PySide6.QtCore",
        "--hidden-import=PySide6.QtGui",
        "--hidden-import=PySide6.QtWidgets",
        "--hidden-import=xlwings",
        "--hidden-import=openpyxl",
        "--hidden-import=pandas",
        "--hidden-import=numpy",
        "--clean",
        "--noconfirm",
    ]

    try:
        PyInstaller.__main__.run(pyinstaller_args)
        print("打包完成！")
        print(f"输出目录: {os.path.join(project_root, 'dist')}")
        return True
    except Exception as e:
        print(f"打包失败: {e}")
        return False


if __name__ == "__main__":
    build_project()
