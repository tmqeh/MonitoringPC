


-- =============================================
-- Author:  jyh
-- Create date: 2020.03.02
-- Description: Server Resource BULK INSERT MULTIPLE FILES From a Folder 
-- History : 
		-- 2022.10.24 김진우 hostname SUBSTRING 로직 변경
		-- 2023.08.20 이지수 SELECT Substring + instr -> Split + Pivot 로직 변경
		-- 2024.05.30 김진우 데이터타입이 datetime이 아닌 경우 null 표기
-- =============================================
CREATE PROCEDURE [dbo].[usp_GetCVChk]
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

    IF OBJECT_ID(N'tempdb..#TB_CV_BAK_Stat_Chk_L_Split', 'U') IS NOT NULL
        DROP TABLE #TB_CV_BAK_Stat_Chk_L_Split;
    CREATE TABLE #TB_CV_BAK_Stat_Chk_L_Split (Value varchar(max), Idx int, splStr varchar(max));


    declare @filename varchar(255),
            @path     varchar(255),
            @sql      varchar(8000),
            @cmd      varchar(1000)


    -- get the list of files from Specific Directory
    -- be aware of xp_cmdShell
    SET @path = 'D:\gatherLog\'
    
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

		INSERT INTO #TB_CV_BAK_Stat_Chk_L_Split
		SELECT 
			TMP.Value
			, SPL.Idx
			, CASE WHEN SPL.splStr = 'N/A' THEN NULL ELSE SPL.splStr END AS splStr
		FROM #TB_CV_BAK_Stat_Chk_L TMP
		OUTER APPLY (
			SELECT
				Idx
				, SUBSTRING(TMP.Value, StartStr, EndStr-StartStr+1) AS splStr
			FROM (
				SELECT 
					Idx
					, GubunStr
					, 1 + GubunStr AS StartStr
					, ISNULL(LEAD(GubunStr) OVER(ORDER BY Idx) - LEN(CHAR(9)), LEN(TMP.Value))  AS EndStr
				FROM (
					SELECT
						ROW_NUMBER() OVER(ORDER BY GubunStr) Idx
						, GubunStr
					FROM (		
						SELECT 0 AS GubunStr
						UNION ALL
						SELECT number AS GubunStr
						FROM master.dbo.spt_values
						WHERE TYPE = 'P' 
						AND number BETWEEN 1 AND LEN(TMP.Value) 
						AND SUBSTRING(TMP.Value, number,1) = CHAR(9)		
					) DEF
				) SPL
			) RES
		) SPL

		MERGE INTO TB_CV_BAK_Stat_Chk_L T1
		USING (
			SELECT SUBSTRING([6], 1, CHARINDEX('(',[6])-1) AS JobID
				 , [7] AS Status
				 , [8] AS Type
				 , [1] AS Client
				 , [2] AS Agent
				 , [3] AS Instance
				 , [4] AS BackupSet
				 , [5] AS Subclient
				 , [9] AS ScanType
				 -- 2024.05.30 김진우 데이터타입이 datetime이 아닌 경우 null 표기
				 , IIF(ISDATE([10]) = 0, NULL, [10]) AS StartTime				 
				 , IIF(ISDATE([11]) = 0, NULL, [11]) AS WriteStartTime				 
				 , IIF(ISDATE([12]) = 0, NULL, [12]) AS EndTime				 
				 , IIF(ISDATE([13]) = 0, NULL, [13]) AS WriteEndTime
				 , [14] AS SizeOfApplication
				 , [15] AS CompressionRate
				 , [16] AS DataTransferred
				 , [17] AS DataWritten
				 , [18] AS SpaceSavingPercentage
				 , [19] AS DataSizeChange
				 , [20] AS TransferTime
				 , [21] AS CurrentTransferTime
				 , ROUND(IIF(ISNUMERIC([22]) = 1, [22], NULL),0) AS Throughput
				 , ROUND(IIF(ISNUMERIC([23]) = 1, [23], NULL),0) AS CurrentThroughput
				 , [24] AS ProtectedObjects
				 , [25] AS FailedObjects
				 , [26] AS FailedFolders
				 , [27] AS ScanTypeChangeReason
				 , [28] AS SystemStateBackupSkipReason
				 , 'usp_GetCVChk' AS RGPR_ID
				 , GETDATE() AS RGST_DTM
				 , CONVERT(VARCHAR, GETDATE(), 112) AS CollectDT
			  FROM (
				   SELECT T2.Idx
					    , T2.splStr
					    , T2.Value
				     FROM #TB_CV_BAK_Stat_Chk_L T1
			   INNER JOIN #TB_CV_BAK_Stat_Chk_L_Split T2 
			           ON T1.Value = T2.Value
			       ) TMP
			   PIVOT (
				     MAX(TMP.splStr) 
				     FOR TMP.Idx IN ([1],[2],[3],[4],[5],[6],[7],[8],[9],[10],[11],[12],[13],[14],[15],[16],[17],[18],[19],[20],[21],[22],[23],[24],[25],[26],[27],[28])
					 ) AS Result
			) T2
		   ON T1.JobID = T2.JobID
	     WHEN MATCHED THEN 
			UPDATE SET Status						= T2.Status						
				      ,Type							= T2.Type							
				      ,Client						= T2.Client						
				      ,Agent						= T2.Agent						
				      ,Instance						= T2.Instance						
				      ,BackupSet					= T2.BackupSet					
				      ,Subclient					= T2.Subclient					
				      ,ScanType						= T2.ScanType						
				      ,StartTime					= T2.StartTime					
				      ,WriteStartTime				= T2.WriteStartTime				
				      ,EndTime						= T2.EndTime						
				      ,WriteEndTime					= T2.WriteEndTime					
				      ,SizeOfApplication			= T2.SizeOfApplication			
				      ,CompressionRate				= T2.CompressionRate				
				      ,DataTransferred				= T2.DataTransferred				
				      ,DataWritten					= T2.DataWritten					
				      ,SpaceSavingPercentage		= T2.SpaceSavingPercentage		
				      ,DataSizeChange				= T2.DataSizeChange				
				      ,TransferTime					= T2.TransferTime					
				      ,CurrentTransferTime			= T2.CurrentTransferTime			
				      ,Throughput					= T2.Throughput					
				      ,CurrentThroughput			= T2.CurrentThroughput			
				      ,ProtectedObjects				= T2.ProtectedObjects				
				      ,FailedObjects				= T2.FailedObjects				
				      ,FailedFolders				= T2.FailedFolders				
				      ,ScanTypeChangeReason			= T2.ScanTypeChangeReason			
				      ,SystemStateBackupSkipReason	= T2.SystemStateBackupSkipReason	
				      ,RGPR_ID						= T2.RGPR_ID						
				      ,RGST_DTM						= T2.RGST_DTM						
				      ,CollectDT					= T2.CollectDT					
		 WHEN NOT MATCHED THEN
			INSERT (JobID
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
			VALUES (T2.JobID
				   ,T2.Status
				   ,T2.Type
				   ,T2.Client
				   ,T2.Agent
				   ,T2.Instance
				   ,T2.BackupSet
				   ,T2.Subclient
				   ,T2.ScanType
				   ,T2.StartTime
				   ,T2.WriteStartTime
				   ,T2.EndTime
				   ,T2.WriteEndTime
				   ,T2.SizeOfApplication
				   ,T2.CompressionRate
				   ,T2.DataTransferred
				   ,T2.DataWritten
				   ,T2.SpaceSavingPercentage
				   ,T2.DataSizeChange
				   ,T2.TransferTime
				   ,T2.CurrentTransferTime
				   ,T2.Throughput
				   ,T2.CurrentThroughput
				   ,T2.ProtectedObjects
				   ,T2.FailedObjects
				   ,T2.FailedFolders
				   ,T2.ScanTypeChangeReason
				   ,T2.SystemStateBackupSkipReason
				   ,T2.RGPR_ID
				   ,T2.RGST_DTM
				   ,T2.CollectDT);

        -- for below continuous Cursor
        DELETE #TB_CV_BAK_Stat_Chk_L

    -- u have to close all of cursor in MS-SQL
    fetch next from c1 into @path,@filename
      end
    close c1
    deallocate c1

END



 --SELECT DataSizeChange , * FROM TB_CV_BAK_Stat_Chk_L 
