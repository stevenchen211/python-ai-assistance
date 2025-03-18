# SAS Database Analysis Tool

This tool is used to analyze database usage in SAS code, capable of identifying different types of database connections and table operations, and outputting analysis results in JSON format.

## Features

- **Multiple Database Type Support**: Supports parsing Oracle, SQL Server, BigQuery, Teradata and other common database types
- **Variable Resolution**: Automatically resolves variable references in SAS code (such as `&var_name`)
- **Table Operation Analysis**: Identifies operations like SELECT, INSERT, UPDATE, DELETE, CREATE VIEW, SELECT INTO
- **Command Line Interface**: Provides an easy-to-use command line interface, supporting file input and standard input

## Supported Scenarios

1. **Generic External Databases** (`LIBNAME` command)
   - Format: `libname dbname dbtype [connection parameters];`
   - Example: `libname mdatal bigquery server="project-id" dataset=mydataset;`
   - Analysis: Identifies database name, type, and connection parameters, and analyzes operations on tables in that database

2. **Teradata Databases** (`LIBNAME` command)
   - Format: `libname tblname TERADATA server="..." schema="dbname";`
   - Example: `libname RSK_LABL TERADATA server="tdprod" schema="RISK_DB";`
   - Analysis: Identifies schemas and tables in Teradata databases, and analyzes operations on these tables

## Installation

Ensure you have Python 3.6 or higher installed, then copy the project files to your local directory.

## Usage

### Command Line Tool

```bash
python analyze_sas.py [options] [SAS_file_path]
```

Parameters:
- `[SAS_file_path]`: Path to the SAS code file to analyze (if not provided, reads from standard input)
- `--output, -o`: Output JSON file path (if not provided, outputs to standard output)
- `--database-only, -d`: Only analyze database usage
- `--pretty, -p`: Beautify JSON output

Examples:
```bash
# Analyze file and beautify output
python analyze_sas.py path/to/sas_code.sas --pretty

# Analyze file and save results to file
python analyze_sas.py path/to/sas_code.sas -o results.json

# Only analyze database usage
python analyze_sas.py path/to/sas_code.sas -d
```

### Using in Python Code

```python
from app.code_runner.data_source_analyzer import analyze_databases

# SAS code
sas_code = """
libname dwh oracle user=dw_user password=xxxx path="DWPROD";
proc sql;
    select * from dwh.customers;
quit;
"""

# Analyze database usage
result = analyze_databases(sas_code)
```

## Output Format

Analysis results are output in JSON format, for example:

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

## Limitations

- Currently only supports analysis of database table operations within `PROC SQL` blocks
- For complex SAS macros or conditional logic, it may not be able to fully analyze all possible execution paths

## Extension

This tool is designed to be extensible, supporting the future addition of analysis for other data source types, such as file systems and API calls. 