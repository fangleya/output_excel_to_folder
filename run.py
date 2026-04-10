# run.py（放在项目根目录）
import sys
import os

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# 导入并运行主程序
from main import main

if __name__ == "__main__":
    main()
