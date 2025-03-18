"""
Test Data Source Analyzer

用于测试数据源分析器功能
"""
import json
import sys
import os

# 添加父目录到sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.code_runner.data_source_analyzer import analyze_data_sources, analyze_databases
from app.code_runner.database_analyzer import analyze_database_usage


def test_comprehensive_example():
    """测试全面的SAS示例"""
    code = """
    /* 定义变量 */
    %let risk_lib = RISK_CALC;
    %let ref_schema = REFERENCE_DB;
    
    /* 定义多种类型的数据库 */
    libname dwh oracle user=dw_user password=xxxx path="DWPROD";
    libname staging sqlsvr server="sql-server-01" database=stage_db;
    libname mdatal bigquery server="project-id" dataset=mydataset;
    libname &risk_lib TERADATA server="teradata01" schema = "&ref_schema";
    libname RSK_VAR TERADATA server="teradata01" schema = "RISK_VAR_DB";
    
    /* 第一个PROC SQL块 */
    proc sql;
        /* 简单的SELECT查询 */
        select * from mdatal.project_metadata;
        
        /* JOIN操作跨多个数据库 */
        create table risk_positions as
        select a.position_id, 
               a.instrument_id,
               a.quantity,
               a.trade_date,
               b.price,
               c.factor_value,
               d.limit_value
        from dwh.trading_positions a
        join mdatal.market_data b 
          on a.instrument_id = b.instrument_id
         and a.trade_date = b.price_date
        left join RISK_CALC.risk_factors c
          on a.instrument_id = c.instrument_id
        left join staging.position_limits d
          on a.position_id = d.position_id
        where a.status = 'Active';
        
        /* UPDATE操作 */
        update staging.batch_control
        set status = 'Completed',
            end_time = current_timestamp
        where batch_id = 123;
    quit;
    
    /* 第二个PROC SQL块 */
    proc sql;
        /* INSERT操作 */
        insert into RSK_VAR.var_results
        select 
            current_date as calc_date,
            sum(case when confidence = 0.95 then var_value else 0 end) as var95,
            sum(case when confidence = 0.99 then var_value else 0 end) as var99
        from RISK_CALC.var_calcs
        where calc_date = current_date - 1;
        
        /* DELETE操作 */
        delete from mdatal.temp_calculations
        where created_date < current_date - 30;
        
        /* CREATE VIEW操作 */
        create view dwh.active_positions as
        select * from dwh.positions
        where status = 'Active';
        
        /* SELECT INTO操作 */
        select * into mdatal.backup_metadata
        from mdatal.project_metadata;
    quit;
    """
    
    # 分析所有数据源
    result = analyze_data_sources(code)
    result_obj = json.loads(result)
    
    # 输出结果
    print("全面数据源分析结果:")
    print(json.dumps(result_obj, indent=2))
    
    # 验证结果
    assert "databases" in result_obj, "应该包含数据库分析结果"
    dbs = result_obj["databases"]
    assert len(dbs) >= 5, "应该找到至少5个数据库"
    
    # 验证是否找到所有数据库
    db_names = [db["databaseName"] for db in dbs]
    expected_dbs = ["dwh", "staging", "mdatal", "REFERENCE_DB", "RISK_VAR_DB"]
    for expected_db in expected_dbs:
        assert expected_db in db_names, f"应该找到{expected_db}数据库"
    
    # 验证数据库类型
    db_types = {db["databaseName"]: db["databaseType"] for db in dbs}
    assert db_types["dwh"] == "oracle", "dwh应为oracle类型"
    assert db_types["staging"] == "sqlsvr", "staging应为sqlsvr类型"
    assert db_types["mdatal"] == "bigquery", "mdatal应为bigquery类型"
    assert db_types["REFERENCE_DB"] == "TERADATA", "REFERENCE_DB应为TERADATA类型"
    assert db_types["RISK_VAR_DB"] == "TERADATA", "RISK_VAR_DB应为TERADATA类型"
    
    # 验证表操作
    for db in dbs:
        if db["databaseName"] == "mdatal":
            tables = {table["tableName"]: table["operations"] for table in db["operationTables"]}
            assert "project_metadata" in tables, "mdatal应包含project_metadata表"
            assert "SELECT" in tables["project_metadata"], "project_metadata表应有SELECT操作"
            assert "temp_calculations" in tables, "mdatal应包含temp_calculations表"
            assert "DELETE" in tables["temp_calculations"], "temp_calculations表应有DELETE操作"
        
        if db["databaseName"] == "dwh":
            tables = {table["tableName"]: table["operations"] for table in db["operationTables"]}
            assert "trading_positions" in tables, "dwh应包含trading_positions表"
            assert "SELECT" in tables["trading_positions"], "trading_positions表应有SELECT操作"
            assert "active_positions" in tables, "dwh应包含active_positions表"
            assert "CREATE VIEW" in tables["active_positions"], "active_positions表应有CREATE VIEW操作"


