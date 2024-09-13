

-- =============================================
-- Author:  jyh
-- Create date: 2020.05.06
-- Description: Rdscle Tablespace BULK INSERT MULTIPLE FILES From a Folder 
-- =============================================
CREATE PROCEDURE [dbo].[usp_GetRdsErrChk_before_remove_instr]
 -- Add the parameters for the stored procedure here
 ---------------------------------------------
 -- NOTE : 2021-03-19 Method changed to Python
 ---------------------------------------------
AS
BEGIN
    -- when File List Temp Table Exist, then reCreate
    IF OBJECT_ID(N'tempdb..#TB_Rds_Err_filelist_T', 'U') IS NOT NULL
    DROP TABLE #TB_Rds_Err_filelist_T;
    CREATE TABLE #TB_Rds_Err_filelist_T(path VARCHAR(255),fileName varchar(255))
    -- when Resource Bulk Insert Temp Table Exist, then reCreate
    IF OBJECT_ID(N'tempdb..#TB_Rds_Err_Chk_T', 'U') IS NOT NULL
        DROP TABLE #TB_Rds_Err_Chk_T;
    CREATE TABLE #TB_Rds_Err_Chk_T (Value varchar(max));
 
    declare @filename varchar(255),
            @path     varchar(255),
            @sql      varchar(8000),
            @cmd      varchar(1000)

    -- get the list of files from Specific Directory
    -- be aware of xp_cmdShell
    SET @path = 'C:\rdslog\' + substring(convert(varchar, getdate(), 112),1,4) + '\' + substring(convert(varchar, getdate(), 112),5,2) + '\'
    SET @cmd = 'dir ' + @path + '*_error.log /b'
    INSERT INTO  #TB_Rds_Err_filelist_T(fileName)
    EXEC Master..xp_cmdShell @cmd
    UPDATE #TB_Rds_Err_filelist_T SET path = @path where path is null

    -- cursor loop
    -- target is for only Today
    declare c1 cursor for SELECT path,fileName FROM #TB_Rds_Err_filelist_T where fileName like convert(varchar, getdate(), 112) + convert(varchar(2), getdate(), 108) + '%_error.log%'
    -- 수기 작업용
    -- declare c1 cursor for SELECT path,fileName FROM #TB_Rds_Err_filelist_T where fileName like  + '2020082919%_error.log%'
    -- declare c1 cursor for SELECT path,fileName FROM #TB_Rds_Err_filelist_T where fileName like convert(varchar, getdate(), 112) + '%_error.log%'
    open c1 fetch next from c1 into @path,@filename
        While @@fetch_status <> -1
          begin
          -- bulk insert won't take a variable name, so make a sql and execute it instead:
          -- cuz of above that, need to use literal SQL
           set @sql = 'BULK INSERT #TB_Rds_Err_Chk_T FROM ''' + @path + @filename + ''' '
               + '     WITH ( 
                       ROWTERMINATOR = ''0x7D0a'', 
                       FIRSTROW = 1
                    ) '
        -- to debug uncomment it
        -- print @sql
        
        exec (@sql)

        update #TB_Rds_Err_Chk_T
           set value = substring(@fileName,12,dbo.instr(@fileName,'_error.log',1,1)-12) + value
          from  #TB_Rds_Err_Chk_T
          where dbo.instr(value,'{',1,1) between 1 and 2

    -- u have to close all of cursor in MS-SQL
    fetch next from c1 into @path,@filename
      end
    close c1
    deallocate c1

    -- after all of things, INSERT to Main Table
    -- u should know the dbo.instr function is USER Function (someone made it same as Rdscle)
    insert into [dbo].[TB_Rds_Err_Chk_L] (ServerHost, CollectDT, CollectHH, MESSAGE_TEXT, CollectDtm, RGPR_ID, RGST_DTM)
    select replace(substring(value,1, dbo.instr(value, '{',1,1) -1),char(10),'') ServerHost
         , convert(char(8), dateadd(hh, 9, convert(datetime,substring(replace(replace(substring(value, dbo.instr(value,', "Message":',1,1)+14,27),'T',' '),'Z',''),1,len(replace(replace(substring(value, dbo.instr(value,', "Message":',1,1)+14,27),'T',' '),'Z',''))-3))), 112) CollectDT
         , convert(char(2), dateadd(hh, 9, convert(datetime,substring(replace(replace(substring(value, dbo.instr(value,', "Message":',1,1)+14,27),'T',' '),'Z',''),1,len(replace(replace(substring(value, dbo.instr(value,', "Message":',1,1)+14,27),'T',' '),'Z',''))-3))), 108) CollectHH
         , substring(value, dbo.instr(value,', "Message":',1,1) + 41 +1 , dbo.instr(value,', "IngestionTime":',1,1) - (dbo.instr(value,', "Message":',1,1) + 41 +2) ) as MESSAGE_TEXT
         , dateadd(hh, 9, convert(datetime,substring(replace(replace(substring(value, dbo.instr(value,', "Message":',1,1)+14,27),'T',' '),'Z',''),1,len(replace(replace(substring(value, dbo.instr(value,', "Message":',1,1)+14,27),'T',' '),'Z',''))-3))) CollectDTM
         , 'usp_GetRdsErrChk' as RGPR_ID
         , GETDATE() AS RGST_DTM
      from #TB_Rds_Err_Chk_T a
      where substring(value, dbo.instr(value,', "Message":',1,1) + 41 +1 , dbo.instr(value,', "IngestionTime":',1,1) - (dbo.instr(value,', "Message":',1,1) + 41 +2) ) not like '%Bad handshake%'
        and substring(value, dbo.instr(value,', "Message":',1,1) + 41 +1 , dbo.instr(value,', "IngestionTime":',1,1) - (dbo.instr(value,', "Message":',1,1) + 41 +2) ) not like '%Got an error reading communication packets%'
        and substring(value, dbo.instr(value,', "Message":',1,1) + 41 +1 , dbo.instr(value,', "IngestionTime":',1,1) - (dbo.instr(value,', "Message":',1,1) + 41 +2) ) not like '%Access denied for user %(using password: YES)%'
        -- 20200603 added
        and substring(value, dbo.instr(value,', "Message":',1,1) + 41 +1 , dbo.instr(value,', "IngestionTime":',1,1) - (dbo.instr(value,', "Message":',1,1) + 41 +2) ) not like '%Got timeout reading communication packets%'
        -- 20200709 added
        and substring(value, dbo.instr(value,', "Message":',1,1) + 41 +1 , dbo.instr(value,', "IngestionTime":',1,1) - (dbo.instr(value,', "Message":',1,1) + 41 +2) ) not like '%Got timeout writing communication packets%'
        and substring(value, dbo.instr(value,', "Message":',1,1) + 41 +1 , dbo.instr(value,', "IngestionTime":',1,1) - (dbo.instr(value,', "Message":',1,1) + 41 +2) ) not like '%Got an error writing communication packets%'
		-- 20200928 added
		and dbo.instr(value, '[',1,1) != 0
    -- 20200928 added
    union all
    select replace(substring(value,1, dbo.instr(value, '{',1,1) -1),char(10),'') ServerHost
         , convert(char(8), dateadd(hh, 9, convert(datetime,substring(replace(replace(substring(value, dbo.instr(value,', "Message":',1,1)+14,27),'T',' '),'Z',''),1,len(replace(replace(substring(value, dbo.instr(value,', "Message":',1,1)+14,27),'T',' '),'Z',''))-3))), 112) CollectDT
         , convert(char(2), dateadd(hh, 9, convert(datetime,substring(replace(replace(substring(value, dbo.instr(value,', "Message":',1,1)+14,27),'T',' '),'Z',''),1,len(replace(replace(substring(value, dbo.instr(value,', "Message":',1,1)+14,27),'T',' '),'Z',''))-3))), 108) CollectHH
         , substring(value, dbo.instr(value,', "Message":',1,1) + 41 +1 , dbo.instr(value,', "IngestionTime":',1,1) - (dbo.instr(value,', "Message":',1,1) + 41 +2) ) as MESSAGE_TEXT
         , dateadd(hh, 9, convert(datetime,substring(replace(replace(substring(value, dbo.instr(value,', "Message":',1,1)+14,27),'T',' '),'Z',''),1,len(replace(replace(substring(value, dbo.instr(value,', "Message":',1,1)+14,27),'T',' '),'Z',''))-3))) CollectDTM
         , 'usp_GetRdsErrChk' as RGPR_ID
         , GETDATE() AS RGST_DTM
      from #TB_Rds_Err_Chk_T b
     where dbo.instr(value, '[',1,1) = 0
END










