-- =============================================
-- Author:		<Author,,Name>
-- Create date: <Create Date,,>
-- Description:	<Description,,>
-- =============================================
CREATE PROCEDURE [dbo].[PostgresDailyReport_BAK20250723]
AS
BEGIN
	SET NOCOUNT ON;
    SELECT  host_ip,
            host_name,
            cpu_usr_pct,
            cpu_sys_pct,	
            cpu_wio_pct,	
            mem_free_mb,	
            tbs_cnt,	
            err_cnt,	
            dt,	
            hh    
    FROM OPENQUERY (POSTGRESQL,'SELECT  host_ip,
                                        host_name,
                                        cpu_usr_pct,
                                        cpu_sys_pct,	
                                        cpu_wio_pct,	
                                        mem_free_mb,	
                                        tbs_cnt,	
                                        err_cnt,	
                                        dt,	
                                        hh 
                                FROM    public.dba_oracle_daily_report');
END
