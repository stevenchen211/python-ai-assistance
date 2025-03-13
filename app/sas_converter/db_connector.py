"""
数据库连接处理模块
"""
from typing import Dict, List, Any, Optional
import re


class DBConnector:
    """数据库连接处理器"""
    
    def __init__(self, data_source_analysis: Optional[Dict[str, Any]] = None):
        """
        初始化数据库连接处理器
        
        Args:
            data_source_analysis: 数据源分析结果
        """
        self.data_source_analysis = data_source_analysis or {}
        self.connection_templates = {
            'sqlserver': self._get_sqlserver_template,
            'oracle': self._get_oracle_template,
            'mysql': self._get_mysql_template,
            'postgresql': self._get_postgresql_template,
            'sqlite': self._get_sqlite_template,
        }
    
    def _get_sqlserver_template(self, connection_info: Dict[str, str]) -> str:
        """
        获取SQL Server连接模板
        
        Args:
            connection_info: 连接信息
            
        Returns:
            连接代码
        """
        server = connection_info.get('server', 'SERVER_NAME')
        database = connection_info.get('database', 'DATABASE_NAME')
        username = connection_info.get('username', 'USERNAME')
        password = connection_info.get('password', 'PASSWORD')
        
        return f"""
# SQL Server连接
import pyodbc
import pandas as pd
from sqlalchemy import create_engine

# 使用pyodbc
conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
conn = pyodbc.connect(conn_str)

# 使用SQLAlchemy
engine = create_engine(f'mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server')

# 读取数据示例
# df = pd.read_sql('SELECT * FROM table_name', conn)
# 或
# df = pd.read_sql('SELECT * FROM table_name', engine)
"""
    
    def _get_oracle_template(self, connection_info: Dict[str, str]) -> str:
        """
        获取Oracle连接模板
        
        Args:
            connection_info: 连接信息
            
        Returns:
            连接代码
        """
        host = connection_info.get('host', 'HOST')
        port = connection_info.get('port', '1521')
        service = connection_info.get('service', 'SERVICE_NAME')
        username = connection_info.get('username', 'USERNAME')
        password = connection_info.get('password', 'PASSWORD')
        
        return f"""
# Oracle连接
import cx_Oracle
import pandas as pd
from sqlalchemy import create_engine

# 使用cx_Oracle
dsn = cx_Oracle.makedsn(host='{host}', port={port}, service_name='{service}')
conn = cx_Oracle.connect(user='{username}', password='{password}', dsn=dsn)

# 使用SQLAlchemy
engine = create_engine(f'oracle+cx_oracle://{username}:{password}@{host}:{port}/?service_name={service}')

# 读取数据示例
# df = pd.read_sql('SELECT * FROM table_name', conn)
# 或
# df = pd.read_sql('SELECT * FROM table_name', engine)
"""
    
    def _get_mysql_template(self, connection_info: Dict[str, str]) -> str:
        """
        获取MySQL连接模板
        
        Args:
            connection_info: 连接信息
            
        Returns:
            连接代码
        """
        host = connection_info.get('host', 'HOST')
        port = connection_info.get('port', '3306')
        database = connection_info.get('database', 'DATABASE_NAME')
        username = connection_info.get('username', 'USERNAME')
        password = connection_info.get('password', 'PASSWORD')
        
        return f"""
# MySQL连接
import pymysql
import pandas as pd
from sqlalchemy import create_engine

# 使用pymysql
conn = pymysql.connect(host='{host}', port={port}, user='{username}', password='{password}', database='{database}')

# 使用SQLAlchemy
engine = create_engine(f'mysql+pymysql://{username}:{password}@{host}:{port}/{database}')

# 读取数据示例
# df = pd.read_sql('SELECT * FROM table_name', conn)
# 或
# df = pd.read_sql('SELECT * FROM table_name', engine)
"""
    
    def _get_postgresql_template(self, connection_info: Dict[str, str]) -> str:
        """
        获取PostgreSQL连接模板
        
        Args:
            connection_info: 连接信息
            
        Returns:
            连接代码
        """
        host = connection_info.get('host', 'HOST')
        port = connection_info.get('port', '5432')
        database = connection_info.get('database', 'DATABASE_NAME')
        username = connection_info.get('username', 'USERNAME')
        password = connection_info.get('password', 'PASSWORD')
        
        return f"""
# PostgreSQL连接
import psycopg2
import pandas as pd
from sqlalchemy import create_engine

# 使用psycopg2
conn = psycopg2.connect(host='{host}', port={port}, user='{username}', password='{password}', dbname='{database}')

# 使用SQLAlchemy
engine = create_engine(f'postgresql://{username}:{password}@{host}:{port}/{database}')

# 读取数据示例
# df = pd.read_sql('SELECT * FROM table_name', conn)
# 或
# df = pd.read_sql('SELECT * FROM table_name', engine)
"""
    
    def _get_sqlite_template(self, connection_info: Dict[str, str]) -> str:
        """
        获取SQLite连接模板
        
        Args:
            connection_info: 连接信息
            
        Returns:
            连接代码
        """
        database = connection_info.get('database', 'DATABASE_FILE.db')
        
        return f"""
# SQLite连接
import sqlite3
import pandas as pd
from sqlalchemy import create_engine

# 使用sqlite3
conn = sqlite3.connect('{database}')

# 使用SQLAlchemy
engine = create_engine(f'sqlite:///{database}')

# 读取数据示例
# df = pd.read_sql('SELECT * FROM table_name', conn)
# 或
# df = pd.read_sql('SELECT * FROM table_name', engine)
"""
    
    def generate_db_connections(self) -> str:
        """
        生成数据库连接代码
        
        Returns:
            数据库连接代码
        """
        if not self.data_source_analysis or 'data_sources' not in self.data_source_analysis:
            return "# 未检测到数据库连接信息"
        
        data_sources = self.data_source_analysis.get('data_sources', [])
        connection_code = []
        
        for source in data_sources:
            source_type = source.get('type', '').lower()
            if source_type in self.connection_templates:
                connection_info = source.get('connection_info', {})
                template_func = self.connection_templates[source_type]
                connection_code.append(template_func(connection_info))
        
        if not connection_code:
            return "# 未检测到支持的数据库连接信息"
        
        return "\n".join(connection_code) 