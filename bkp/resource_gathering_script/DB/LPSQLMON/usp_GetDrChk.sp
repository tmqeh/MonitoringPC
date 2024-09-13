-- =============================================
-- Author:  jyh
-- Create date: 2020.03.02
-- Description: Server Resource BULK INSERT MULTIPLE FILES From a Folder 
-- History : 
		-- 2022.10.24 김진우 hostname SUBSTRING 로직 변경
-- =============================================
CREATE PROCEDURE [dbo].[usp_GetDrChk]
 -- Add the parameters for the stored procedure here
AS

BEGIN
    -- when File List Temp Table Exist, then reCreate
    IF OBJECT_ID(N'tempdb..#TB_Svr_Dr_filelist_T', 'U') IS NOT NULL
    DROP TABLE #TB_Svr_Dr_filelist_T;
    CREATE TABLE #TB_Svr_Dr_filelist_T (hostname VARCHAR(30), path VARCHAR(255),fileName varchar(255), )

    -- when Resource Bulk Insert Temp Table Exist, then reCreate
    IF OBJECT_ID(N'tempdb..#TB_Svr_Dr_Sync_T', 'U') IS NOT NULL
        DROP TABLE #TB_Svr_Dr_Sync_T;
    CREATE TABLE #TB_Svr_Dr_Sync_T (Value varchar(max));

    -- when Resource Bulk Insert Temp Table Exist, then reCreate
    IF OBJECT_ID(N'tempdb..#TB_Svr_BCV_Copy_T', 'U') IS NOT NULL
        DROP TABLE #TB_Svr_BCV_Copy_T;
    CREATE TABLE #TB_Svr_BCV_Copy_T (Value varchar(max));
 
    declare @filename varchar(255),
            @path     varchar(255),
            @sql      varchar(8000),
            @cmd      varchar(1000)


    -- get the list of files from Specific Directory
    -- be aware of xp_cmdShell
    SET @path = 'D:\gatherLog\'
    
	-- 특정 파일을 선택해서 넣고 싶을 때는 아래 쿼리를 수정
	-- EX) SET @cmd = 'dir ' + @path + '*LD-HRDB02.dr_sync.log /b'
    SET @cmd = 'dir ' + @path + '*.dr_sync.log /b'

    INSERT INTO  #TB_Svr_Dr_filelist_T (fileName)
    EXEC Master..xp_cmdShell @cmd
    
	-- 특정 파일을 선택해서 넣고 싶을 때는 아래 쿼리를 수정
	-- EX) SET @cmd = 'dir ' + @path + '*LD-HRDB02.bcv_copy.log /b'
--    SET @cmd = 'dir ' + @path + '*.bcv_copy.log /b'
	SET @cmd = 'dir ' + @path + '*.bcv_copy.log /b'

    INSERT INTO  #TB_Svr_Dr_filelist_T (fileName)
    EXEC Master..xp_cmdShell @cmd 
    
    UPDATE #TB_Svr_Dr_filelist_T 
    SET path = @path 
    --, hostname = substring(filename, CHARINDEX('_', filename)+1, len(filename)- CHARINDEX('.', filename)-2) 
	, hostname = substring(filename, CHARINDEX('_', filename)+1, CHARINDEX('.', filename)-CHARINDEX('_', filename)-1) --2022.10.24 김진우 SUBSTRING 로직 변경
    where path is null

    -- cursor loop
    -- target is for only TODAY
    declare c1 cursor for SELECT path,fileName FROM #TB_Svr_Dr_filelist_T where fileName like convert(varchar, getdate(), 112) +'%.dr_sync.log%'
    open c1 fetch next from c1 into @path,@filename
    print(@@fetch_status)
        While @@fetch_status <> -1
          begin
          -- bulk insert won't take a variable name, so make a sql and execute it instead:
          -- cuz of above that, need to use literal SQL
           set @sql = 'BULK INSERT #TB_Svr_Dr_Sync_T FROM ''' + @path + @filename + ''' '
               + '     WITH ( 
                       ROWTERMINATOR = ''0x0a'', 
                       FIRSTROW = 1
                    ) '
        -- to debug uncomment it
        -- print @sql

        exec (@sql)

        -- INSERT to Main Table
        insert into TB_Svr_Dr_Sync_L (hostName, CollectDT, MESSAGE_TEXT, RGPR_ID, RGST_DTM)
        select 
		       --substring(@filename, CHARINDEX('_', @filename)+1, len(@filename)- CHARINDEX('.', @filename)-2) as hostname
			   substring(@filename, CHARINDEX('_', @filename)+1, CHARINDEX('.', @filename)-CHARINDEX('_', @filename)-1) as hostname --2022.10.24 김진우 SUBSTRING 로직 변경
             , substring(@filename, 1, CHARINDEX('_', @filename)-1) as collectDT
             , substring(value,1,2048) as MESSAGE_TEXT
             , 'usp_GetDrChk_Dr_Sync' as RGPR_ID
             , GETDATE() AS RGST_DTM
        from #TB_Svr_Dr_Sync_T
        where value is not null

        -- for below continuous Cursor
        DELETE #TB_Svr_Dr_Sync_T

    -- u have to close all of cursor in MS-SQL
    fetch next from c1 into @path,@filename
      end
    close c1
    deallocate c1

----------------------------------------------------------------------------------------------------------------

    -- cursor loop
    -- target is for only TODAY
    declare c1 cursor for SELECT path,fileName FROM #TB_Svr_Dr_filelist_T where fileName like convert(varchar, getdate(), 112) +'%.bcv_copy.log%'
    open c1 fetch next from c1 into @path,@filename
    print(@@fetch_status)
        While @@fetch_status <> -1
          begin
          -- bulk insert won't take a variable name, so make a sql and execute it instead:
          -- cuz of above that, need to use literal SQL
           set @sql = 'BULK INSERT #TB_Svr_BCV_Copy_T FROM ''' + @path + @filename + ''' '
               + '     WITH ( 
                       ROWTERMINATOR = ''0x0a'', 
                       FIRSTROW = 1
                    ) '
        -- to debug uncomment it
        -- print @sql

        exec (@sql)

        -- INSERT to Main Table		
        insert into TB_Svr_BCV_Copy_L (hostName, CollectDT, MESSAGE_TEXT, RGPR_ID, RGST_DTM)
		select hostName, CollectDT, MESSAGE_TEXT, RGPR_ID, RGST_DTM
		from (
			select substring(@filename, CHARINDEX('_', @filename)+1, len(@filename)- CHARINDEX('.', @filename)-3) as hostname
			     , substring(@filename, 1, CHARINDEX('_', @filename)-1) as collectDT
			     , substring(value,1,2048) as MESSAGE_TEXT
			     , 'usp_GetDrChk_BCV_Copy' as RGPR_ID
			     , GETDATE() AS RGST_DTM
			from #TB_Svr_BCV_Copy_T
			where value is not null
		) t
		/* 20240403 이지수, 중복키 실패 방지 로직 추가 */
		where not exists (
			select top 1 1
			from TB_Svr_BCV_Copy_L
			where CollectDT = t.CollectDT 
			and hostName = t.hostName )

        -- frankly, this is unnecessary
        DELETE #TB_Svr_BCV_Copy_T

    -- u have to close all of cursor in MS-SQL
    fetch next from c1 into @path,@filename
      end
    close c1
    deallocate c1
END



