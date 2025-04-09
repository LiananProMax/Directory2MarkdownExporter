# Directory to Markdown Exporter 🗂️→📄

将项目目录结构及文件内容自动导出为可读的Markdown文档，支持智能过滤和灵活配置。

## 功能特性
- 🌳 生成类`tree`命令的目录结构图
- 📝 自动附加文件内容到Markdown文档
- ⚙️ 支持`.env`文件配置默认路径
- 🚫 排除指定目录/文件/扩展名（如`.git`, `node_modules`）
- 🔀 命令行参数优先于配置文件
- ⚠️ 自动跳过二进制文件
- 🖥️ 支持Windows/macOS/Linux
## 快速开始
### 安装依赖
```bash
pip install python-dotenv
```


## 高级配置
### 配置文件`.env`
```ini
INPUT_DIR=./my_project
OUTPUT_FILE=./STRUCTURE.md
EXCLUDE_DIRS=.git, __pycache__, node_modules
EXCLUDE_FILES=README.md, .DS_Store
EXCLUDE_EXTENSIONS=.log, .tmp, .exe
```
### 命令行参数
| 参数        | 说明                          | 默认值       |
|-------------|-------------------------------|-------------|
| `input_dir` | 要扫描的目录路径              | .env中配置  |
| `output_file` | 生成的Markdown文件路径       | .env中配置  |
### 排除规则
- **目录排除**：精确匹配目录名称（如`.git`）
- **文件排除**：精确匹配文件名（如`secret.key`）
- **扩展名排除**：匹配文件后缀（如`.log`）
## 输出示例
````markdown
目录结构
```
.
├── src
│   ├── __init__.py
│   └── main.py
└── README.md
2 directories, 2 files
```
README.md
```python
# My Awesome Project
...
```
````
## 常见问题
### 如何处理二进制文件？
程序会自动跳过无法用UTF-8解码的文件，并在控制台显示警告：
```
⚠️ 跳过二进制文件: images/logo.png
```
### 为什么某些文件没有被排除？
请检查：
1. 排除规则是否在`.env`文件中正确配置
2. 文件名/扩展名是否完全匹配（区分大小写）
3. 是否通过命令行参数覆盖了配置
## 贡献指南
欢迎提交Issue和PR！建议遵循以下流程：
1. Fork仓库
2. 创建功能分支（`feat/xxx` 或 `fix/xxx`）
3. 提交测试用例
4. 发起Pull Request
## 许可协议
MIT License © 2024 LiananProMax
