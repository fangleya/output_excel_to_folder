# PySide6工程目录结构

```
output_excel_to_folder/          # 项目根目录（可大写开头，仅根目录例外）
└── config/
└── docker/       # 容器化部署相关（企业级交付必备）
    ├── Dockerfile
    ├── docker-compose.yml
└── docs/       # 【强化】文档目录（补充分类，企业级需标准化）
└── lib/       # 第三方依赖库（若有无法通过pip安装的包）
└── resource/
    ├── excel.ico
    ├── icon.ico
└── src/       # 核心源代码
    ├── cfg/       # 配置模块（读取/解析配置文件）
    │   ├── __init__.py
    ├── config/
    │   ├── app_config.json
    │   ├── system_config.json
    │   ├── theme_config.json
    │   ├── user_config.json
    │   ├── window_config.json
    ├── core/       # 核心业务层
    │   ├── __init__.py
    ├── logic/       # 业务逻辑
    │   ├── __init__.py
    ├── ui/       # UI文件目录
    │   ├── __init__.py
    ├── utils/       # 工具函数
    │   ├── __init__.py
    │   ├── config_manager.py
    │   ├── dialog_manager.py
    │   ├── path_utils.py       # 路径工具
    │   ├── resource_manager.py
    │   ├── resource_utils.py
    ├── __init__.py       # 标记为Python包
    ├── main.py
└── test/
    ├── __init__.py
    ├── debug_resources.py
    ├── test.html
    ├── test_config_manager.py
    ├── test_resource_manager.py
└── tmp/       # 临时文件目录（日志、缓存等）
└── .gitignore       # Git忽略文件（避免提交tmp/、__pycache__等）
└── README.en.md
└── README.md
└── build.bat
└── build.ps1.bak
└── build.py
└── build_simple.py
└── project_structure.md       # 目录说明文档
└── pyside6_excel_clean.spec
└── read_project_structure.py
└── requirements.txt       # 依赖清单（可通过pyproject.toml关联）
└── run.py
└── run_tests.py
```