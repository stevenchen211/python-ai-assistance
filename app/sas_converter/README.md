# SAS to Python Converter

This package provides functionality to convert SAS code to Python code. It leverages Azure OpenAI services for code conversion and offers a series of tools to handle various aspects of SAS code.

## Features

1. **SAS Macro Conversion**: Convert SAS macros to Python functions
2. **Main Code Conversion**: Convert SAS main body code to Python code
3. **SQL Processing**: Special handling for SQL code within SAS
4. **Database Connection**: Generate database connection code based on data source analysis results
5. **Dependency Handling**: Identify and mark external dependencies that cannot be automatically converted
6. **Code Merging**: Merge converted code, handle import statements
7. **Generate requirements.txt**: Automatically generate Python dependency list

## Installation

Ensure you have installed the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Command Line Usage

```bash
python -m app.sas_converter.cli input_file.sas --output-dir output_directory --openai-api-key YOUR_OPENAI_API_KEY --azure-openai-api-key YOUR_AZURE_OPENAI_API_KEY
```

Parameter description:
- `input_file.sas`: Path to the input SAS file
- `--output-dir`: Output directory path, default is "output"
- `--openai-api-key`: OpenAI API key (for analysis)
- `--azure-openai-api-key`: Azure OpenAI API key (for conversion)

### Usage in Code

```python
from app.sas_converter.converter import SASConverter

# Initialize converter
converter = SASConverter(
    openai_api_key="YOUR_OPENAI_API_KEY",
    azure_openai_api_key="YOUR_AZURE_OPENAI_API_KEY"
)

# Read SAS code
with open("input_file.sas", "r", encoding="utf-8") as f:
    sas_code = f.read()

# Convert SAS code
result = converter.convert(sas_code, "input_file")

# Save output
converter.save_output(result, "output_directory", "input_file")
```

## Output Structure

The converted output will include the following:

- `{base_filename}.py`: Converted Python code
- `requirements.txt`: Python dependency list
- `functions/`: Converted Python function library
- `analysis/`: SAS code analysis results

## Configuration

The converter uses the following environment variables:

- `OPENAI_API_KEY`: OpenAI API key (for analysis)
- `AZURE_OPENAI_API_KEY`: Azure OpenAI API key (for conversion)
- `AZURE_OPENAI_API_BASE`: Azure OpenAI API base URL
- `AZURE_OPENAI_API_VERSION`: Azure OpenAI API version
- `AZURE_OPENAI_DEPLOYMENT_NAME`: Azure OpenAI deployment name

You can also specify these values directly in the code.

## Custom Prompts

The converter uses predefined prompts to guide AI in code conversion. These prompts are stored in the `config.py` file, which you can modify as needed.

## Notes

- Converted code may require manual adjustment, especially for complex SAS code
- External dependencies need to be handled manually
- Database connection information needs to be configured according to actual circumstances 