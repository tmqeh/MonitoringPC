
-- =============================================
-- Author:  jyh
-- Create date: 2020.05.06
-- Description: ORacle Tablespace BULK INSERT MULTIPLE FILES From a Folder 
-- =============================================
CREATE PROCEDURE [dbo].[usp_GetOraTbsChk]
 -- Add the parameters for the stored procedure here
AS
BEGIN
    -- when File List Temp Table Exist, then reCreate
    IF OBJECT_ID(N'tempdb..#TB_Ora_Tbs_filelist_T', 'U') IS NOT NULL
    DROP TABLE #TB_Ora_tbs_filelist_T;
    CREATE TABLE #TB_Ora_tbs_filelist_T(path VARCHAR(255),fileName varchar(255))
    -- when Resource Bulk Insert Temp Table Exist, then reCreate
    IF OBJECT_ID(N'tempdb..#TB_Ora_Tbs_Chk_T', 'U') IS NOT NULL
        DROP TABLE #TB_Ora_tbs_Chk_T;
    CREATE TABLE #TB_Ora_tbs_Chk_T (Value varchar(max));
 
    declare @filename varchar(255),
            @path     varchar(255),
            @sql      varchar(8000),
            @cmd      varchar(1000)


    -- get the list of files from Specific Directory
    -- be aware of xp_cmdShell
    SET @path = 'D:\gatherLog\'
    SET @cmd = 'dir ' + @path + '*.tbs.log /b'	
    INSERT INTO  #TB_Ora_tbs_filelist_T(fileName)
    EXEC Master..xp_cmdShell @cmd
    UPDATE #TB_Ora_tbs_filelist_T SET path = @path where path is null

    -- cursor loop
    -- target is for only Today
    declare c1 cursor for SELECT path,fileName FROM #TB_Ora_tbs_filelist_T where fileName like convert(varchar, getdate(), 112)+'%.tbs.log%'
    open c1 fetch next from c1 into @path,@filename
        While @@fetch_status <> -1
          begin
          -- bulk insert won't take a variable name, so make a sql and execute it instead:
          -- cuz of above that, need to use literal SQL
           set @sql = 'BULK INSERT #TB_Ora_Tbs_Chk_T FROM ''' + @path + @filename + ''' '
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
	/* 20240403 이지수, 중복키 실패 방지 로직 추가 */
    insert into [dbo].[TB_Ora_Tbs_Chk_L] (dbName, CollectDT, tbs_name, tot_gb, free_gb, use_gb, use_pct, RGPR_ID, RGST_DTM)
	select dbName, CollectDT, tbs_name, tot_gb, free_gb, use_gb, use_pct, RGPR_ID, RGST_DTM
	from (
		select replace(substring(value, 1, dbo.instr(value,',',1,1) - 1),' ', '') as dbName
			 , replace(substring(value, dbo.instr(value,',',1,1) +1, dbo.instr(value,',',1,2) - dbo.instr(value,',',1,1) -1),' ', '') as CollectDT
			 , replace(substring(value, dbo.instr(value,',',1,2) +1, dbo.instr(value,',',1,3) - dbo.instr(value,',',1,2) -1),' ', '') as tbs_name
			 , replace(substring(value, dbo.instr(value,',',1,3) +1, dbo.instr(value,',',1,4) - dbo.instr(value,',',1,3) -1),' ', '') as tot_gb
			 , replace(substring(value, dbo.instr(value,',',1,4) +1, dbo.instr(value,',',1,5) - dbo.instr(value,',',1,4) -1),' ', '') as free_gb
			 , replace(substring(value, dbo.instr(value,',',1,5) +1, dbo.instr(value,',',1,6) - dbo.instr(value,',',1,5) -1),' ', '') as use_gb
			 , replace(replace(substring(value, dbo.instr(value,',',1,6) +1, LEN(value) - dbo.instr(value,',',1,5) ),' ', ''),char(13),'') as use_pct
			 , 'usp_GetOraTbsChk' as RGPR_ID
			 , GETDATE() AS RGST_DTM
		  from #TB_Ora_Tbs_Chk_T
	) t
	where not exists (
		select top 1 1
		from TB_Ora_Tbs_Chk_L
		where t.CollectDT = CollectDT
		and t.dbName = dbName 
		and t.tbs_name = tbs_name)
END