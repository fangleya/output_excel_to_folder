# run_tests.py
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试运行脚本
"""
import os
import sys

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# 运行测试
if __name__ == "__main__":
    import unittest

    # 自动发现并运行所有测试
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover("test", pattern="test_*.py")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    sys.exit(0 if result.wasSuccessful() else 1)
