# SAS Code Analysis Tool

A Celery-based SAS code analysis tool that can perform the following analysis tasks:

### 1. SAS Code Analysis Features

- **Code Chunking**
  - Extract SAS macros and preserve the main body
  - Logically split the main body based on output token size
- **Code Complexity Analysis**
  - Calculate code lines, comment lines
  - Calculate the number of macros, PROC steps, DATA steps
  - Calculate the number of IF statements, DO loops
  - Calculate cyclomatic complexity
- **Dependency Analysis**
  - Internal dependencies (such as macro calls)
  - External dependencies (such as using macros from other programs)
  - Database or dataset usage types
- **Data Source Analysis**
  - Find datasets in the code and their schemas
  - Try to extract any possible information from the source code to enrich the schema

### 2. Installation and Configuration

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd sas-code-analysis
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   - Copy `.env.example` to `.env`
   - Edit the `.env` file to set Redis and OpenAI API keys

### 3. Usage

#### Start Celery Worker

```bash
python run_worker.py
```

#### Use Command Line Tool

Analyze SAS code:
```bash
python -m app.cli code "data test; set input; run;" --output result.json
```

Analyze SAS file:
```bash
python -m app.cli file path/to/file.sas --token-size 4000 --output result.json
```

Analyze SAS files in a directory:
```bash
python -m app.cli dir path/to/directory --pattern "*.sas" --output result.json
```

#### Start API Server

```bash
python run_api.py
```

The API server will run at http://localhost:8000 and provide the following endpoints:

- `POST /api/analyze/code` - Analyze SAS code
- `POST /api/analyze/file` - Analyze SAS file
- `POST /api/analyze/directory` - Analyze SAS files in a directory
- `GET /api/task/{task_id}` - Get task status and results

API documentation can be viewed at http://localhost:8000/docs.

#### API Usage Examples

Analyze code using curl:
```bash
curl -X POST "http://localhost:8000/api/analyze/code" \
  -H "Content-Type: application/json" \
  -d '{"code": "data test; set input; run;", "max_token_size": 4000}'
```

Query task status:
```bash
curl -X GET "http://localhost:8000/api/task/{task_id}"
```

### 4. Project Structure

```
sas-code-analysis/
├── app/
│   ├── __init__.py
│   ├── celery_app.py        # Celery application configuration
│   ├── cli.py               # Command line interface
│   ├── tasks.py             # Celery task definitions
│   └── sas_analyzer/        # SAS analysis modules
│       ├── __init__.py
│       ├── code_chunker.py          # Code chunking
│       ├── complexity_analyzer.py    # Complexity analysis
│       ├── dependency_analyzer.py    # Dependency analysis
│       └── data_source_analyzer.py   # Data source analysis
├── .env.example             # Environment variables example
├── requirements.txt         # Dependencies list
├── run_worker.py            # Worker startup script
├── run_api.py               # API server startup script
└── README.md                # Project documentation
```

### 5. Dependencies

- Python 3.8+
- Celery
- Redis
- FastAPI
- LangChain
- OpenAI API (optional, for enhanced analysis)





