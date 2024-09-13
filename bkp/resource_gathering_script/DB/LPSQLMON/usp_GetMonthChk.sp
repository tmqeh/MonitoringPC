-- =============================================
-- Author:  김진우
-- Create date: 2022.11.28
-- Description: Server Resource BULK INSERT MULTIPLE FILES From a Folder 
-- History : 		
-- =============================================
CREATE PROCEDURE [dbo].[usp_GetMonthChk]
 -- Add the parameters for the stored procedure here
AS

BEGIN
    -- when File List Temp Table Exist, then reCreate
    IF OBJECT_ID(N'tempdb..#TB_Svr_Alert_filelist_T', 'U') IS NOT NULL
    DROP TABLE #TB_Svr_Alert_filelist_T;
    CREATE TABLE #TB_Svr_Alert_filelist_T (hostname VARCHAR(30), path VARCHAR(255),fileName varchar(255), )

    -- when Resource Bulk Insert Temp Table Exist, then reCreate
    IF OBJECT_ID(N'tempdb..#TB_Svr_Month_Check_T', 'U') IS NOT NULL
        DROP TABLE #TB_Svr_Month_Check_T;
    CREATE TABLE #TB_Svr_Month_Check_T (Value varchar(max));
 
    declare @hostname varchar(255),
			@filename varchar(255),
            @path     varchar(255),
            @sql      varchar(8000),
            @cmd      varchar(1000)			


    -- get the list of files from Specific Directory
    -- be aware of xp_cmdShell
    SET @path = 'D:\MonthCheck\'
    
    SET @cmd = 'dir ' + @path + '*.alert.log /b'
    INSERT INTO  #TB_Svr_Alert_filelist_T (fileName)
    EXEC Master..xp_cmdShell @cmd
    
    UPDATE #TB_Svr_Alert_filelist_T 
    SET path = @path 
    --, hostname = substring(filename, CHARINDEX('_', filename)+1, len(filename)- CHARINDEX('.', filename)-2) 
	, hostname = substring(filename, CHARINDEX('_', filename)+1, CHARINDEX('.', filename)-CHARINDEX('_', filename)-1) --2022.10.24 김진우 SUBSTRING 로직 변경
    where path is null

    -- cursor loop
    -- target is for only TODAY

    declare c1 cursor for SELECT hostname,path,fileName FROM #TB_Svr_Alert_filelist_T where fileName like convert(varchar, getdate(), 112) +'%.alert.log%'
    open c1 fetch next from c1 into @hostname,@path,@filename
    print(@@fetch_status)
        While @@fetch_status <> -1
          begin
          -- bulk insert won't take a variable name, so make a sql and execute it instead:
          -- cuz of above that, need to use literal SQL
           set @sql = 'BULK INSERT #TB_Svr_Month_Check_T FROM ''' + @path + @filename + ''' '
               + '     WITH ( 
                       ROWTERMINATOR = ''0x0a'', 
                       FIRSTROW = 1
                    ) '
        -- to debug uncomment it
        -- print @sql

        exec (@sql)

		IF @hostname LIKE 'LOTTEHRS%'
		BEGIN

			-- INSERT to Main Table
			insert into TB_Svr_Month_Check_L (hostName, CollectDT, LINE, MESSAGE_TEXT, RGPR_ID, RGST_DTM)
			select 
				   --substring(@filename, CHARINDEX('_', @filename)+1, len(@filename)- CHARINDEX('.', @filename)-2) as hostname
				   substring(@filename, CHARINDEX('_', @filename)+1, CHARINDEX('.', @filename)-CHARINDEX('_', @filename)-1) as hostname --2022.10.24 김진우 SUBSTRING 로직 변경
				 , substring(@filename, 1, CHARINDEX('_', @filename)-1) as collectDT
				 , ROWNUM as LINE
				 , substring(T1.value,1,2048) as MESSAGE_TEXT
				 , 'usp_GetMonthChk_Month_Check' as RGPR_ID
				 , GETDATE() AS RGST_DTM
			from (
					SELECT	ROW_NUMBER() OVER(ORDER BY (SELECT 1)) AS ROWNUM
						   ,T1.VALUE
					FROM	#TB_Svr_Month_Check_T T1
				 ) T1						
			where	1=1
			AND		T1.VALUE is NOT null
			--TIMESTAMP
			AND		T1.VALUE NOT LIKE '%+09:00'
			--LGWR
			AND     T1.VALUE NOT LIKE '%LGWR switch%'
			AND     T1.VALUE NOT LIKE '%Current log#%ONLINELOG%'
			--ARCH
			AND     T1.VALUE NOT LIKE '%Archived Log entry%'
			AND     T1.VALUE NOT LIKE 'ALTER SYSTEM ARCHIVE LOG'
			--BCV
			AND     T1.VALUE NOT LIKE '%datafile % was not in online%'
			--RESOURCE_MANAGER
			AND     T1.VALUE NOT LIKE '%Restoring Resource Manager%'
			AND     T1.VALUE NOT LIKE '%Setting Resource Manager%'
			--MMON SLAVE
			AND     T1.VALUE NOT LIKE '%Suspending MMON%'
			--BACKUP
			AND     T1.VALUE NOT LIKE '%alter database %backup%'
			--NETBACKUP
			AND     T1.VALUE NOT LIKE 'Starting control autobackup'
			AND     T1.VALUE NOT LIKE 'Control autobackup written to SBT_TAPE device'
			AND     T1.VALUE NOT LIKE 'comment ''API Version 2.0,MMS Version 5.0.0.0'''
			AND     T1.VALUE NOT LIKE 'media ''@aaaae'''
			AND     T1.VALUE NOT LIKE 'handle ''c-1951807230%'
			--AND     T1.VALUE NOT LIKE ''
			--KILL SESSION
			AND     T1.VALUE NOT LIKE '%KILL SESSION for sid%'
			AND     T1.VALUE NOT LIKE '%  Reason = profile limit idle_time%'
			AND     T1.VALUE NOT LIKE '%  Reason = alter system kill session%'			  
			AND     T1.VALUE NOT LIKE '%  Mode = KILL SOFT -/-/-%'
			AND     T1.VALUE NOT LIKE '%  Requestor = PMON%'
			AND     T1.VALUE NOT LIKE '%  Requestor = USER%'			  
			AND     T1.VALUE NOT LIKE '%  Owner = Process: USER%'
			AND     T1.VALUE NOT LIKE '%  Result = ORA-0%'
			--SYSTEM PARTITION
			AND     T1.VALUE NOT LIKE '%ADDED INTERVAL PARTITION SYS%'
			--ETC 
			AND     T1.VALUE NOT LIKE '%Closing scheduler window%'

		END

		ELSE IF @hostname LIKE 'LPDLV%'
		BEGIN

			-- INSERT to Main Table
			insert into TB_Svr_Month_Check_L (hostName, CollectDT, LINE, MESSAGE_TEXT, RGPR_ID, RGST_DTM)
			select 
				   --substring(@filename, CHARINDEX('_', @filename)+1, len(@filename)- CHARINDEX('.', @filename)-2) as hostname
				   substring(@filename, CHARINDEX('_', @filename)+1, CHARINDEX('.', @filename)-CHARINDEX('_', @filename)-1) as hostname --2022.10.24 김진우 SUBSTRING 로직 변경
				 , substring(@filename, 1, CHARINDEX('_', @filename)-1) as collectDT
				 , ROWNUM as LINE
				 , substring(T1.value,1,2048) as MESSAGE_TEXT
				 , 'usp_GetMonthChk_Month_Check' as RGPR_ID
				 , GETDATE() AS RGST_DTM
			from (
					SELECT	ROW_NUMBER() OVER(ORDER BY (SELECT 1)) AS ROWNUM
						   ,T1.VALUE
					FROM	#TB_Svr_Month_Check_T T1
				 ) T1						
			where	T1.VALUE is NOT null
			--TIMESTAMP
			AND		CASE WHEN LEN(T1.VALUE) = 24 AND T1.VALUE LIKE 'Sun%' THEN 1
						 WHEN LEN(T1.VALUE) = 24 AND T1.VALUE LIKE 'Mon%' THEN 1
						 WHEN LEN(T1.VALUE) = 24 AND T1.VALUE LIKE 'Tue%' THEN 1
						 WHEN LEN(T1.VALUE) = 24 AND T1.VALUE LIKE 'Wed%' THEN 1
						 WHEN LEN(T1.VALUE) = 24 AND T1.VALUE LIKE 'Thu%' THEN 1
						 WHEN LEN(T1.VALUE) = 24 AND T1.VALUE LIKE 'Fri%' THEN 1
						 WHEN LEN(T1.VALUE) = 24 AND T1.VALUE LIKE 'Sat%' THEN 1
						 ELSE 0
					 END = 0
			--
			AND		T1.VALUE NOT LIKE '%+09:00'
			--LGWR
			AND     T1.VALUE NOT LIKE 'Thread 1 advanced to log sequence%LGWR switch%'
			AND     T1.VALUE NOT LIKE '%Current log#%%'
			AND		T1.VALUE NOT LIKE 'Resize operation completed%'
			AND		T1.VALUE NOT LIKE 'Thread 2 advanced to log sequence%'
			--ARCH
			AND     T1.VALUE NOT LIKE '%Archived Log entry%'
			AND		T1.VALUE NOT LIKE 'ALTER SYSTEM ARCHIVE LOG'
			AND		T1.VALUE NOT LIKE '%Thread % advanced to log sequence%(LGWR switch)'
			
			--RESOURCE MANAGER
			AND		T1.VALUE NOT LIKE 'Closing scheduler window'
			AND		T1.VALUE NOT LIKE 'Closing Resource Manager plan via scheduler window'
			AND		T1.VALUE NOT LIKE 'Clearing Resource Manager plan via parameter'
			AND		T1.VALUE NOT LIKE 'Control autobackup written to SBT_TAPE device'
			AND		T1.VALUE NOT LIKE '%Resource Manager%'
			--MMS
			AND		T1.VALUE NOT LIKE '%API Version 2.0,MMS Version 5.0.0.0%'
			AND		T1.VALUE NOT LIKE '%media %@aaaae%'
			AND		T1.VALUE NOT LIKE '%handle %c-%'
			--SYS INTERVAL PARTITION
			AND		T1.VALUE NOT LIKE 'TABLE SYS.%ADDED INTERVAL PARTITION%'
			AND		T1.VALUE NOT LIKE '%automatic SQL Tuning%'
			AND		T1.VALUE NOT LIKE 'Expanded controlfile section%'

		END

		ELSE IF @hostname LIKE 'LPSIS%'
		BEGIN

			-- INSERT to Main Table
			insert into TB_Svr_Month_Check_L (hostName, CollectDT, LINE, MESSAGE_TEXT, RGPR_ID, RGST_DTM)
			select 
				   --substring(@filename, CHARINDEX('_', @filename)+1, len(@filename)- CHARINDEX('.', @filename)-2) as hostname
				   substring(@filename, CHARINDEX('_', @filename)+1, CHARINDEX('.', @filename)-CHARINDEX('_', @filename)-1) as hostname --2022.10.24 김진우 SUBSTRING 로직 변경
				 , substring(@filename, 1, CHARINDEX('_', @filename)-1) as collectDT
				 , ROWNUM as LINE
				 , substring(T1.value,1,2048) as MESSAGE_TEXT
				 , 'usp_GetMonthChk_Month_Check' as RGPR_ID
				 , GETDATE() AS RGST_DTM
			from (
					SELECT	ROW_NUMBER() OVER(ORDER BY (SELECT 1)) AS ROWNUM
						   ,T1.VALUE
					FROM	#TB_Svr_Month_Check_T T1
				 ) T1						
			where	1=1
			AND		T1.VALUE is NOT null
			--TIMESTAMP
			AND		CASE WHEN LEN(T1.VALUE) = 24 AND T1.VALUE LIKE 'Sun%' THEN 1
						 WHEN LEN(T1.VALUE) = 24 AND T1.VALUE LIKE 'Mon%' THEN 1
						 WHEN LEN(T1.VALUE) = 24 AND T1.VALUE LIKE 'Tue%' THEN 1
						 WHEN LEN(T1.VALUE) = 24 AND T1.VALUE LIKE 'Wed%' THEN 1
						 WHEN LEN(T1.VALUE) = 24 AND T1.VALUE LIKE 'Thu%' THEN 1
						 WHEN LEN(T1.VALUE) = 24 AND T1.VALUE LIKE 'Fri%' THEN 1
						 WHEN LEN(T1.VALUE) = 24 AND T1.VALUE LIKE 'Sat%' THEN 1
						 ELSE 0
					 END = 0
			--LGWR
			AND     T1.VALUE NOT LIKE '%LGWR switch%'
			AND     T1.VALUE NOT LIKE '%Current log#%ONLINELOG%'
			AND		T1.VALUE NOT LIKE 'Thread % cannot allocate new log, sequence%'
			AND		T1.VALUE NOT LIKE 'Checkpoint not complete%'
			--ARCH
			AND     T1.VALUE NOT LIKE '%Archived Log entry%'
			AND     T1.VALUE NOT LIKE 'ALTER SYSTEM ARCHIVE LOG'
			--BCV
			AND     T1.VALUE NOT LIKE '%datafile % was not in online%'
			--RESOURCE_MANAGER			
			AND		T1.VALUE NOT LIKE '%Resource Manager%'
			--MMON SLAVE
			AND     T1.VALUE NOT LIKE '%Suspending MMON%'
			--BACKUP
			AND     T1.VALUE NOT LIKE '%alter database %backup%'
			--NETBACKUP
			AND     T1.VALUE NOT LIKE 'Starting control autobackup'
			AND     T1.VALUE NOT LIKE 'Control autobackup written to SBT_TAPE device'
			AND     T1.VALUE NOT LIKE 'comment ''API Version 2.0,MMS Version 5.0.0.0'''
			AND     T1.VALUE NOT LIKE 'media ''@aaaae'''
			AND     T1.VALUE NOT LIKE 'handle ''c-1951807230%'
			--AND     T1.VALUE NOT LIKE ''
			--KILL SESSION
			AND     T1.VALUE NOT LIKE '%KILL SESSION for sid%'
			AND     T1.VALUE NOT LIKE '%  Reason = profile limit idle_time%'
			AND     T1.VALUE NOT LIKE '%  Reason = alter system kill session%'			  
			AND     T1.VALUE NOT LIKE '%  Mode = KILL SOFT -/-/-%'
			AND     T1.VALUE NOT LIKE '%  Requestor = PMON%'
			AND     T1.VALUE NOT LIKE '%  Requestor = USER%'			  
			AND     T1.VALUE NOT LIKE '%  Owner = Process: USER%'
			AND     T1.VALUE NOT LIKE '%  Result = ORA-0%'
			--SYSTEM PARTITION
			AND     T1.VALUE NOT LIKE '%ADDED INTERVAL PARTITION SYS%'
			--ETC 
			AND     T1.VALUE NOT LIKE '%Closing scheduler window%'
			AND		T1.VALUE NOT LIKE '%automatic SQL Tuning Advisor run%'
			
			
			

		END

		-- for below continuous Cursor
		DELETE #TB_Svr_Month_Check_T

    -- u have to close all of cursor in MS-SQL
    fetch next from c1 into @hostname,@path,@filename
      end
    close c1
    deallocate c1

END



