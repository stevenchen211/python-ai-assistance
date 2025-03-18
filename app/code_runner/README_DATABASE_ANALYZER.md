# SAS 数据库分析工具

这个工具用于分析 SAS 代码中的数据库使用情况，能够识别不同类型的数据库连接和表操作，并以 JSON 格式输出分析结果。

## 功能特性

- **多种数据库类型支持**：支持解析 Oracle、SQL Server、BigQuery、Teradata 等常见数据库类型
- **变量解析**：自动解析 SAS 代码中的变量引用 (如 `&var_name`)
- **表操作分析**：识别 SELECT、INSERT、UPDATE、DELETE、CREATE VIEW、SELECT INTO 等操作
- **命令行界面**：提供易用的命令行界面，支持文件输入和标准输入

## 支持的场景

1. **普通外部数据库** (`LIBNAME` 命令)
   - 格式：`libname dbname dbtype [连接参数];`
   - 示例：`libname mdatal bigquery server="project-id" dataset=mydataset;`
   - 分析：识别数据库名、类型和连接参数，并分析对该数据库中表的操作

2. **Teradata 数据库** (`LIBNAME` 命令)
   - 格式：`libname tblname TERADATA server="..." schema="dbname";`
   - 示例：`libname RSK_LABL TERADATA server="tdprod" schema="RISK_DB";`
   - 分析：识别 Teradata 数据库中的 schema 和表，并分析对这些表的操作

## 安装

确保已安装 Python 3.6 或更高版本，然后复制项目文件到本地目录即可。

## 使用方法

### 命令行工具

```bash
python analyze_sas.py [选项] [SAS文件路径]
```

参数：
- `[SAS文件路径]`：要分析的 SAS 代码文件路径 (如未提供则从标准输入读取)
- `--output, -o`：输出 JSON 文件路径 (如未提供则输出到标准输出)
- `--database-only, -d`：仅分析数据库使用情况
- `--pretty, -p`：美化输出 JSON

示例：
```bash
# 分析文件并美化输出
python analyze_sas.py path/to/sas_code.sas --pretty

# 分析文件并保存结果到文件
python analyze_sas.py path/to/sas_code.sas -o results.json

# 仅分析数据库使用情况
python analyze_sas.py path/to/sas_code.sas -d
```

### 在 Python 代码中使用

```python
from app.code_runner.data_source_analyzer import analyze_databases

# SAS 代码
sas_code = """
libname dwh oracle user=dw_user password=xxxx path="DWPROD";
proc sql;
    select * from dwh.customers;
quit;
"""

# 分析数据库使用情况
result = analyze_databases(sas_code)
```

## 输出格式

分析结果以 JSON 格式输出，示例如下：

```json
{
  "databases": [
    {
      "databaseName": "dwh",
      "databaseType": "oracle",
      "connectionDetail": "user=dw_user password=xxxx path=\"DWPROD\"",
      "operationTables": [
        {
          "tableName": "customers",
          "operations": ["SELECT"]
        }
      ]
    }
  ]
}
```

## 限制

- 目前仅支持 `PROC SQL` 语句块中对数据库表的操作分析
- 对于复杂的 SAS 宏或条件逻辑，可能无法完全分析所有可能的执行路径

## 扩展

该工具设计为可扩展的，支持未来添加其他数据源类型的分析，如文件系统和 API 调用。 