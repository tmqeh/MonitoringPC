
-- =============================================
-- Author:  jyh
-- Create date: 2020.05.06
-- Description: Server Resource (File System) BULK INSERT MULTIPLE FILES From a Folder 
-- =============================================
CREATE PROCEDURE [dbo].[usp_GetSvrFsChk]
 -- Add the parameters for the stored procedure here
AS
BEGIN
    -- when File List Temp Table Exist, then reCreate
    IF OBJECT_ID(N'tempdb..#TB_Svr_Fs_filelist_T', 'U') IS NOT NULL
    DROP TABLE #TB_Svr_Fs_filelist_T;
    CREATE TABLE #TB_Svr_Fs_filelist_T(path VARCHAR(255),fileName varchar(255))
    -- when Resource Bulk Insert Temp Table Exist, then reCreate
    IF OBJECT_ID(N'tempdb..#TB_Svr_Fs_Chk_T', 'U') IS NOT NULL
        DROP TABLE #TB_Svr_Fs_Chk_T;
    CREATE TABLE #TB_Svr_Fs_Chk_T (Value varchar(max));
 
    declare @filename varchar(255),
            @path     varchar(255),
            @sql      varchar(8000),
            @cmd      varchar(1000)


    -- get the list of files from Specific Directory
    -- be aware of xp_cmdShell
    SET @path = 'D:\gatherLog\'
    SET @cmd = 'dir ' + @path + '*.Fs.log /b'
    INSERT INTO  #TB_Svr_Fs_filelist_T(fileName)
    EXEC Master..xp_cmdShell @cmd
    UPDATE #TB_Svr_Fs_filelist_T SET path = @path where path is null

    -- cursor loop
    -- target is for only Today
    declare c1 cursor for SELECT path,fileName FROM #TB_Svr_Fs_filelist_T where fileName like convert(varchar, getdate(), 112)+'%.Fs.log%'
    open c1 fetch next from c1 into @path,@filename
        While @@fetch_status <> -1
          begin
          -- bulk insert won't take a variable name, so make a sql and execute it instead:
          -- cuz of above that, need to use literal SQL
           set @sql = 'BULK INSERT #TB_Svr_Fs_Chk_T FROM ''' + @path + @filename + ''' '
               + '     WITH ( 
                       FIELDTERMINATOR = '','', 
                       ROWTERMINATOR = ''0x0a'', 
                       FIRSTROW = 1
                    ) '
        -- to debug uncomment it
        -- print @sql
        
        exec (@sql)

    -- u have to close all of cursor in MS-SQL
    fetch next from c1 into @path,@filename
      end
    close c1
    deallocate c1

    -- after all of things, INSERT to Main Table
    -- u should know the dbo.instr function is USER Function (someone made it same as Oracle)	
    insert into [dbo].[TB_Svr_Fs_Chk_L] (hostName, CollectDT, path_name, use_pct, RGPR_ID, RGST_DTM)
	select hostName, CollectDT, path_name, use_pct, RGPR_ID, RGST_DTM
	from (
		select distinct 
			   --, dbo.instr(value,',',1,1)
				 substring(value, 1, dbo.instr(value,',',1,1) - 1) as hostName
			   --, dbo.instr(value,',',1,2)
			   , substring(value, dbo.instr(value,',',1,1) +1, dbo.instr(value,',',1,2) - dbo.instr(value,',',1,1) -1) as CollectDT
			   --, dbo.instr(value,',',1,4)
			   , substring(value, dbo.instr(value,',',1,2) +1, dbo.instr(value,',',1,3) - dbo.instr(value,',',1,2) -1) as path_name
			   --, dbo.instr(value,',',1,5)
			   , substring(value, dbo.instr(value,',',1,3) +1, LEN(value) - dbo.instr(value,',',1,3) ) as use_pct
			   --, LEN(value)
			   , 'usp_GetSvrFsChk' as RGPR_ID
			   , GETDATE() AS RGST_DTM
		  from #TB_Svr_Fs_Chk_T
	) t
	/* 20240403 이지수, 중복키 실패 방지 로직 추가 */
	where not exists (
		select top 1 1
		from TB_Svr_Fs_Chk_L
		where t.CollectDT = CollectDT
		and t.hostName = hostName
		and t.path_name = path_name )
END