def test_only_database_analysis():
    """仅测试数据库分析功能"""
    code = """
    /* 定义Teradata数据库 */
    libname RSK_VAR TERADATA server="teradata01" schema = "RISK_VAR_DB";
    
    /* SQL操作 */
    proc sql;
        /* 查询操作 */
        select * from RSK_VAR.var_results;
        
        /* 插入操作 */
        insert into RSK_VAR.audit_log
        values (current_timestamp, 'TEST', 'Testing');
    quit;
    """
    
    # 仅分析数据库
    result = analyze_databases(code)
    result_obj = json.loads(result)
    
    # 输出结果
    print("\n仅数据库分析结果:")
    print(json.dumps(result_obj, indent=2))
    
    # 验证结果
    assert len(result_obj) == 1, "应该找到一个数据库"
    assert result_obj[0]["databaseName"] == "RISK_VAR_DB", "数据库名应为RISK_VAR_DB"
    assert result_obj[0]["databaseType"] == "TERADATA", "数据库类型应为TERADATA"
    
    # 验证表操作
    tables = {table["tableName"]: table["operations"] for table in result_obj[0]["operationTables"]}
    assert "RSK_VAR" in tables, "应该包含RSK_VAR表"
    
    for table_name, operations in tables.items():
        if table_name == "var_results":
            assert "SELECT" in operations, "var_results表应有SELECT操作"
        elif table_name == "audit_log":
            assert "INSERT" in operations, "audit_log表应有INSERT操作"


def test_direct_database_analyzer():
    """直接测试数据库分析器"""
    code = """
    /* 定义数据库 */
    libname dwh oracle user=dw_user password=xxxx path="DWPROD";
    
    /* SQL操作 */
    proc sql;
        /* 查询并创建表 */
        create table report as
        select * from dwh.customers
        where status = 'Active';
    quit;
    """
    
    # 直接使用数据库分析器
    result = analyze_database_usage(code)
    result_obj = json.loads(result)
    
    # 输出结果
    print("\n直接数据库分析器结果:")
    print(json.dumps(result_obj, indent=2))
    
    # 验证结果
    assert len(result_obj) == 1, "应该找到一个数据库"
    assert result_obj[0]["databaseName"] == "dwh", "数据库名应为dwh"
    assert result_obj[0]["databaseType"] == "oracle", "数据库类型应为oracle"
    
    # 验证表操作
    tables = {table["tableName"]: table["operations"] for table in result_obj[0]["operationTables"]}
    assert "customers" in tables, "应该包含customers表"
    assert "SELECT" in tables["customers"], "customers表应有SELECT操作"


if __name__ == "__main__":
    try:
        print("开始测试数据源分析器...")
        test_comprehensive_example()
        test_only_database_analysis()
        test_direct_database_analyzer()
        print("\n所有测试通过！数据源分析器功能正常。")
    except Exception as e:
        print(f"\n测试失败: {str(e)}") 