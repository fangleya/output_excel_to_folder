# -*- coding: utf-8 -*-
# pyqt6_excel_clean.spec

block_cipher = None

# 获取项目根目录
import os
import sys
# project_root = os.path.dirname(os.path.abspath(__file__))

# 获取项目根目录的替代方法（不使用 __file__）
# 方法1：使用当前工作目录（假设在项目根目录执行打包）
project_root = os.getcwd()

# 方法2：或者使用 spec 文件的环境变量（更可靠）
# project_root = os.path.dirname(os.path.abspath(SPECPATH))

src_dir = os.path.join(project_root, 'src')

# 递归获取所有需要包含的文件
def get_data_files(directory):
    data_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(('.py', '.ui', '.json', '.ico', '.md', '.txt', '.png', '.jpg')):
                full_path = os.path.join(root, file)
                # 计算相对路径
                rel_path = os.path.relpath(full_path, src_dir)
                # 确定目标目录
                target_dir = os.path.join('src', os.path.dirname(rel_path))
                data_files.append((full_path, target_dir))
    return data_files

# 收集所有需要包含的文件
data_files = [
    # 资源文件
    (os.path.join(project_root, 'resource'), 'resource'),
    # 配置文件
    (os.path.join(src_dir, 'cfg', 'user_config.json'), os.path.join('src', 'cfg')),
    # 依赖库（如果有）
    *([(os.path.join(project_root, 'lib', f), 'lib') for f in os.listdir(os.path.join(project_root, 'lib'))]
      if os.path.exists(os.path.join(project_root, 'lib')) else []),
]

# 添加src目录下的所有文件
data_files.extend(get_data_files(src_dir))

a = Analysis(
    # 主程序入口
    [os.path.join(src_dir, 'main.py')],
    pathex=[src_dir, project_root],
    binaries=[],
    datas=data_files,
    hiddenimports=[
        # 'PySide6',
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'xlwings',
        # 'openpyxl',
        # 'pandas',
        # 'numpy',
        # 添加其他可能需要的模块
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',  # 排除不需要的包减小体积
        'scipy',
        'sklearn',
        'tkinter',
        'test',
        'tests',
        'unittest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# 设置exe选项
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# 创建单文件exe
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Excel数据清洗工具',  # 生成的exe名称
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # 使用UPX压缩减小体积
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 不显示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(project_root, 'resource', 'icon.ico'),  # 设置exe图标
)

# 如果需要打包成文件夹形式（便于调试），使用COLLECT
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Excel数据清洗工具',
)