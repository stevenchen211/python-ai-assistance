"""
Database Analyzer Module

Used to analyze database usage in SAS code
"""
import re
import json
from typing import Dict, List, Any, Set


class DatabaseAnalyzer:
    """Database Analyzer"""
    
    def __init__(self, code: str):
        """
        Initialize database analyzer
        
        Args:
            code: SAS code
        """
        self.code = code
        self.databases = []
        self.variables = {}  # Store variable definitions
    
    def _parse_variables(self):
        """Parse SAS variable definitions"""
        # Match variable definition pattern %let varname = value;
        variable_pattern = r'%let\s+(\w+)\s*=\s*([^;]+);'
        matches = re.finditer(variable_pattern, self.code, re.IGNORECASE)
        
        for match in matches:
            var_name = match.group(1).strip()
            value = match.group(2).strip()
            self.variables[var_name] = value
    
    def _resolve_variable(self, var_ref: str) -> str:
        """
        Resolve variable reference
        
        Args:
            var_ref: Variable reference, e.g. &varname
            
        Returns:
            Resolved variable value
        """
        if var_ref.startswith('&'):
            var_name = var_ref[1:]
            return self.variables.get(var_name, var_ref)
        return var_ref
    
    def _parse_generic_libname(self) -> List[Dict[str, Any]]:
        """
        Parse generic external database LIBNAME commands
        
        Returns:
            List of database information
        """
        databases = []
        
        # Match LIBNAME command pattern
        libname_pattern = r'libname\s+(\w+)\s+(\w+)([^;]*);'
        matches = re.finditer(libname_pattern, self.code, re.IGNORECASE)
        
        for match in matches:
            db_name = match.group(1).strip()
            db_type = match.group(2).strip()
            
            # Skip Teradata type, this will be handled in a dedicated function
            if db_type.upper() == 'TERADATA':
                continue
                
            # Get connection details
            connection_detail = match.group(3).strip() if match.group(3) else ""
            
            # Add database information
            databases.append({
                "databaseName": db_name,
                "databaseType": db_type,
                "connectionDetail": connection_detail,
                "operationTables": []
            })
        
        return databases
    
    def _parse_teradata_libname(self) -> List[Dict[str, Any]]:
        """
        Parse Teradata LIBNAME commands
        
        Returns:
            List of database information
        """
        databases = []
        
        # Match Teradata LIBNAME command pattern (case insensitive)
        teradata_pattern = r'libname\s+(\w+|\&\w+)\s+TERADATA\s+([^;]*);'
        matches = re.finditer(teradata_pattern, self.code, re.IGNORECASE)
        
        for match in matches:
            table_name = match.group(1).strip()
            connection_info = match.group(2).strip()
            
            # Resolve variable reference
            if table_name.startswith('&'):
                table_name = self._resolve_variable(table_name)
            
            # Try to extract schema from connection info
            schema_match = re.search(r'schema\s*=\s*["\']?([^"\'\s;]+)["\']?', connection_info, re.IGNORECASE)
            db_name = schema_match.group(1) if schema_match else "UNKNOWN"
            
            # If schema itself is a variable reference, resolve it
            if db_name.startswith('&'):
                db_name = self._resolve_variable(db_name)
            
            # Add database information
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
        """Extract SQL operations and populate database information"""
        # Find all PROC SQL blocks
        sql_blocks_pattern = r'proc\s+sql;(.*?)quit;'
        sql_blocks = re.finditer(sql_blocks_pattern, self.code, re.IGNORECASE | re.DOTALL)
        
        for sql_block_match in sql_blocks:
            sql_code = sql_block_match.group(1)
            
            # Process table operations for each database
            for db in self.databases:
                db_name = db["databaseName"]
                table_ops = {}  # Temporary storage for table information {table_name: [operations]}
                
                # For TERADATA type databases, also process tables defined in libname
                if db["databaseType"] == "TERADATA":
                    for table_info in db["operationTables"]:
                        libname_table = table_info["tableName"]
                        
                        # Record libname table operations
                        if "operations" not in table_info or not table_info["operations"]:
                            table_info["operations"] = []
                        
                        # Extract operations related to this libname
                        # Find SELECT operations
                        select_pattern = r'select\s+.*?\s+from\s+(?:' + libname_table + r'\.)(\w+)'
                        select_matches = re.finditer(select_pattern, sql_code, re.IGNORECASE | re.DOTALL)
                        for select_match in select_matches:
                            table_name = select_match.group(1)
                            if table_name not in table_ops:
                                table_ops[table_name] = []
                            if "SELECT" not in table_ops[table_name]:
                                table_ops[table_name].append("SELECT")
                            # Add query operation to libname table
                            if "SELECT" not in table_info["operations"]:
                                table_info["operations"].append("SELECT")
                        
                        # Find JOIN operations
                        join_pattern = r'join\s+(?:' + libname_table + r'\.)(\w+)'
                        join_matches = re.finditer(join_pattern, sql_code, re.IGNORECASE)
                        for join_match in join_matches:
                            table_name = join_match.group(1)
                            if table_name not in table_ops:
                                table_ops[table_name] = []
                            if "SELECT" not in table_ops[table_name]:
                                table_ops[table_name].append("SELECT")
                            # Add query operation to libname table
                            if "SELECT" not in table_info["operations"]:
                                table_info["operations"].append("SELECT")
                        
                        # Find UPDATE operations
                        update_pattern = r'update\s+(?:' + libname_table + r'\.)(\w+)'
                        update_matches = re.finditer(update_pattern, sql_code, re.IGNORECASE)
                        for update_match in update_matches:
                            table_name = update_match.group(1)
                            if table_name not in table_ops:
                                table_ops[table_name] = []
                            if "UPDATE" not in table_ops[table_name]:
                                table_ops[table_name].append("UPDATE")
                            # Add update operation to libname table
                            if "UPDATE" not in table_info["operations"]:
                                table_info["operations"].append("UPDATE")
                        
                        # Find INSERT operations
                        insert_pattern = r'insert\s+(?:into\s+)?(?:' + libname_table + r'\.)(\w+)'
                        insert_matches = re.finditer(insert_pattern, sql_code, re.IGNORECASE)
                        for insert_match in insert_matches:
                            table_name = insert_match.group(1)
                            if table_name not in table_ops:
                                table_ops[table_name] = []
                            if "INSERT" not in table_ops[table_name]:
                                table_ops[table_name].append("INSERT")
                            # Add insert operation to libname table
                            if "INSERT" not in table_info["operations"]:
                                table_info["operations"].append("INSERT")
                        
                        # Find DELETE operations
                        delete_pattern = r'delete\s+from\s+(?:' + libname_table + r'\.)(\w+)'
                        delete_matches = re.finditer(delete_pattern, sql_code, re.IGNORECASE)
                        for delete_match in delete_matches:
                            table_name = delete_match.group(1)
                            if table_name not in table_ops:
                                table_ops[table_name] = []
                            if "DELETE" not in table_ops[table_name]:
                                table_ops[table_name].append("DELETE")
                            # Add delete operation to libname table
                            if "DELETE" not in table_info["operations"]:
                                table_info["operations"].append("DELETE")
                        
                        # Find CREATE VIEW operations
                        create_view_pattern = r'create\s+view\s+(?:' + libname_table + r'\.)(\w+)'
                        create_view_matches = re.finditer(create_view_pattern, sql_code, re.IGNORECASE)
                        for create_view_match in create_view_matches:
                            table_name = create_view_match.group(1)
                            if table_name not in table_ops:
                                table_ops[table_name] = []
                            if "CREATE VIEW" not in table_ops[table_name]:
                                table_ops[table_name].append("CREATE VIEW")
                            # Add view operation to libname table
                            if "CREATE VIEW" not in table_info["operations"]:
                                table_info["operations"].append("CREATE VIEW")
                        
                        # Find SELECT INTO operations
                        select_into_pattern = r'select\s+.*?\s+into\s+(?:' + libname_table + r'\.)(\w+)'
                        select_into_matches = re.finditer(select_into_pattern, sql_code, re.IGNORECASE | re.DOTALL)
                        for select_into_match in select_into_matches:
                            table_name = select_into_match.group(1)
                            if table_name not in table_ops:
                                table_ops[table_name] = []
                            if "SELECT INTO" not in table_ops[table_name]:
                                table_ops[table_name].append("SELECT INTO")
                            # Add query and insert operation to libname table
                            if "SELECT INTO" not in table_info["operations"]:
                                table_info["operations"].append("SELECT INTO")
                
                # Regular database queries
                # Find SELECT operations
                select_pattern = r'select\s+.*?\s+from\s+(?:' + db_name + r'\.)(\w+)'
                select_matches = re.finditer(select_pattern, sql_code, re.IGNORECASE | re.DOTALL)
                for select_match in select_matches:
                    table_name = select_match.group(1)
                    if table_name not in table_ops:
                        table_ops[table_name] = []
                    if "SELECT" not in table_ops[table_name]:
                        table_ops[table_name].append("SELECT")
                
                # Find JOIN operations
                join_pattern = r'join\s+(?:' + db_name + r'\.)(\w+)'
                join_matches = re.finditer(join_pattern, sql_code, re.IGNORECASE)
                for join_match in join_matches:
                    table_name = join_match.group(1)
                    if table_name not in table_ops:
                        table_ops[table_name] = []
                    if "SELECT" not in table_ops[table_name]:
                        table_ops[table_name].append("SELECT")
                
                # Find UPDATE operations
                update_pattern = r'update\s+(?:' + db_name + r'\.)(\w+)'
                update_matches = re.finditer(update_pattern, sql_code, re.IGNORECASE)
                for update_match in update_matches:
                    table_name = update_match.group(1)
                    if table_name not in table_ops:
                        table_ops[table_name] = []
                    if "UPDATE" not in table_ops[table_name]:
                        table_ops[table_name].append("UPDATE")
                
                # Find INSERT operations
                insert_pattern = r'insert\s+(?:into\s+)?(?:' + db_name + r'\.)(\w+)'
                insert_matches = re.finditer(insert_pattern, sql_code, re.IGNORECASE)
                for insert_match in insert_matches:
                    table_name = insert_match.group(1)
                    if table_name not in table_ops:
                        table_ops[table_name] = []
                    if "INSERT" not in table_ops[table_name]:
                        table_ops[table_name].append("INSERT")
                
                # Find DELETE operations
                delete_pattern = r'delete\s+from\s+(?:' + db_name + r'\.)(\w+)'
                delete_matches = re.finditer(delete_pattern, sql_code, re.IGNORECASE)
                for delete_match in delete_matches:
                    table_name = delete_match.group(1)
                    if table_name not in table_ops:
                        table_ops[table_name] = []
                    if "DELETE" not in table_ops[table_name]:
                        table_ops[table_name].append("DELETE")
                
                # Find CREATE VIEW operations
                create_view_pattern = r'create\s+view\s+(?:' + db_name + r'\.)(\w+)'
                create_view_matches = re.finditer(create_view_pattern, sql_code, re.IGNORECASE)
                for create_view_match in create_view_matches:
                    table_name = create_view_match.group(1)
                    if table_name not in table_ops:
                        table_ops[table_name] = []
                    if "CREATE VIEW" not in table_ops[table_name]:
                        table_ops[table_name].append("CREATE VIEW")
                
                # Find SELECT INTO operations
                select_into_pattern = r'select\s+.*?\s+into\s+(?:' + db_name + r'\.)(\w+)'
                select_into_matches = re.finditer(select_into_pattern, sql_code, re.IGNORECASE | re.DOTALL)
                for select_into_match in select_into_matches:
                    table_name = select_into_match.group(1)
                    if table_name not in table_ops:
                        table_ops[table_name] = []
                    if "SELECT INTO" not in table_ops[table_name]:
                        table_ops[table_name].append("SELECT INTO")
                
                # Update database table operation information
                for table_name, operations in table_ops.items():
                    # Check if table already exists
                    table_exists = False
                    for table_info in db["operationTables"]:
                        if table_info["tableName"] == table_name:
                            # Merge operations
                            for op in operations:
                                if op not in table_info["operations"]:
                                    table_info["operations"].append(op)
                            table_exists = True
                            break
                    
                    # Add new table
                    if not table_exists:
                        db["operationTables"].append({
                            "tableName": table_name,
                            "operations": operations
                        })
    
    def analyze(self) -> str:
        """
        Analyze database usage in SAS code
        
        Returns:
            Database usage information in JSON format
        """
        # Parse variable definitions
        self._parse_variables()
        
        # Parse database definitions
        generic_dbs = self._parse_generic_libname()
        teradata_dbs = self._parse_teradata_libname()
        
        # Merge all database information
        self.databases = generic_dbs + teradata_dbs
        
        # Extract SQL operations
        self._extract_sql_operations()
        
        # Filter out tables with no operations
        for db in self.databases:
            db["operationTables"] = [table for table in db["operationTables"] if table["operations"]]
            
        # Filter out databases with no table operations
        self.databases = [db for db in self.databases if db["operationTables"]]
        
        # Return results in JSON format
        return json.dumps(self.databases, indent=2)


def analyze_database_usage(code: str) -> str:
    """
    Analyze database usage in SAS code
    
    Args:
        code: SAS code
        
    Returns:
        Database usage information in JSON format
    """
    analyzer = DatabaseAnalyzer(code)
    return analyzer.analyze() 