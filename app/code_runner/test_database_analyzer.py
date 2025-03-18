"""
Test Database Analyzer

Used to test database analyzer functionality
"""
import json
import sys
import os
from database_analyzer import analyze_database_usage


def test_generic_database():
    """Test generic external database analysis"""
    code = """
    /* Define generic external database */
    libname mdatal bigquery server="project-id" dataset=mydataset;
    
    /* Use database tables */
    proc sql;
        /* Simple SELECT query */
        select * from mdatal.project_metadata;
        
        /* JOIN operation */
        select a.*, b.status 
        from mdatal.users as a
        join mdatal.project_metadata as b
        on a.project_id = b.id;
        
        /* UPDATE operation */
        update mdatal.users
        set status = 'Active'
        where last_login > '2023-01-01';
        
        /* INSERT operation */
        insert into mdatal.logs
        select current_timestamp, 'test', 'INFO'
        from mdatal.config;
        
        /* DELETE operation */
        delete from mdatal.temp_data
        where created_date < '2023-01-01';
        
        /* CREATE VIEW operation */
        create view mdatal.active_users as
        select * from mdatal.users
        where status = 'Active';
        
        /* SELECT INTO operation */
        select * into mdatal.backup_users
        from mdatal.users;
    quit;
    """
    
    result = analyze_database_usage(code)
    result_obj = json.loads(result)
    
    # Output results
    print("Generic external database analysis results:")
    print(json.dumps(result_obj, indent=2))
    
    # Verify results
    assert len(result_obj) == 1, "Should find one database"
    assert result_obj[0]["databaseName"] == "mdatal", "Database name should be mdatal"
    assert result_obj[0]["databaseType"] == "bigquery", "Database type should be bigquery"
    
    # Verify table operations
    tables_ops = {table["tableName"]: table["operations"] for table in result_obj[0]["operationTables"]}
    assert "project_metadata" in tables_ops, "Should include project_metadata table"
    assert "SELECT" in tables_ops["project_metadata"], "project_metadata table should have SELECT operation"
    
    assert "users" in tables_ops, "Should include users table"
    assert set(["SELECT", "UPDATE"]).issubset(set(tables_ops["users"])), "users table should have SELECT and UPDATE operations"
    
    assert "logs" in tables_ops, "Should include logs table"
    assert "INSERT" in tables_ops["logs"], "logs table should have INSERT operation"
    
    assert "temp_data" in tables_ops, "Should include temp_data table"
    assert "DELETE" in tables_ops["temp_data"], "temp_data table should have DELETE operation"
    
    assert "active_users" in tables_ops, "Should include active_users table"
    assert "CREATE VIEW" in tables_ops["active_users"], "active_users table should have CREATE VIEW operation"
    
    assert "backup_users" in tables_ops, "Should include backup_users table"
    assert "SELECT INTO" in tables_ops["backup_users"], "backup_users table should have SELECT INTO operation"


def test_teradata_database():
    """Test Teradata database analysis"""
    code = """
    /* Define variables */
    %let my_table = RISK_DATA;
    
    /* Define Teradata database */
    libname RSK_LABL TERADATA server="tdprod" schema = "RISK_DB";
    libname &my_table TERADATA server="tdprod" schema = "RISK_PROD";
    
    /* Use database tables */
    proc sql;
        /* Simple SELECT query */
        select * from RSK_LABL.risk_factors;
        
        /* JOIN operation */
        select a.*, b.factor 
        from RSK_LABL.positions as a
        join RISK_DATA.scenarios as b
        on a.scenario_id = b.id;
        
        /* UPDATE operation */
        update RSK_LABL.parameters
        set value = 0.05
        where name = 'interest_rate';
        
        /* INSERT operation */
        insert into RISK_DATA.audit_log
        values (current_timestamp, 'UPDATE', 'Changed parameters');
    quit;
    """
    
    result = analyze_database_usage(code)
    result_obj = json.loads(result)
    
    # Output results
    print("\nTeradata database analysis results:")
    print(json.dumps(result_obj, indent=2))
    
    # Verify results
    assert len(result_obj) == 2, "Should find two databases"
    
    # Verify first database
    db1 = next((db for db in result_obj if db["databaseName"] == "RISK_DB"), None)
    assert db1 is not None, "Should find RISK_DB database"
    assert db1["databaseType"] == "TERADATA", "Database type should be TERADATA"
    
    # Verify first database table operations
    tables_ops_1 = {table["tableName"]: table["operations"] for table in db1["operationTables"]}
    assert "RSK_LABL" in tables_ops_1, "Should include RSK_LABL table"
    assert "risk_factors" in tables_ops_1 or "positions" in tables_ops_1 or "parameters" in tables_ops_1, "Should include related operation tables"
    
    # Verify second database
    db2 = next((db for db in result_obj if db["databaseName"] == "RISK_PROD"), None)
    assert db2 is not None, "Should find RISK_PROD database"
    assert db2["databaseType"] == "TERADATA", "Database type should be TERADATA"
    
    # Verify second database table operations
    tables_ops_2 = {table["tableName"]: table["operations"] for table in db2["operationTables"]}
    assert "RISK_DATA" in tables_ops_2, "Should include RISK_DATA table"
    assert "scenarios" in tables_ops_2 or "audit_log" in tables_ops_2, "Should include related operation tables"


def test_multiple_databases():
    """Test multiple database analysis"""
    code = """
    /* Define multiple databases */
    libname dwh oracle user=user1 password=pass1 path="DWPROD";
    libname staging sqlsvr server="sqlserver01" database=stage;
    libname RSK_CALC TERADATA server="tdprod" schema = "RISK_CALC";
    
    proc sql;
        /* Cross-database query */
        create table combined as
        select a.*, b.risk_score, c.limit
        from dwh.customers a
        join RSK_CALC.risk_scores b on a.id = b.customer_id
        join staging.credit_limits c on a.id = c.customer_id
        where a.status = 'Active';
        
        /* Update operation */
        update staging.audit_log
        set status = 'Processed'
        where process_date = today();
        
        /* Insert operation */
        insert into dwh.logs
        select current_timestamp, 'Data load completed', 'INFO'
        from staging.batch_control;
    quit;
    """
    
    result = analyze_database_usage(code)
    result_obj = json.loads(result)
    
    # Output results
    print("\nMultiple database analysis results:")
    print(json.dumps(result_obj, indent=2))
    
    # Verify results
    assert len(result_obj) >= 3, "Should find at least three databases"
    
    # Verify Oracle database
    oracle_db = next((db for db in result_obj if db["databaseType"] == "oracle"), None)
    assert oracle_db is not None, "Should find Oracle database"
    assert oracle_db["databaseName"] == "dwh", "Oracle database name should be dwh"
    
    # Verify SQL Server database
    sqlsvr_db = next((db for db in result_obj if db["databaseType"] == "sqlsvr"), None)
    assert sqlsvr_db is not None, "Should find SQL Server database"
    assert sqlsvr_db["databaseName"] == "staging", "SQL Server database name should be staging"
    
    # Verify Teradata database
    teradata_db = next((db for db in result_obj if db["databaseType"] == "TERADATA"), None)
    assert teradata_db is not None, "Should find Teradata database"
    assert teradata_db["databaseName"] == "RISK_CALC", "Teradata database name should be RISK_CALC"


if __name__ == "__main__":
    try:
        print("Starting database analyzer tests...")
        test_generic_database()
        test_teradata_database()
        test_multiple_databases()
        print("\nAll tests passed! Database analyzer is working correctly.")
    except Exception as e:
        print(f"\nTest failed: {str(e)}") 