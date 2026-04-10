import os
import sys

# 自定义注释映射：匹配你示例中的注释，可根据自己的工程扩展
COMMENT_MAP = {
    "docker": "容器化部署相关（企业级交付必备）",
    "docs": "【强化】文档目录（补充分类，企业级需标准化）",
    "docs/api": "【接口文档（若后续扩展接口）",
    "docs/design": "设计文档（UI/业务逻辑设计）",
    "docs/deploy": "部署文档",
    "docs/user_guide.md": "用户手册",
    "lib": "第三方依赖库（若有无法通过pip安装的包）",
    "resources": "静态资源文件（图片、配置模板、字体等）",
    "resources/icons": "图标文件夹",
    "resources/styles": "样式表文件夹",
    "resources/configs": "配置文件模板（如app.ini.template）",
    "resources/app_icons.qrc": "资源描述文件",
    "scripts": "核心源代码",
    "src": "核心源代码",
    "src/__init__.py": "标记为Python包",
    "src/cfg": "配置模块（读取/解析配置文件）",
    "src/cfg/app_config.py": "配置读取逻辑",
    "src/core": "核心业务层",
    "src/ui": "UI文件目录",
    "src/logic": "业务逻辑",
    "src/utils": "工具函数",
    "src/utils/log_utils.py": "日志工具",
    "src/utils/path_utils.py": "路径工具",
    "tests": "测试代码",
    "tests/unit": "单元测试（测试单个函数/类）",
    "tests/integration": "集成测试（测试模块间交互）",
    "tests/conftest.py": "测试夹具（如初始化QApplication）",
    "tmp": "临时文件目录（日志、缓存等）",
    ".gitignore": "Git忽略文件（避免提交tmp/、__pycache__等）",
    "project_structure.md": "目录说明文档",
    "pyproject.toml": "项目配置文件（现代Python标准）",
    "requirements.txt": "依赖清单（可通过pyproject.toml关联）",
    "ReadMe.md": "项目说明（补充环境搭建、运行命令）",
    "main.py": "程序入口",
}

# 需要跳过的无用文件/文件夹（避免干扰结构展示）
SKIP_ITEMS = {"__pycache__", ".git", ".idea", "venv", "env", ".vscode", "logs", "dist", "build", "*.pyc", ".DS_Store"}


def should_skip(item_name: str) -> bool:
    """判断是否需要跳过当前文件/文件夹"""
    for skip in SKIP_ITEMS:
        if skip.startswith("*"):
            # 匹配后缀（如*.pyc）
            suffix = skip[1:]
            if item_name.endswith(suffix):
                return True
        elif item_name == skip:
            return True
    return False


def get_relative_path(project_root: str, item_path: str) -> str:
    """
    获取相对于项目根目录的路径（用于匹配注释）
    :param project_root: 项目最顶层根目录
    :param item_path: 当前文件/文件夹的绝对路径
    :return: 标准化的相对路径（/分隔）
    """
    rel_path = os.path.relpath(item_path, project_root)
    # 统一路径分隔符为/（兼容Windows）
    return rel_path.replace(os.sep, "/")


def generate_tree(
    current_dir: str,  # 当前递归处理的目录
    project_root: str,  # 项目顶层根目录（固定）
    prefix: str = "",  # 层级前缀（控制树形符号）
    is_last: bool = True,  # 是否是当前层级最后一个项
    output_lines: list = None,  # 存储输出行的列表 # type: ignore
) -> None:
    """
    递归生成树形目录结构（修复相对路径计算逻辑）
    :param current_dir: 当前递归处理的目录
    :param project_root: 项目顶层根目录（固定）
    :param prefix: 层级前缀（控制树形符号）
    :param is_last: 是否是当前层级最后一个项
    :param output_lines: 存储输出行的列表
    """
    if output_lines is None:
        output_lines = []

    # 获取当前目录下的所有项（按文件夹在前、文件在后排序）
    items = []
    for item in os.listdir(current_dir):
        if should_skip(item):
            continue
        item_path = os.path.join(current_dir, item)
        items.append((item, item_path, os.path.isdir(item_path)))

    # 排序：文件夹在前，文件在后；名称按字母排序
    items.sort(key=lambda x: (not x[2], x[0]))
    total = len(items)

    for idx, (item_name, item_path, is_dir) in enumerate(items):
        is_last_item = idx == total - 1

        # 构建树形符号
        if is_last:
            current_prefix = prefix + "└── "
            next_prefix = prefix + "    "
        else:
            current_prefix = prefix + "├── "
            next_prefix = prefix + "│   "

        # 修复：传入项目根目录计算相对路径（而非当前递归目录的父目录）
        rel_path = get_relative_path(project_root, item_path)
        comment = COMMENT_MAP.get(rel_path, "")

        # 构建行文本（带注释）
        line = f"{current_prefix}{item_name}/" if is_dir else f"{current_prefix}{item_name}"
        if comment:
            line += f"       # {comment}"
        output_lines.append(line)

        # 递归处理子目录
        if is_dir:
            generate_tree(item_path, project_root, next_prefix, is_last_item, output_lines)


def main(project_root: str):
    """主函数：生成并输出目录结构"""
    # 校验目录是否存在
    if not os.path.isdir(project_root):
        print(f"❌ 错误：目录 {project_root} 不存在！")
        sys.exit(1)

    # 获取项目根目录名称（用于标题）
    root_name = os.path.basename(os.path.abspath(project_root))
    output_lines = [f"{root_name}/          # 项目根目录（可大写开头，仅根目录例外）"]

    # 修复：传入项目根目录给generate_tree（当前目录=项目根，项目根=项目根）
    generate_tree(project_root, project_root, "", is_last=True, output_lines=output_lines)

    # 合并为文本
    structure_text = "\n".join(output_lines)

    # 1. 输出到控制台
    print("\n📋 项目目录结构：")
    print("-" * 50)
    print(structure_text)
    print("-" * 50)

    # 2. 保存到文件（project_structure.md）
    output_file = os.path.join(project_root, "project_structure.md")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# PySide6工程目录结构\n\n")
        f.write("```\n")
        f.write(structure_text)
        f.write("\n```")

    print(f"\n✅ 目录结构已保存到：{output_file}")


if __name__ == "__main__":
    # 支持命令行传入项目根目录，否则使用当前目录
    if len(sys.argv) >= 2:
        project_root = sys.argv[1]
    else:
        project_root = os.getcwd()  # 默认当前目录

    # 规范化路径（兼容不同系统）
    project_root = os.path.abspath(project_root)
    main(project_root)
