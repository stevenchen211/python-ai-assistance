/*****************************************************
 示例SAS代码文件
 包含多种数据库类型和操作
*****************************************************/

/* 定义变量 */
%let risk_schema = RISK_DB;
%let mart_lib = DATA_MART;

/* 定义多种类型的数据库 */
libname DWH oracle user=dw_user password=xxxx path="DWPROD";
libname STAGING sqlsvr server="sql-server-01" database=stage_db;
libname MDATA bigquery server="project-id" dataset=metadata;
libname RSK_CALC TERADATA server="teradata01" schema = "&risk_schema";
libname &mart_lib TERADATA server="teradata01" schema = "DATA_MART_DB";

/* 创建宏以便于重用 */
%macro process_data(date_param);
  
  /* 获取风险数据 */
  proc sql;
    /* 从不同数据库获取数据 */
    create table work.combined_data as
    select 
      a.trade_id,
      a.instrument_id,
      a.trade_date,
      a.quantity,
      a.price,
      b.market_value,
      c.risk_factor,
      d.limit_value
    from DWH.trades a
    join MDATA.market_data b
      on a.instrument_id = b.instrument_id
     and a.trade_date = b.price_date
    left join RSK_CALC.risk_factors c
      on a.instrument_id = c.instrument_id
    left join STAGING.trading_limits d
      on a.trade_id = d.trade_id
    where a.trade_date = "&date_param"d;
    
    /* 更新状态表 */
    update STAGING.batch_run_status
    set end_time = current_timestamp,
        status = 'Completed'
    where batch_date = "&date_param"d
      and process_type = 'RISK_CALC';
    
    /* 记录审计信息 */
    insert into DWH.process_audit_log
    values (
      current_timestamp,
      'RISK_CALC',
      "&date_param"d,
      'Process completed successfully',
      'INFO'
    );
  quit;
  
  /* 计算风险指标 */
  proc sql;
    /* 计算VaR */
    create table work.var_results as
    select 
      "&date_param"d as calc_date,
      instrument_type,
      sum(case when confidence = 0.95 then var_value else 0 end) as var95,
      sum(case when confidence = 0.99 then var_value else 0 end) as var99
    from RSK_CALC.var_calculations
    where calc_date = "&date_param"d
    group by instrument_type;
    
    /* 保存计算结果 */
    insert into DATA_MART.risk_results
    select * from work.var_results;
    
    /* 清理临时数据 */
    delete from MDATA.temp_calculations
    where created_date < "&date_param"d - 30;
    
    /* 创建报表视图 */
    create view DWH.risk_summary as
    select 
      calc_date,
      sum(var95) as total_var95,
      sum(var99) as total_var99
    from DATA_MART.risk_results
    group by calc_date;
    
    /* 创建备份表 */
    select * into MDATA.risk_backup
    from DATA_MART.risk_results
    where calc_date = "&date_param"d;
  quit;
  
%mend process_data;

/* 调用宏处理今天的数据 */
%process_data(%sysfunc(today(), date9.)); 