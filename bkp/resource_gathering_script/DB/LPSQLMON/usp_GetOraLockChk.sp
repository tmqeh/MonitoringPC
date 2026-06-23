

-- =============================================
-- Author:  jyh
-- Create date: 2020.05.06
-- Description: ORacle Tablespace BULK INSERT MULTIPLE FILES From a Folder 
-- =============================================
CREATE PROCEDURE [dbo].[usp_GetOraLockChk]
 -- Add the parameters for the stored procedure here
AS
BEGIN
    -- when File List Temp Table Exist, then reCreate
    IF OBJECT_ID(N'tempdb..#TB_Ora_Lock_filelist_T', 'U') IS NOT NULL
    DROP TABLE #TB_Ora_Lock_filelist_T;
    CREATE TABLE #TB_Ora_Lock_filelist_T(path VARCHAR(255),fileName varchar(255))
    -- when Resource Bulk Insert Temp Table Exist, then reCreate
    IF OBJECT_ID(N'tempdb..#TB_Ora_Lock_Chk_T', 'U') IS NOT NULL
        DROP TABLE #TB_Ora_Lock_Chk_T;
    CREATE TABLE #TB_Ora_Lock_Chk_T (Value varchar(max));
 
    declare @filename varchar(255),
            @path     varchar(255),
            @sql      varchar(8000),
            @cmd      varchar(1000)


    -- get the list of files from Specific Directory
    -- be aware of xp_cmdShell
    SET @path = 'D:\gatherLog\'
    SET @cmd = 'dir ' + @path + '*.lock.log /b'
    INSERT INTO  #TB_Ora_Lock_filelist_T(fileName)
    EXEC Master..xp_cmdShell @cmd
    UPDATE #TB_Ora_Lock_filelist_T SET path = @path where path is null

    -- cursor loop
    -- target is for only Today
    declare c1 cursor for SELECT path,fileName FROM #TB_Ora_Lock_filelist_T where fileName like convert(varchar, getdate(), 112)+'%.lock.log%'
    open c1 fetch next from c1 into @path,@filename
        While @@fetch_status <> -1
          begin
          -- bulk insert won't take a variable name, so make a sql and execute it instead:
          -- cuz of above that, need to use literal SQL
           set @sql = 'BULK INSERT #TB_Ora_Lock_Chk_T FROM ''' + @path + @filename + ''' '
               + '     WITH ( 
                       FIELDTERMINATOR = '','', 
                       ROWTERMINATOR = ''0x0a'', 
                       FIRSTROW = 1
                    ) '
        -- to debug uncomment it
        print @sql
        
        exec (@sql)

    -- u have to close all of cursor in MS-SQL
    fetch next from c1 into @path,@filename
      end
    close c1
    deallocate c1


    -- after all of things, INSERT to Main Table
    -- u should know the dbo.instr function is USER Function (someone made it same as Oracle)
    insert into [dbo].[TB_Ora_Lock_Chk_L] (CollectDT, HOSTNAME, BLOCKED_SESSION, BLOCKED_SQL_ID, BLOCKED_SQL_TEXT, HOLDING_SESSION, HOLDING_SQL_ID, HOLDING_SQL_TEXT, WAIT_TIME, EVENT, COMMAND, RGPR_ID, RGST_DTM)
	select CollectDT
	     , HOSTNAME
	     , BLOCKED_SESSION
	     , BLOCKED_SQL_ID
	     , REPLACE(REPLACE(BLOCKED_SQL_TEXT, '||CHAR(13)||', CHAR(13)), '||CHAR(10)||', CHAR(10))
		 , HOLDING_SESSION
		 , HOLDING_SQL_ID
		 , REPLACE(REPLACE(HOLDING_SQL_TEXT, '||CHAR(13)||', CHAR(13)), '||CHAR(10)||', CHAR(10))
		 , WAIT_TIME
		 , EVENT
		 , COMMAND
		 , RGPR_ID
		 , RGST_DTM
	from (
		select RTRIM(substring(value, 1, dbo.instr(value,'##',1,1) - 1)) as CollectDT
			 , substring(value, dbo.instr(value,'##',1,1) +2, dbo.instr(value,'##',1,2) - dbo.instr(value,'##',1,1) -2) as HOSTNAME
			 , substring(value, dbo.instr(value,'##',1,2) +2, dbo.instr(value,'##',1,3) - dbo.instr(value,'##',1,2) -2) as BLOCKED_SESSION
			 , substring(value, dbo.instr(value,'##',1,3) +2, dbo.instr(value,'##',1,4) - dbo.instr(value,'##',1,3) -2) as BLOCKED_SQL_ID
			 , substring(value, dbo.instr(value,'##',1,4) +2, dbo.instr(value,'##',1,5) - dbo.instr(value,'##',1,4) -2) as BLOCKED_SQL_TEXT
			 , substring(value, dbo.instr(value,'##',1,5) +2, dbo.instr(value,'##',1,6) - dbo.instr(value,'##',1,5) -2) as HOLDING_SESSION
			 , substring(value, dbo.instr(value,'##',1,6) +2, dbo.instr(value,'##',1,7) - dbo.instr(value,'##',1,6) -2) as HOLDING_SQL_ID
			 , substring(value, dbo.instr(value,'##',1,7) +2, dbo.instr(value,'##',1,8) - dbo.instr(value,'##',1,7) -2) as HOLDING_SQL_TEXT
			 , substring(value, dbo.instr(value,'##',1,8) +2, dbo.instr(value,'##',1,9) - dbo.instr(value,'##',1,8) -2) as WAIT_TIME
			 , substring(value, dbo.instr(value,'##',1,9) +2, dbo.instr(value,'##',1,10) - dbo.instr(value,'##',1,9) -2) as EVENT
			 , substring(value, dbo.instr(value,'##',1,10) +2, LEN(value) - dbo.instr(value,'##',1,9) ) as COMMAND
			 , 'usp_GetOraLockChk' as RGPR_ID
			 , GETDATE() AS RGST_DTM
		  from #TB_Ora_Lock_Chk_T
		  where value is not null
		    and value <> 'no rows selected'
	) t
	/* 20240403 이지수, 중복키 실패 방지 로직 추가 */
	where not exists (
		select top 1 1
		from TB_Ora_Lock_Chk_L
		where CollectDT = t.CollectDT
		and HOSTNAME = t.HOSTNAME
		and BLOCKED_SESSION = t.BLOCKED_SESSION
		and BLOCKED_SQL_ID = t.BLOCKED_SQL_ID
		and HOLDING_SESSION = t.HOLDING_SESSION
		and HOLDING_SQL_ID = t.HOLDING_SQL_ID)
END