
-- =============================================
-- Author:  jyh
-- Create date: 2020.03.02
-- Description: Server Resource BULK INSERT MULTIPLE FILES From a Folder 
-- History : 
		-- 2022.10.24 김진우 hostname SUBSTRING 로직 변경
-- =============================================
CREATE PROCEDURE [dbo].[usp_GetCVChk_bak20230820]
 -- Add the parameters for the stored procedure here
AS

BEGIN
    -- when File List Temp Table Exist, then reCreate
    IF OBJECT_ID(N'tempdb..#TB_Svr_CV_filelist_T', 'U') IS NOT NULL
		DROP TABLE #TB_Svr_CV_filelist_T;
    CREATE TABLE #TB_Svr_CV_filelist_T (hostname VARCHAR(30), path VARCHAR(255),fileName varchar(255), )

    -- when Resource Bulk Insert Temp Table Exist, then reCreate
    IF OBJECT_ID(N'tempdb..#TB_CV_BAK_Stat_Chk_L', 'U') IS NOT NULL
        DROP TABLE #TB_CV_BAK_Stat_Chk_L;
    CREATE TABLE #TB_CV_BAK_Stat_Chk_L (Value varchar(max));

    declare @filename varchar(255),
            @path     varchar(255),
            @sql      varchar(8000),
            @cmd      varchar(1000)


    -- get the list of files from Specific Directory
    -- be aware of xp_cmdShell
    SET @path = 'F:\gatherLog\'
    
    SET @cmd = 'dir ' + @path + '*.comvault.log /b'
    INSERT INTO  #TB_Svr_CV_filelist_T (fileName)
    EXEC Master..xp_cmdShell @cmd
    
    UPDATE #TB_Svr_CV_filelist_T 
    SET path = @path 
    --, hostname = substring(filename, CHARINDEX('_', filename)+1, len(filename)- CHARINDEX('.', filename)-2) 
	, hostname = substring(filename, CHARINDEX('_', filename)+1, CHARINDEX('.', filename)-CHARINDEX('_', filename)-1) --2022.10.24 김진우 SUBSTRING 로직 변경
    where path is null

    -- cursor loop
    -- target is for only TODAY
    declare c1 cursor for SELECT path,fileName FROM #TB_Svr_CV_filelist_T where fileName like convert(varchar, getdate(), 112) +'%.comvault.log%'
    open c1 fetch next from c1 into @path,@filename
    print(@@fetch_status)
        While @@fetch_status <> -1
          begin
          -- bulk insert won't take a variable name, so make a sql and execute it instead:
          -- cuz of above that, need to use literal SQL
           set @sql = 'BULK INSERT #TB_CV_BAK_Stat_Chk_L FROM ''' + @path + @filename + ''' '
               + '     WITH ( 
                       ROWTERMINATOR = ''0x0a'', 
                       FIRSTROW = 1
                    ) '
        -- to debug uncomment it
        -- print @sql

        exec (@sql)

		insert into TB_CV_BAK_Stat_Chk_L (	 JobID
											,Status
											,Type
											,Client
											,Agent
											,Instance
											,BackupSet
											,Subclient
											,ScanType
											,StartTime
											,WriteStartTime
											,EndTime
											,WriteEndTime
											,SizeOfApplication
											,CompressionRate
											,DataTransferred
											,DataWritten
											,SpaceSavingPercentage
											,DataSizeChange
											,TransferTime
											,CurrentTransferTime
											,Throughput
											,CurrentThroughput
											,ProtectedObjects
											,FailedObjects
											,FailedFolders
											,ScanTypeChangeReason
											,SystemStateBackupSkipReason
											,RGPR_ID
											,RGST_DTM
											,CollectDT)
		SELECT  convert(decimal, substring(value, dbo.instr(value,'	',1,5) +1, dbo.instr(value,'	',1,6) - dbo.instr(value,'	',1,5) -10)) as JobID
			   ,substring(value, dbo.instr(value,'	',1,6) +1, dbo.instr(value,'	',1,7) - dbo.instr(value,'	',1,6) -1) as Status
			   ,substring(value, dbo.instr(value,'	',1,7) +1, dbo.instr(value,'	',1,8) - dbo.instr(value,'	',1,7) -1) as Type
			   ,substring(value, 1, dbo.instr(value,'	',1,1) - 1) as Client
			   ,substring(value, dbo.instr(value,'	',1,1) +1, dbo.instr(value,'	',1,2) - dbo.instr(value,'	',1,1) -1) as Agent
			   ,substring(value, dbo.instr(value,'	',1,2) +1, dbo.instr(value,'	',1,3) - dbo.instr(value,'	',1,2) -1) as Instance
			   ,substring(value, dbo.instr(value,'	',1,3) +1, dbo.instr(value,'	',1,4) - dbo.instr(value,'	',1,3) -1) as BackupSet
			   ,substring(value, dbo.instr(value,'	',1,4) +1, dbo.instr(value,'	',1,5) - dbo.instr(value,'	',1,4) -1) as Subclient	   
			   ,substring(value, dbo.instr(value,'	',1,8) +1, dbo.instr(value,'	',1,9) - dbo.instr(value,'	',1,8) -1) as ScanType
			   ,convert(datetime, substring(value, dbo.instr(value,'	',1,9) +1, dbo.instr(value,'	',1,10) - dbo.instr(value,'	',1,9) -1)) as StartTime
			   ,convert(datetime, substring(value, dbo.instr(value,'	',1,10) +1, dbo.instr(value,'	',1,11) - dbo.instr(value,'	',1,10) -1)) as WriteStartTime
			   ,convert(datetime, substring(value, dbo.instr(value,'	',1,11) +1, dbo.instr(value,'	',1,12) - dbo.instr(value,'	',1,11) -1)) as EndTime
			   ,convert(datetime, substring(value, dbo.instr(value,'	',1,12) +1, dbo.instr(value,'	',1,13) - dbo.instr(value,'	',1,12) -1)) as WriteEndTime
			   ,convert(decimal, substring(value, dbo.instr(value,'	',1,13) +1, dbo.instr(value,'	',1,14) - dbo.instr(value,'	',1,13) -1)) as SizeOfApplication
			   ,substring(value, dbo.instr(value,'	',1,14) +1, dbo.instr(value,'	',1,15) - dbo.instr(value,'	',1,14) -1) as CompressionRate
			   ,convert(decimal, substring(value, dbo.instr(value,'	',1,15) +1, dbo.instr(value,'	',1,16) - dbo.instr(value,'	',1,15) -1)) as DataTransferred
			   ,convert(decimal, substring(value, dbo.instr(value,'	',1,16) +1, dbo.instr(value,'	',1,17) - dbo.instr(value,'	',1,16) -1)) as DataWritten
			   ,substring(value, dbo.instr(value,'	',1,17) +1, dbo.instr(value,'	',1,18) - dbo.instr(value,'	',1,17) -1) as SpaceSavingPercentage
			   ,substring(value, dbo.instr(value,'	',1,18) +1, dbo.instr(value,'	',1,19) - dbo.instr(value,'	',1,18) -1) as DataSizeChange
			   ,substring(value, dbo.instr(value,'	',1,19) +1, dbo.instr(value,'	',1,20) - dbo.instr(value,'	',1,19) -1) as TransferTime
			   ,substring(value, dbo.instr(value,'	',1,20) +1, dbo.instr(value,'	',1,21) - dbo.instr(value,'	',1,20) -1) as CurrentTransferTime
			   ,convert(decimal, substring(value, dbo.instr(value,'	',1,21) +1, dbo.instr(value,'	',1,22) - dbo.instr(value,'	',1,21) -1)) as Throughput
			   ,substring(value, dbo.instr(value,'	',1,22) +1, dbo.instr(value,'	',1,23) - dbo.instr(value,'	',1,22) -1) as CurrentThroughput
			   ,convert(decimal, substring(value, dbo.instr(value,'	',1,23) +1, dbo.instr(value,'	',1,24) - dbo.instr(value,'	',1,23) -1)) as ProtectedObjects
			   ,convert(decimal, substring(value, dbo.instr(value,'	',1,24) +1, dbo.instr(value,'	',1,25) - dbo.instr(value,'	',1,24) -1)) as FailedObjects
			   ,convert(decimal, substring(value, dbo.instr(value,'	',1,25) +1, dbo.instr(value,'	',1,26) - dbo.instr(value,'	',1,25) -1)) as FailedFolders
			   ,substring(value, dbo.instr(value,'	',1,26) +1, dbo.instr(value,'	',1,27) - dbo.instr(value,'	',1,26) -1) as ScanTypeChangeReason
			   ,substring(value, dbo.instr(value,'	',1,27) +1, dbo.instr(value,'	',1,28) - dbo.instr(value,'	',1,27) -1) as SystemStateBackupSkipReason
			   ,'usp_GetCVChk' as RGPR_ID
               ,GETDATE() AS RGST_DTM
			   ,CONVERT(VARCHAR, GETDATE(), 112) AS CollectDT
		FROM	#TB_CV_BAK_Stat_Chk_L	

        -- for below continuous Cursor
        DELETE #TB_CV_BAK_Stat_Chk_L

    -- u have to close all of cursor in MS-SQL
    fetch next from c1 into @path,@filename
      end
    close c1
    deallocate c1

END