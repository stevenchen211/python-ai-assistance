"""
Test Data Source Analyzer

Used to test data source analyzer functionality
"""
import json
import sys
import os

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.code_runner.data_source_analyzer import analyze_data_sources, analyze_databases
from app.code_runner.database_analyzer import analyze_database_usage


def test_comprehensive_example():
    """Test comprehensive SAS example"""
    code = """
    /* Define variables */
    %let risk_lib = RISK_CALC;
    %let ref_schema = REFERENCE_DB;
    
    /* Define multiple database types */
    libname dwh oracle user=dw_user password=xxxx path="DWPROD";
    libname staging sqlsvr server="sql-server-01" database=stage_db;
    libname mdatal bigquery server="project-id" dataset=mydataset;
    libname &risk_lib TERADATA server="teradata01" schema = "&ref_schema";
    libname RSK_VAR TERADATA server="teradata01" schema = "RISK_VAR_DB";
    
    /* First PROC SQL block */
    proc sql;
        /* Simple SELECT query */
        select * from mdatal.project_metadata;
        
        /* JOIN operation across multiple databases */
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
        
        /* UPDATE operation */
        update staging.batch_control
        set status = 'Completed',
            end_time = current_timestamp
        where batch_id = 123;
    quit;
    
    /* Second PROC SQL block */
    proc sql;
        /* INSERT operation */
        insert into RSK_VAR.var_results
        select 
            current_date as calc_date,
            sum(case when confidence = 0.95 then var_value else 0 end) as var95,
            sum(case when confidence = 0.99 then var_value else 0 end) as var99
        from RISK_CALC.var_calcs
        where calc_date = current_date - 1;
        
        /* DELETE operation */
        delete from mdatal.temp_calculations
        where created_date < current_date - 30;
        
        /* CREATE VIEW operation */
        create view dwh.active_positions as
        select * from dwh.positions
        where status = 'Active';
        
        /* SELECT INTO operation */
        select * into mdatal.backup_metadata
        from mdatal.project_metadata;
    quit;
    """
    
    # Analyze all data sources
    result = analyze_data_sources(code)
    result_obj = json.loads(result)
    
    # Output results
    print("Comprehensive data source analysis results:")
    print(json.dumps(result_obj, indent=2))
    
    # Verify results
    assert "databases" in result_obj, "Should include database analysis results"
    dbs = result_obj["databases"]
    assert len(dbs) >= 5, "Should find at least 5 databases"
    
    # Verify all databases are found
    db_names = [db["databaseName"] for db in dbs]
    expected_dbs = ["dwh", "staging", "mdatal", "REFERENCE_DB", "RISK_VAR_DB"]
    for expected_db in expected_dbs:
        assert expected_db in db_names, f"Should find {expected_db} database"
    
    # Verify database types
    db_types = {db["databaseName"]: db["databaseType"] for db in dbs}
    assert db_types["dwh"] == "oracle", "dwh should be oracle type"
    assert db_types["staging"] == "sqlsvr", "staging should be sqlsvr type"
    assert db_types["mdatal"] == "bigquery", "mdatal should be bigquery type"
    assert db_types["REFERENCE_DB"] == "TERADATA", "REFERENCE_DB should be TERADATA type"
    assert db_types["RISK_VAR_DB"] == "TERADATA", "RISK_VAR_DB should be TERADATA type"
    
    # Verify table operations
    for db in dbs:
        if db["databaseName"] == "mdatal":
            tables = {table["tableName"]: table["operations"] for table in db["operationTables"]}
            assert "project_metadata" in tables, "mdatal should include project_metadata table"
            assert "SELECT" in tables["project_metadata"], "project_metadata table should have SELECT operation"
            assert "temp_calculations" in tables, "mdatal should include temp_calculations table"
            assert "DELETE" in tables["temp_calculations"], "temp_calculations table should have DELETE operation"
        
        if db["databaseName"] == "dwh":
            tables = {table["tableName"]: table["operations"] for table in db["operationTables"]}
            assert "trading_positions" in tables, "dwh should include trading_positions table"
            assert "SELECT" in tables["trading_positions"], "trading_positions table should have SELECT operation"
            assert "active_positions" in tables, "dwh should include active_positions table"
            assert "CREATE VIEW" in tables["active_positions"], "active_positions table should have CREATE VIEW operation"


def test_only_database_analysis():
    """Test database analysis only"""
    code = """
    /* Define Teradata database */
    libname RSK_VAR TERADATA server="teradata01" schema = "RISK_VAR_DB";
    
    /* SQL operations */
    proc sql;
        /* Query operation */
        select * from RSK_VAR.var_results;
        
        /* Insert operation */
        insert into RSK_VAR.audit_log
        values (current_timestamp, 'TEST', 'Testing');
    quit;
    """
    
    # Analyze databases only
    result = analyze_databases(code)
    result_obj = json.loads(result)
    
    # Output results
    print("\nDatabase analysis only results:")
    print(json.dumps(result_obj, indent=2))
    
    # Verify results
    assert len(result_obj) == 1, "Should find one database"
    assert result_obj[0]["databaseName"] == "RISK_VAR_DB", "Database name should be RISK_VAR_DB"
    assert result_obj[0]["databaseType"] == "TERADATA", "Database type should be TERADATA"
    
    # Verify table operations
    tables = {table["tableName"]: table["operations"] for table in result_obj[0]["operationTables"]}
    assert "RSK_VAR" in tables, "Should include RSK_VAR table"
    
    for table_name, operations in tables.items():
        if table_name == "var_results":
            assert "SELECT" in operations, "var_results table should have SELECT operation"
        elif table_name == "audit_log":
            assert "INSERT" in operations, "audit_log table should have INSERT operation"


def test_direct_database_analyzer():
    """Test direct database analyzer"""
    code = """
    /* Define database */
    libname dwh oracle user=dw_user password=xxxx path="DWPROD";
    
    /* SQL operations */
    proc sql;
        /* Query and create table */
        create table report as
        select * from dwh.customers
        where status = 'Active';
    quit;
    """
    
    # Use database analyzer directly
    result = analyze_database_usage(code)
    result_obj = json.loads(result)
    
    # Output results
    print("\nDirect database analyzer results:")
    print(json.dumps(result_obj, indent=2))
    
    # Verify results
    assert len(result_obj) == 1, "Should find one database"
    assert result_obj[0]["databaseName"] == "dwh", "Database name should be dwh"
    assert result_obj[0]["databaseType"] == "oracle", "Database type should be oracle"
    
    # Verify table operations
    tables = {table["tableName"]: table["operations"] for table in result_obj[0]["operationTables"]}
    assert "customers" in tables, "Should include customers table"
    assert "SELECT" in tables["customers"], "customers table should have SELECT operation"


if __name__ == "__main__":
    try:
        print("Starting data source analyzer tests...")
        test_comprehensive_example()
        test_only_database_analysis()
        test_direct_database_analyzer()
        print("\nAll tests passed! Data source analyzer is working correctly.")
    except Exception as e:
        print(f"\nTest failed: {str(e)}") 