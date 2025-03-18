"""
Test Database Analyzer

用于测试数据库分析器功能
"""
import json
import sys
import os
from database_analyzer import analyze_database_usage


def test_generic_database():
    """测试普通外部数据库分析"""
    code = """
    /* 定义普通外部数据库 */
    libname mdatal bigquery server="project-id" dataset=mydataset;
    
    /* 使用数据库表 */
    proc sql;
        /* 简单的SELECT查询 */
        select * from mdatal.project_metadata;
        
        /* JOIN操作 */
        select a.*, b.status 
        from mdatal.users as a
        join mdatal.project_metadata as b
        on a.project_id = b.id;
        
        /* UPDATE操作 */
        update mdatal.users
        set status = 'Active'
        where last_login > '2023-01-01';
        
        /* INSERT操作 */
        insert into mdatal.logs
        select current_timestamp, 'test', 'INFO'
        from mdatal.config;
        
        /* DELETE操作 */
        delete from mdatal.temp_data
        where created_date < '2023-01-01';
        
        /* CREATE VIEW操作 */
        create view mdatal.active_users as
        select * from mdatal.users
        where status = 'Active';
        
        /* SELECT INTO操作 */
        select * into mdatal.backup_users
        from mdatal.users;
    quit;
    """
    
    result = analyze_database_usage(code)
    result_obj = json.loads(result)
    
    # 输出结果
    print("普通外部数据库分析结果:")
    print(json.dumps(result_obj, indent=2))
    
    # 验证结果
    assert len(result_obj) == 1, "应该找到一个数据库"
    assert result_obj[0]["databaseName"] == "mdatal", "数据库名应为mdatal"
    assert result_obj[0]["databaseType"] == "bigquery", "数据库类型应为bigquery"
    
    # 验证表操作
    tables_ops = {table["tableName"]: table["operations"] for table in result_obj[0]["operationTables"]}
    assert "project_metadata" in tables_ops, "应该包含project_metadata表"
    assert "SELECT" in tables_ops["project_metadata"], "project_metadata表应有SELECT操作"
    
    assert "users" in tables_ops, "应该包含users表"
    assert set(["SELECT", "UPDATE"]).issubset(set(tables_ops["users"])), "users表应有SELECT和UPDATE操作"
    
    assert "logs" in tables_ops, "应该包含logs表"
    assert "INSERT" in tables_ops["logs"], "logs表应有INSERT操作"
    
    assert "temp_data" in tables_ops, "应该包含temp_data表"
    assert "DELETE" in tables_ops["temp_data"], "temp_data表应有DELETE操作"
    
    assert "active_users" in tables_ops, "应该包含active_users表"
    assert "CREATE VIEW" in tables_ops["active_users"], "active_users表应有CREATE VIEW操作"
    
    assert "backup_users" in tables_ops, "应该包含backup_users表"
    assert "SELECT INTO" in tables_ops["backup_users"], "backup_users表应有SELECT INTO操作"


