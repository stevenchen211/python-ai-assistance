"""
Database Analyzer Module

用于分析SAS代码中的数据库使用情况
"""
import re
import json
from typing import Dict, List, Any, Set


class DatabaseAnalyzer:
    """数据库分析器"""
    
    def __init__(self, code: str):
        """
        初始化数据库分析器
        
        Args:
            code: SAS代码
        """
        self.code = code
        self.databases = []
        self.variables = {}  # 存储变量定义
    
    def _parse_variables(self):
        """解析SAS变量定义"""
        # 匹配变量定义模式 %let varname = value;
        variable_pattern = r'%let\s+(\w+)\s*=\s*([^;]+);'
        matches = re.finditer(variable_pattern, self.code, re.IGNORECASE)
        
        for match in matches:
            var_name = match.group(1).strip()
            value = match.group(2).strip()
            self.variables[var_name] = value
    
    def _resolve_variable(self, var_ref: str) -> str:
        """
        解析变量引用
        
        Args:
            var_ref: 变量引用，例如 &varname
            
        Returns:
            解析后的变量值
        """
        if var_ref.startswith('&'):
            var_name = var_ref[1:]
            return self.variables.get(var_name, var_ref)
        return var_ref
    
    def _parse_generic_libname(self) -> List[Dict[str, Any]]:
        """
        解析普通外部数据库的LIBNAME命令
        
        Returns:
            数据库信息列表
        """
        databases = []
        
        # 匹配LIBNAME命令模式
        libname_pattern = r'libname\s+(\w+)\s+(\w+)([^;]*);'
        matches = re.finditer(libname_pattern, self.code, re.IGNORECASE)
        
        for match in matches:
            db_name = match.group(1).strip()
            db_type = match.group(2).strip()
            
            # 跳过Teradata类型，这将在专门的函数中处理
            if db_type.upper() == 'TERADATA':
                continue
                
            # 获取连接详情
            connection_detail = match.group(3).strip() if match.group(3) else ""
            
            # 添加数据库信息
            databases.append({
                "databaseName": db_name,
                "databaseType": db_type,
                "connectionDetail": connection_detail,
                "operationTables": []
            })
        
        return databases
    
    def _parse_teradata_libname(self) -> List[Dict[str, Any]]:
        """
        解析Teradata的LIBNAME命令
        
        Returns:
            数据库信息列表
        """
        databases = []
        
        # 匹配Teradata的LIBNAME命令模式 (不区分大小写)
        teradata_pattern = r'libname\s+(\w+|\&\w+)\s+TERADATA\s+([^;]*);'
        matches = re.finditer(teradata_pattern, self.code, re.IGNORECASE)
        
        for match in matches:
            table_name = match.group(1).strip()
            connection_info = match.group(2).strip()
            
            # 解析变量引用
            if table_name.startswith('&'):
                table_name = self._resolve_variable(table_name)
            
            # 尝试从连接信息中提取schema
            schema_match = re.search(r'schema\s*=\s*["\']?([^"\'\s;]+)["\']?', connection_info, re.IGNORECASE)
            db_name = schema_match.group(1) if schema_match else "UNKNOWN"
            
            # 如果schema本身是变量引用，解析它
            if db_name.startswith('&'):
                db_name = self._resolve_variable(db_name)
            
            # 添加数据库信息
            databases.append({
                "databaseName": db_name,
                "databaseType": "TERADATA",
                "connectionDetail": connection_info,
                "operationTables": [{
                    "tableName": table_name,
                    "operations": []
                }]
            })
        
        return databases
    
    def _extract_sql_operations(self):
        """提取SQL操作并填充到数据库信息中"""
        # 查找所有PROC SQL块
        sql_blocks_pattern = r'proc\s+sql;(.*?)quit;'
        sql_blocks = re.finditer(sql_blocks_pattern, self.code, re.IGNORECASE | re.DOTALL)
        
        for sql_block_match in sql_blocks:
            sql_code = sql_block_match.group(1)
            
            # 处理每个数据库的表操作
            for db in self.databases:
                db_name = db["databaseName"]
                table_ops = {}  # 临时存储表信息 {表名: [操作列表]}
                
                # 对于TERADATA类型的数据库，还需要处理libname定义的表
                if db["databaseType"] == "TERADATA":
                    for table_info in db["operationTables"]:
                        libname_table = table_info["tableName"]
                        
                        # 记录libname表的操作
                        if "operations" not in table_info or not table_info["operations"]:
                            table_info["operations"] = []
                        
                        # 提取此libname相关的操作
                        # 查找SELECT操作
                        select_pattern = r'select\s+.*?\s+from\s+(?:' + libname_table + r'\.)(\w+)'
                        select_matches = re.finditer(select_pattern, sql_code, re.IGNORECASE | re.DOTALL)
                        for select_match in select_matches:
                            table_name = select_match.group(1)
                            if table_name not in table_ops:
                                table_ops[table_name] = []
                            if "SELECT" not in table_ops[table_name]:
                                table_ops[table_name].append("SELECT")
                            # 添加查询操作到libname表
                            if "SELECT" not in table_info["operations"]:
                                table_info["operations"].append("SELECT")
                        
                        # 查找JOIN操作
                        join_pattern = r'join\s+(?:' + libname_table + r'\.)(\w+)'
                        join_matches = re.finditer(join_pattern, sql_code, re.IGNORECASE)
                        for join_match in join_matches:
                            table_name = join_match.group(1)
                            if table_name not in table_ops:
                                table_ops[table_name] = []
                            if "SELECT" not in table_ops[table_name]:
                                table_ops[table_name].append("SELECT")
                            # 添加查询操作到libname表
                            if "SELECT" not in table_info["operations"]:
                                table_info["operations"].append("SELECT")
                        
                        # 查找UPDATE操作
                        update_pattern = r'update\s+(?:' + libname_table + r'\.)(\w+)'
                        update_matches = re.finditer(update_pattern, sql_code, re.IGNORECASE)
                        for update_match in update_matches:
                            table_name = update_match.group(1)
                            if table_name not in table_ops:
                                table_ops[table_name] = []
                            if "UPDATE" not in table_ops[table_name]:
                                table_ops[table_name].append("UPDATE")
                            # 添加更新操作到libname表
                            if "UPDATE" not in table_info["operations"]:
                                table_info["operations"].append("UPDATE")
                        
                        # 查找INSERT操作
                        insert_pattern = r'insert\s+(?:into\s+)?(?:' + libname_table + r'\.)(\w+)'
                        insert_matches = re.finditer(insert_pattern, sql_code, re.IGNORECASE)
                        for insert_match in insert_matches:
                            table_name = insert_match.group(1)
                            if table_name not in table_ops:
                                table_ops[table_name] = []
                            if "INSERT" not in table_ops[table_name]:
                                table_ops[table_name].append("INSERT")
                            # 添加插入操作到libname表
                            if "INSERT" not in table_info["operations"]:
                                table_info["operations"].append("INSERT")
                        
                        # 查找DELETE操作
                        delete_pattern = r'delete\s+from\s+(?:' + libname_table + r'\.)(\w+)'
                        delete_matches = re.finditer(delete_pattern, sql_code, re.IGNORECASE)
                        for delete_match in delete_matches:
                            table_name = delete_match.group(1)
                            if table_name not in table_ops:
                                table_ops[table_name] = []
                            if "DELETE" not in table_ops[table_name]:
                                table_ops[table_name].append("DELETE")
                            # 添加删除操作到libname表
                            if "DELETE" not in table_info["operations"]:
                                table_info["operations"].append("DELETE")
                        
                        # 查找CREATE VIEW操作
                        create_view_pattern = r'create\s+view\s+(?:' + libname_table + r'\.)(\w+)'
                        create_view_matches = re.finditer(create_view_pattern, sql_code, re.IGNORECASE)
                        for create_view_match in create_view_matches:
                            table_name = create_view_match.group(1)
                            if table_name not in table_ops:
                                table_ops[table_name] = []
                            if "CREATE VIEW" not in table_ops[table_name]:
                                table_ops[table_name].append("CREATE VIEW")
                            # 添加视图操作到libname表
                            if "CREATE VIEW" not in table_info["operations"]:
                                table_info["operations"].append("CREATE VIEW")
                        
                        # 查找SELECT INTO操作
                        select_into_pattern = r'select\s+.*?\s+into\s+(?:' + libname_table + r'\.)(\w+)'
                        select_into_matches = re.finditer(select_into_pattern, sql_code, re.IGNORECASE | re.DOTALL)
                        for select_into_match in select_into_matches:
                            table_name = select_into_match.group(1)
                            if table_name not in table_ops:
                                table_ops[table_name] = []
                            if "SELECT INTO" not in table_ops[table_name]:
                                table_ops[table_name].append("SELECT INTO")
                            # 添加查询并插入操作到libname表
                            if "SELECT INTO" not in table_info["operations"]:
                                table_info["operations"].append("SELECT INTO")
                
                # 普通的数据库查询
                # 查找SELECT操作
                select_pattern = r'select\s+.*?\s+from\s+(?:' + db_name + r'\.)(\w+)'
                select_matches = re.finditer(select_pattern, sql_code, re.IGNORECASE | re.DOTALL)
                for select_match in select_matches:
                    table_name = select_match.group(1)
                    if table_name not in table_ops:
                        table_ops[table_name] = []
                    if "SELECT" not in table_ops[table_name]:
                        table_ops[table_name].append("SELECT")
                
                # 查找JOIN操作
                join_pattern = r'join\s+(?:' + db_name + r'\.)(\w+)'
                join_matches = re.finditer(join_pattern, sql_code, re.IGNORECASE)
                for join_match in join_matches:
                    table_name = join_match.group(1)
                    if table_name not in table_ops:
                        table_ops[table_name] = []
                    if "SELECT" not in table_ops[table_name]:
                        table_ops[table_name].append("SELECT")
                
                # 查找UPDATE操作
                update_pattern = r'update\s+(?:' + db_name + r'\.)(\w+)'
                update_matches = re.finditer(update_pattern, sql_code, re.IGNORECASE)
                for update_match in update_matches:
                    table_name = update_match.group(1)
                    if table_name not in table_ops:
                        table_ops[table_name] = []
                    if "UPDATE" not in table_ops[table_name]:
                        table_ops[table_name].append("UPDATE")
                
                # 查找INSERT操作
                insert_pattern = r'insert\s+(?:into\s+)?(?:' + db_name + r'\.)(\w+)'
                insert_matches = re.finditer(insert_pattern, sql_code, re.IGNORECASE)
                for insert_match in insert_matches:
                    table_name = insert_match.group(1)
                    if table_name not in table_ops:
                        table_ops[table_name] = []
                    if "INSERT" not in table_ops[table_name]:
                        table_ops[table_name].append("INSERT")
                
                # 查找DELETE操作
                delete_pattern = r'delete\s+from\s+(?:' + db_name + r'\.)(\w+)'
                delete_matches = re.finditer(delete_pattern, sql_code, re.IGNORECASE)
                for delete_match in delete_matches:
                    table_name = delete_match.group(1)
                    if table_name not in table_ops:
                        table_ops[table_name] = []
                    if "DELETE" not in table_ops[table_name]:
                        table_ops[table_name].append("DELETE")
                
                # 查找CREATE VIEW操作
                create_view_pattern = r'create\s+view\s+(?:' + db_name + r'\.)(\w+)'
                create_view_matches = re.finditer(create_view_pattern, sql_code, re.IGNORECASE)
                for create_view_match in create_view_matches:
                    table_name = create_view_match.group(1)
                    if table_name not in table_ops:
                        table_ops[table_name] = []
                    if "CREATE VIEW" not in table_ops[table_name]:
                        table_ops[table_name].append("CREATE VIEW")
                
                # 查找SELECT INTO操作
                select_into_pattern = r'select\s+.*?\s+into\s+(?:' + db_name + r'\.)(\w+)'
                select_into_matches = re.finditer(select_into_pattern, sql_code, re.IGNORECASE | re.DOTALL)
                for select_into_match in select_into_matches:
                    table_name = select_into_match.group(1)
                    if table_name not in table_ops:
                        table_ops[table_name] = []
                    if "SELECT INTO" not in table_ops[table_name]:
                        table_ops[table_name].append("SELECT INTO")
                
                # 更新数据库表操作信息
                for table_name, operations in table_ops.items():
                    # 检查表是否已存在
                    table_exists = False
                    for table_info in db["operationTables"]:
                        if table_info["tableName"] == table_name:
                            # 合并操作
                            for op in operations:
                                if op not in table_info["operations"]:
                                    table_info["operations"].append(op)
                            table_exists = True
                            break
                    
                    # 添加新表
                    if not table_exists:
                        db["operationTables"].append({
                            "tableName": table_name,
                            "operations": operations
                        })
    
    def analyze(self) -> str:
        """
        分析SAS代码中的数据库使用情况
        
        Returns:
            JSON格式的数据库使用信息
        """
        # 解析变量定义
        self._parse_variables()
        
        # 解析数据库定义
        generic_dbs = self._parse_generic_libname()
        teradata_dbs = self._parse_teradata_libname()
        
        # 合并所有数据库信息
        self.databases = generic_dbs + teradata_dbs
        
        # 提取SQL操作
        self._extract_sql_operations()
        
        # 过滤掉没有操作的表
        for db in self.databases:
            db["operationTables"] = [table for table in db["operationTables"] if table["operations"]]
            
        # 过滤掉没有表操作的数据库
        self.databases = [db for db in self.databases if db["operationTables"]]
        
        # 返回JSON格式的结果
        return json.dumps(self.databases, indent=2)


def analyze_database_usage(code: str) -> str:
    """
    分析SAS代码中的数据库使用情况
    
    Args:
        code: SAS代码
        
    Returns:
        JSON格式的数据库使用信息
    """
    analyzer = DatabaseAnalyzer(code)
    return analyzer.analyze() 