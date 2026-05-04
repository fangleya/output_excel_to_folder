# build_encrypted.py — 加密单文件一键打包脚本
"""
步骤:
  1. 环境检查
  2. 备份 src/**/*.py
  3. Cython 编译 .py → .pyd
  4. 清理中间文件
  5. 删除原始 .py（保留 __init__.py）
  6. PyInstaller 单文件打包
  7. 恢复备份的 .py
"""
import os
import sys
import shutil
import subprocess
import time
from pathlib import Path

PROJECT_ROOT = Path(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = PROJECT_ROOT / "src"
BACKUP_DIR = PROJECT_ROOT / ".build_backup"
CYTHON_SCRIPT = PROJECT_ROOT / "cython_setup.py"
SPEC_FILE = PROJECT_ROOT / "Excel导出工具_onefile.spec"
DIST_DIR = PROJECT_ROOT / "dist"
BUILD_DIR = PROJECT_ROOT / "build"
EXE_NAME = "Excel导出工具.exe"


def step(msg):
    print(f"\n{'='*60}")
    print(f"  {msg}")
    print(f"{'='*60}")


def fail(msg):
    print(f"\n  [ERROR] {msg}")
    input("\n按任意键退出...")
    sys.exit(1)


def run_cmd(cmd, cwd=None):
    """运行命令，失败返回 False"""
    print(f"  > {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    result = subprocess.run(cmd, cwd=cwd or PROJECT_ROOT, shell=isinstance(cmd, str))
    if result.returncode != 0:
        print(f"  [FAILED] 返回码: {result.returncode}")
        return False
    print(f"  [OK]")
    return True


# ---------------------------------------------------------------------------
def step1_check_env():
    step("1/8 环境检查")
    # 检查 Python
    try:
        r = subprocess.run([sys.executable, "-c", "import sys; print(sys.executable)"],
                           capture_output=True, text=True, cwd=PROJECT_ROOT)
        py_path = r.stdout.strip()
        print(f"  Python: {py_path}")
        if "env_python310" not in py_path:
            print("  [WARNING] 当前不是 env_python310 环境，请确认")
    except Exception:
        fail("无法运行 Python")

    # 检查关键依赖
    for mod in ["PySide6", "Cython", "PyInstaller", "pandas", "openpyxl"]:
        r = subprocess.run([sys.executable, "-c", f"import {mod}"],
                           capture_output=True, cwd=PROJECT_ROOT)
        if r.returncode != 0:
            fail(f"缺少依赖: {mod}，请执行 pip install -r requirements.txt")

    print("  依赖检查通过")

    # 检查必要文件
    for f in [SRC_DIR, CYTHON_SCRIPT, SPEC_FILE, PROJECT_ROOT / "main.py"]:
        if not f.exists():
            fail(f"缺少文件: {f}")
    print("  文件检查通过")


# ---------------------------------------------------------------------------
def step2_backup():
    step("2/8 备份源码")
    if BACKUP_DIR.exists():
        shutil.rmtree(BACKUP_DIR)
    BACKUP_DIR.mkdir(parents=True)

    py_files = list(SRC_DIR.rglob("*.py"))
    if not py_files:
        fail("src 目录下没有找到 .py 文件")

    for f in py_files:
        rel = f.relative_to(PROJECT_ROOT)
        dest = BACKUP_DIR / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, dest)

    print(f"  已备份 {len(py_files)} 个文件到 {BACKUP_DIR}")


# ---------------------------------------------------------------------------
def step3_cython():
    step("3/8 Cython 编译 (.py → .pyd)")
    ok = run_cmd([sys.executable, str(CYTHON_SCRIPT), "build_ext", "--inplace"])
    if not ok:
        restore_backup()
        fail("Cython 编译失败，请检查是否安装了 MSVC 编译器")
    # 统计生成的 .pyd
    pyd_files = list(SRC_DIR.rglob("*.pyd"))
    print(f"  生成 .pyd 文件: {len(pyd_files)} 个")
    for f in pyd_files:
        print(f"    {f.relative_to(PROJECT_ROOT)}")


# ---------------------------------------------------------------------------
def step4_clean_intermediate():
    step("4/8 清理编译中间文件")
    # 删除 .c 文件
    for c_file in PROJECT_ROOT.rglob("*.c"):
        c_file.unlink()
        print(f"  删除: {c_file.relative_to(PROJECT_ROOT)}")

    # 删除 build 临时目录（Cython 的，不是 PyInstaller 的）
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
        print(f"  删除: build/")

    # 删除可能的 dist 目录（Cython setuptools 可能产生的）
    dist_in_src = SRC_DIR / "dist"
    if dist_in_src.exists():
        shutil.rmtree(dist_in_src)


# ---------------------------------------------------------------------------
def step5_remove_source_py():
    step("5/8 删除原始 .py（保留 __init__.py 和 main.py）")
    removed = 0
    kept = 0
    for f in SRC_DIR.rglob("*.py"):
        if f.name == "__init__.py":
            kept += 1
            continue
        f.unlink()
        removed += 1
        print(f"  删除: {f.relative_to(PROJECT_ROOT)}")
    print(f"  共删除 {removed} 个文件，保留 {kept} 个 __init__.py")


# ---------------------------------------------------------------------------
def step6_pyinstaller():
    step("6/8 PyInstaller 单文件打包")
    # 清理旧的输出
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)

    ok = run_cmd([sys.executable, "-m", "PyInstaller", "--clean", "--noconfirm", str(SPEC_FILE)])
    if not ok:
        restore_backup()
        fail("PyInstaller 打包失败")

    exe_path = DIST_DIR / EXE_NAME
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"\n  [SUCCESS] 单文件生成完毕:")
        print(f"    {exe_path}")
        print(f"    大小: {size_mb:.1f} MB")
    else:
        # 可能在子目录里
        for candidate in DIST_DIR.rglob(EXE_NAME):
            size_mb = candidate.stat().st_size / (1024 * 1024)
            print(f"\n  [SUCCESS] 单文件生成完毕:")
            print(f"    {candidate}")
            print(f"    大小: {size_mb:.1f} MB")
            break
        else:
            restore_backup()
            fail("打包完成但未找到 exe 文件")


