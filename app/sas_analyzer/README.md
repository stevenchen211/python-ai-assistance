# SAS代码分析工具

基于Celery的SAS代码分析工具，可以执行以下分析任务：

### 1. SAS代码分析功能

- **代码分块**
  - 提取SAS宏，并保留主体
  - 根据输出令牌大小逻辑拆分主体
- **代码复杂度分析**
  - 计算代码行数、注释行数
  - 计算宏、PROC步骤、DATA步骤数量
  - 计算IF语句、DO循环数量
  - 计算圈复杂度
- **依赖分析**
  - 内部依赖（如宏调用）
  - 外部依赖（如使用其他程序的宏）
  - 数据库或数据集使用类型
- **数据源分析**
  - 查找代码中的数据集及其模式
  - 尝试从源代码中提取任何可能的信息来丰富模式

### 2. 安装与配置

1. 克隆仓库：
   ```bash
   git clone <repository-url>
   cd sas-code-analysis
   ```

2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

3. 配置环境变量：
   - 复制`.env.example`为`.env`
   - 编辑`.env`文件，设置Redis和OpenAI API密钥

### 3. 使用方法

#### 启动Celery Worker

```bash
python run_worker.py
```

#### 使用命令行工具

分析SAS代码：
```bash
python -m app.cli code "data test; set input; run;" --output result.json
```

分析SAS文件：
```bash
python -m app.cli file path/to/file.sas --token-size 4000 --output result.json
```

分析目录中的SAS文件：
```bash
python -m app.cli dir path/to/directory --pattern "*.sas" --output result.json
```

#### 启动API服务器

```bash
python run_api.py
```

API服务器将在 http://localhost:8000 上运行，并提供以下端点：

- `POST /api/analyze/code` - 分析SAS代码
- `POST /api/analyze/file` - 分析SAS文件
- `POST /api/analyze/directory` - 分析目录中的SAS文件
- `GET /api/task/{task_id}` - 获取任务状态和结果

API文档可在 http://localhost:8000/docs 查看。

#### API使用示例

使用curl分析代码：
```bash
curl -X POST "http://localhost:8000/api/analyze/code" \
  -H "Content-Type: application/json" \
  -d '{"code": "data test; set input; run;", "max_token_size": 4000}'
```

查询任务状态：
```bash
curl -X GET "http://localhost:8000/api/task/{task_id}"
```

### 4. 项目结构

```
sas-code-analysis/
├── app/
│   ├── __init__.py
│   ├── celery_app.py        # Celery应用配置
│   ├── cli.py               # 命令行接口
│   ├── tasks.py             # Celery任务定义
│   └── sas_analyzer/        # SAS分析模块
│       ├── __init__.py
│       ├── code_chunker.py          # 代码分块
│       ├── complexity_analyzer.py    # 复杂度分析
│       ├── dependency_analyzer.py    # 依赖分析
│       └── data_source_analyzer.py   # 数据源分析
├── .env.example             # 环境变量示例
├── requirements.txt         # 依赖列表
├── run_worker.py            # 启动Worker脚本
├── run_api.py               # 启动API服务器脚本
└── README.md                # 项目说明
```

### 5. 依赖

- Python 3.8+
- Celery
- Redis
- FastAPI
- LangChain
- OpenAI API (可选，用于增强分析)





