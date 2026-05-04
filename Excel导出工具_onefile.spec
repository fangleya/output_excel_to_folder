# -*- mode: python ; coding: utf-8 -*-
# Excel导出工具 单文件加密打包配置
# Cython编译后 .py → .pyd，PyInstaller通过import分析自动发现.pyd
# 所有内容打入单exe，不使用COLLECT
import os

block_cipher = None

spec_root = os.path.dirname(os.path.abspath(SPECPATH))

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ("resource", "resource"),
        ("src/config", "src/config"),
    ],
    hiddenimports=[
        "src.app.app_view",
        "src.app.app_viewmodel",
        "src.utils.config_manager",
        "src.utils.dialog_manager",
        "src.utils.path_utils",
        "src.utils.resource_manager",
        "src.utils.resource_utils",

        "PySide6.QtCore",
        "PySide6.QtGui",
        "PySide6.QtWidgets",
        "PySide6.QtNetwork",
        "PySide6.QtSvg",
        "PySide6.QtOpenGL",

        "pandas",
        "pandas._libs",

        "numpy",

        "openpyxl",

        "PIL",

        "zipfile",
        "traceback",
        "io",
        "pathlib",
    ],
    excludes=[
        "tkinter",
        "unittest",
        "pytest",
        "pip",
        "setuptools",
        "wheel",
        "cython",
        "matplotlib",
        "scipy",
        "jupyter",
        "notebook",
        "django",
        "flask",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# ---- 单文件模式：所有内容直接打入 EXE，不使用 COLLECT ----
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Excel导出工具',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resource/icon_app.ico',
    uac_admin=False,
    version='file_version_info.txt',
)