# ---------------------------------------------------------------------------
def step7_restore():
    step("7/8 恢复源码")
    restore_backup()
    # 删除备份目录
    if BACKUP_DIR.exists():
        shutil.rmtree(BACKUP_DIR)
        print(f"  已删除备份目录")


def restore_backup():
    """从备份恢复所有 .py 文件"""
    if not BACKUP_DIR.exists():
        return
    for f in BACKUP_DIR.rglob("*.py"):
        rel = f.relative_to(BACKUP_DIR)
        dest = PROJECT_ROOT / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, dest)
    print(f"  已从备份恢复源码文件")


# ---------------------------------------------------------------------------
def step8_done():
    step("8/8 打包完成")
    print(f"""
  ┌─────────────────────────────────────────┐
  │  加密单文件程序已生成:                    │
  │  {DIST_DIR / EXE_NAME}
  │                                          │
  │  - 核心代码已 Cython 编译为 .pyd (加密)   │
  │  - 所有内容打包为单个 .exe                 │
  │  - 源码已完整恢复                         │
  └─────────────────────────────────────────┘
""")


# ---------------------------------------------------------------------------
def main():
    start_time = time.time()
    print("=" * 60)
    print("  Excel导出工具 — 加密单文件打包")
    print("=" * 60)

    try:
        step1_check_env()
        step2_backup()
        step3_cython()
        step4_clean_intermediate()
        step5_remove_source_py()
        step6_pyinstaller()
        step7_restore()
        step8_done()
    except KeyboardInterrupt:
        print("\n\n  用户中断，正在恢复源码...")
        restore_backup()
        sys.exit(1)
    except Exception as e:
        print(f"\n  [FATAL ERROR] {e}")
        restore_backup()
        sys.exit(1)

    elapsed = time.time() - start_time
    print(f"  总耗时: {elapsed:.0f} 秒\n")
    input("按任意键退出...")


if __name__ == "__main__":
    main()