def test_teradata_database():
    """测试Teradata数据库分析"""
    code = """
    /* 定义变量 */
    %let my_table = RISK_DATA;
    
    /* 定义Teradata数据库 */
    libname RSK_LABL TERADATA server="tdprod" schema = "RISK_DB";
    libname &my_table TERADATA server="tdprod" schema = "RISK_PROD";
    
    /* 使用数据库表 */
    proc sql;
        /* 简单的SELECT查询 */
        select * from RSK_LABL.risk_factors;
        
        /* JOIN操作 */
        select a.*, b.factor 
        from RSK_LABL.positions as a
        join RISK_DATA.scenarios as b
        on a.scenario_id = b.id;
        
        /* UPDATE操作 */
        update RSK_LABL.parameters
        set value = 0.05
        where name = 'interest_rate';
        
        /* INSERT操作 */
        insert into RISK_DATA.audit_log
        values (current_timestamp, 'UPDATE', 'Changed parameters');
    quit;
    """
    
    result = analyze_database_usage(code)
    result_obj = json.loads(result)
    
    # 输出结果
    print("\nTeradata数据库分析结果:")
    print(json.dumps(result_obj, indent=2))
    
    # 验证结果
    assert len(result_obj) == 2, "应该找到两个数据库"
    
    # 验证第一个数据库
    db1 = next((db for db in result_obj if db["databaseName"] == "RISK_DB"), None)
    assert db1 is not None, "应该找到RISK_DB数据库"
    assert db1["databaseType"] == "TERADATA", "数据库类型应为TERADATA"
    
    # 验证第一个数据库的表操作
    tables_ops_1 = {table["tableName"]: table["operations"] for table in db1["operationTables"]}
    assert "RSK_LABL" in tables_ops_1, "应该包含RSK_LABL表"
    assert "risk_factors" in tables_ops_1 or "positions" in tables_ops_1 or "parameters" in tables_ops_1, "应该包含相关操作表"
    
    # 验证第二个数据库
    db2 = next((db for db in result_obj if db["databaseName"] == "RISK_PROD"), None)
    assert db2 is not None, "应该找到RISK_PROD数据库"
    assert db2["databaseType"] == "TERADATA", "数据库类型应为TERADATA"
    
    # 验证第二个数据库的表操作
    tables_ops_2 = {table["tableName"]: table["operations"] for table in db2["operationTables"]}
    assert "RISK_DATA" in tables_ops_2, "应该包含RISK_DATA表"
    assert "scenarios" in tables_ops_2 or "audit_log" in tables_ops_2, "应该包含相关操作表"


def test_multiple_databases():
    """测试多数据库分析"""
    code = """
    /* 定义多个数据库 */
    libname dwh oracle user=user1 password=pass1 path="DWPROD";
    libname staging sqlsvr server="sqlserver01" database=stage;
    libname RSK_CALC TERADATA server="tdprod" schema = "RISK_CALC";
    
    proc sql;
        /* 跨数据库查询 */
        create table combined as
        select a.*, b.risk_score, c.limit
        from dwh.customers a
        join RSK_CALC.risk_scores b on a.id = b.customer_id
        join staging.credit_limits c on a.id = c.customer_id
        where a.status = 'Active';
        
        /* 更新操作 */
        update staging.audit_log
        set status = 'Processed'
        where process_date = today();
        
        /* 插入操作 */
        insert into dwh.logs
        select current_timestamp, 'Data load completed', 'INFO'
        from staging.batch_control;
    quit;
    """
    
    result = analyze_database_usage(code)
    result_obj = json.loads(result)
    
    # 输出结果
    print("\n多数据库分析结果:")
    print(json.dumps(result_obj, indent=2))
    
    # 验证结果
    assert len(result_obj) >= 3, "应该找到至少三个数据库"
    
    # 验证Oracle数据库
    oracle_db = next((db for db in result_obj if db["databaseType"] == "oracle"), None)
    assert oracle_db is not None, "应该找到Oracle数据库"
    assert oracle_db["databaseName"] == "dwh", "Oracle数据库名应为dwh"
    
    # 验证SQL Server数据库
    sqlsvr_db = next((db for db in result_obj if db["databaseType"] == "sqlsvr"), None)
    assert sqlsvr_db is not None, "应该找到SQL Server数据库"
    assert sqlsvr_db["databaseName"] == "staging", "SQL Server数据库名应为staging"
    
    # 验证Teradata数据库
    teradata_db = next((db for db in result_obj if db["databaseType"] == "TERADATA"), None)
    assert teradata_db is not None, "应该找到Teradata数据库"
    assert teradata_db["databaseName"] == "RISK_CALC", "Teradata数据库名应为RISK_CALC"


if __name__ == "__main__":
    try:
        print("开始测试数据库分析器...")
        test_generic_database()
        test_teradata_database()
        test_multiple_databases()
        print("\n所有测试通过！数据库分析器功能正常。")
    except Exception as e:
        print(f"\n测试失败: {str(e)}") 