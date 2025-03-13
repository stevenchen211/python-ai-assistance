# SAS到Python转换器

这个包提供了将SAS代码转换为Python代码的功能。它利用Azure OpenAI服务进行代码转换，并提供了一系列工具来处理SAS代码的各个方面。

## 功能特点

1. **SAS宏转换**：将SAS宏转换为Python函数
2. **主体代码转换**：将SAS主体代码转换为Python代码
3. **SQL处理**：特殊处理SAS中的SQL代码
4. **数据库连接**：根据数据源分析结果生成数据库连接代码
5. **依赖处理**：识别并标记无法自动转换的外部依赖
6. **代码合并**：合并转换后的代码，处理import语句
7. **生成requirements.txt**：自动生成Python依赖列表

## 安装

确保已安装所需的依赖：

```bash
pip install -r requirements.txt
```

## 使用方法

### 命令行使用

```bash
python -m app.sas_converter.cli input_file.sas --output-dir output_directory --openai-api-key YOUR_OPENAI_API_KEY --azure-openai-api-key YOUR_AZURE_OPENAI_API_KEY
```

参数说明：
- `input_file.sas`：输入的SAS文件路径
- `--output-dir`：输出目录路径，默认为"output"
- `--openai-api-key`：OpenAI API密钥（用于分析）
- `--azure-openai-api-key`：Azure OpenAI API密钥（用于转换）

### 代码中使用

```python
from app.sas_converter.converter import SASConverter

# 初始化转换器
converter = SASConverter(
    openai_api_key="YOUR_OPENAI_API_KEY",
    azure_openai_api_key="YOUR_AZURE_OPENAI_API_KEY"
)

# 读取SAS代码
with open("input_file.sas", "r", encoding="utf-8") as f:
    sas_code = f.read()

# 转换SAS代码
result = converter.convert(sas_code, "input_file")

# 保存输出
converter.save_output(result, "output_directory", "input_file")
```

## 输出结构

转换后的输出将包含以下内容：

- `{base_filename}.py`：转换后的Python代码
- `requirements.txt`：Python依赖列表
- `functions/`：转换后的Python函数库
- `analysis/`：SAS代码分析结果

## 配置

转换器使用以下环境变量：

- `OPENAI_API_KEY`：OpenAI API密钥（用于分析）
- `AZURE_OPENAI_API_KEY`：Azure OpenAI API密钥（用于转换）
- `AZURE_OPENAI_API_BASE`：Azure OpenAI API基础URL
- `AZURE_OPENAI_API_VERSION`：Azure OpenAI API版本
- `AZURE_OPENAI_DEPLOYMENT_NAME`：Azure OpenAI部署名称

您也可以在代码中直接指定这些值。

## 自定义提示

转换器使用预定义的提示来指导AI进行代码转换。这些提示存储在`config.py`文件中，您可以根据需要进行修改。

## 注意事项

- 转换后的代码可能需要手动调整，特别是对于复杂的SAS代码
- 外部依赖需要手动处理
- 数据库连接信息需要根据实际情况进行配置 