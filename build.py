# build.py
import os
import shutil
import subprocess
import sys


def build_project():
    """打包项目"""
    print("开始打包PySide6项目...")

    # 项目根目录
    project_root = os.path.dirname(os.path.abspath(__file__))

    # 1. 生成requirements.txt（如果还没有）
    requirements_path = os.path.join(project_root, "requirements.txt")
    if not os.path.exists(requirements_path):
        print("正在生成requirements.txt...")
        with open(requirements_path, "w", encoding="utf-8") as f:
            f.write(
                """PySide6>=6.5.0
                    xlwings>=0.29.1
                    openpyxl>=3.0.10
                    pandas>=1.5.0
                    numpy>=1.23.0
                    PyInstaller>=5.9.0"""
            )

    # 2. 检查spec文件是否存在
    spec_file = os.path.join(project_root, "build.spec")
    if not os.path.exists(spec_file):
        print("错误: 未找到build.spec文件")
        return False

    # 3. 创建输出目录
    output_dir = os.path.join(project_root, "dist")
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)

    # 4. 执行打包命令
    print("正在使用PyInstaller打包...")
    cmd = ["pyinstaller", "--clean", "--noconfirm", spec_file]  # 清理临时文件  # 覆盖输出目录不提示

    try:
        subprocess.run(cmd, check=True, cwd=project_root)
        print(f"打包完成！输出目录: {output_dir}")

        # 5. 复制README等文档到输出目录
        docs_to_copy = ["README.md", "README.en.md", "project_structure.md"]
        for doc in docs_to_copy:
            src = os.path.join(project_root, doc)
            if os.path.exists(src):
                shutil.copy2(src, output_dir)

        # 6. 创建便携版zip
        import zipfile

        zip_path = os.path.join(project_root, "Excel数据清洗工具_便携版.zip")
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, output_dir)
                    zipf.write(file_path, arcname)

        print(f"便携版已创建: {zip_path}")
        return True

    except subprocess.CalledProcessError as e:
        print(f"打包失败: {e}")
        return False
    except Exception as e:
        print(f"打包过程中出现错误: {e}")
        return False


if __name__ == "__main__":
    build_project()
