# -*- mode: python ; coding: utf-8 -*-
# Excel导出工具 专属打包配置
# 1. 开启AES-256字节码加密，防止exe被直接解包（密钥请自行修改为16位以上字符）
block_cipher = pyi_crypto.PyiBlockCipher(key='ExcelTool202604101300@666888')

a = Analysis(
    ['main.py'],  # 你的入口文件
    pathex=[],
    binaries=[],
    # -------------------------- 专属资源打包配置 --------------------------
    # 格式：(开发环境的相对路径, 打包后的相对路径)，必须保持你的代码路径结构
    datas=[
        ("resource", "resource"),  # 图标资源目录，打包后保持原结构
        ("src/config", "src/config"),  # 配置文件目录，必须保留原层级
    ],
    # -------------------------- 专属隐藏导入配置（解决模块缺失报错） --------------------------
    # 精准覆盖你的项目所有依赖的隐藏模块，杜绝打包后报「No module named xxx」
    hiddenimports=[
        # PySide6核心模块
        "PySide6.QtCore",
        "PySide6.QtGui",
        "PySide6.QtWidgets",
        "PySide6.QtNetwork",
        "PySide6.QtSvg",
        "PySide6.QtOpenGL",
        # pandas&numpy依赖（打包头号坑点，必须全量添加）
        "pandas",
        "pandas._libs",
        "pandas._libs.tslibs.base",
        "pandas._libs.tslibs.np_datetime",
        "pandas._libs.tslibs.nattype",
        "pandas._libs.tslibs.conversion",
        "numpy",
        "numpy.core._multiarray_umath",
        "numpy.core._multiarray_tests",
        "numpy.linalg.lapack_lite",
        "numpy.linalg._umath_linalg",
        # Excel处理依赖
        "openpyxl",
        "openpyxl.cell",
        "openpyxl.styles",
        "openpyxl.drawing.image",
        "openpyxl.worksheet",
        # 图片处理依赖
        "PIL",
        "PIL._imaging",
        "PIL._imagingtk",
        "PIL.Image",
        "PIL.ImageFile",
        # 其他标准库隐藏依赖
        "zipfile",
        "traceback",
        "io",
        "pathlib",
    ],
    # -------------------------- 排除无用模块，减小打包体积 --------------------------
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

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Excel导出工具',  # 生成的exe文件名
    debug=False,  # 调试时改为True，可看详细报错
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # 启用UPX压缩，减小体积
    console=False,  # 调试时改为True，开启控制台看报错，正式发布改为False
    icon='resource/icon.ico',  # 程序图标，对应你的resource目录下的ico文件
    uac_admin=False,  # 如需处理系统盘文件，改为True请求管理员权限
    version='file_version_info.txt',  # 可选，添加版本信息，避免杀毒误报
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Excel导出工具',
)