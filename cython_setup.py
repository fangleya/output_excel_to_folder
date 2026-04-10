# setup.py 放在项目根目录
from setuptools import setup
from Cython.Build import cythonize
import os
import sys

# -------------------------- 你的项目专属加密配置 --------------------------
# 精准指定要加密的核心模块，100%匹配你的目录结构
ENCRYPT_FILES = [
    # "src/cfg/*.py",
    # "src/config/*.py",
    # "src/core/*.py",
    "src/app/*.py",
    # "src/ui/*.py",
    "src/utils/*.py",
]


# 过滤规则：保留__init__.py不加密（避免包导入失败），排除入口文件
def filter_valid_files(file_list):
    valid_files = []
    for pattern in file_list:
        if "*" in pattern:
            import glob

            for file in glob.glob(pattern, recursive=True):
                file_name = os.path.basename(file)
                # 跳过__init__.py和main.py
                if file_name not in ["__init__.py", "main.py"]:
                    valid_files.append(file)
        else:
            file_name = os.path.basename(pattern)
            if os.path.exists(pattern) and file_name not in ["__init__.py", "main.py"]:
                valid_files.append(pattern)
    return valid_files


if __name__ == "__main__":
    target_files = filter_valid_files(ENCRYPT_FILES)
    if not target_files:
        print("❌ 未找到可加密的py文件，请检查目录结构和配置")
        sys.exit(1)

    print(f"✅ 待加密文件列表：{target_files}")
    setup(
        ext_modules=cythonize(
            target_files,
            compiler_directives={
                "language_level": "3",  # 固定Python3语法
                "embedsignature": True,  # 保留函数签名，解决打包后导入失败
                "boundscheck": False,  # 关闭边界检查，提升性能
                "wraparound": False,  # 关闭负索引，提升性能
                "initializedcheck": False,  # 关闭初始化检查
                "nonecheck": False,  # 关闭None类型检查
            },
            annotate=False,  # 调试时可改为True，生成编译分析报告
        ),
        # 编译后的pyd文件直接生成到原py文件所在目录，保持导入路径不变
        options={"build_ext": {"inplace": True, "force": True}},
    )
