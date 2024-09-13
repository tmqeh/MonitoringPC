
/*******************************************************************************************
-- Author:		홍윤표
-- Create date: 2019.12.30
-- Description:	데이터베이스 사용량 추이 기록
-- EXEC [dbo].[usp_GetDatabaseSizeGrowth] 
*******************************************************************************************/
CREATE PROC [dbo].[usp_GetDatabaseSizeGrowth] 

AS
BEGIN
	SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
	SET NOCOUNT ON;

	DECLARE @DatabaseFileInfo TABLE
	(
		InstanceID INT
		,database_id INT
		,MaxCollectDate DATETIME
	
	
	)
	INSERT INTO @DatabaseFileInfo
	SELECT InstanceID, 
		   database_id,
		   MAX(CollectDate) MaxCollectDate
	FROM [dbo].[TBL2_M_DatabaseFileInfo] 
	WHERE CollectDate >= CONVERT(DATETIME, CAST(CAST(DATEADD(DAY, -1, GETDATE()) AS float) AS INT)) AND 
		  CollectDate <= CONVERT(DATETIME, CAST(CAST(GETDATE() AS float) AS INT))
	GROUP BY InstanceID, database_id, CONVERT(DATETIME, CAST(CAST(CollectDate AS FLOAT) AS INT))
	
	--데이터베이스 데이터파일 사용 추이
	INSERT INTO TB_DataSizeGrowth_S (CollectDate, InstanceID, Database_id, DatabaseName, TotalSizeMB, UsedSizeMB)
	SELECT CONVERT(DATETIME, CAST(CAST(CollectDate AS FLOAT) AS INT)) CollectDate, 
	       a.InstanceID, 
		   a.database_id, 
		   a.databaseName, 
		   SUM(TotalSizeMB) TotalSizeMB,
		   SUM(UsedSizeMB) UsedSizeMB
	FROM [dbo].[TBL2_M_DatabaseFileInfo] a 
		INNER JOIN @DatabaseFileInfo b 
		ON a.InstanceID = b.InstanceID AND a.database_id = b.database_id AND a.CollectDate = b.MaxCollectDate 
	WHERE a.FileGroupName is not null
	GROUP BY CONVERT(DATETIME, CAST(CAST(CollectDate AS FLOAT) AS INT)), a.InstanceID, a.database_id, a.databaseName
	ORDER BY CONVERT(DATETIME, CAST(CAST(CollectDate AS FLOAT) AS INT)), a.InstanceID, a.database_id, a.databaseName

	--데이터베이스 로그파일 사용 추이
	INSERT INTO TB_LogSizeGrowth_S (CollectDate, InstanceID, Database_id, DatabaseName, TotalSizeMB, UsedSizeMB)
	SELECT CONVERT(DATETIME, CAST(CAST(CollectDate AS FLOAT) AS INT)) CollectDate, 
		   a.InstanceID, 
		   a.database_id, 
		   a.databaseName,
		   SUM(TotalSizeMB) TotalSizeMB,
		   SUM(UsedSizeMB) UsedSizeMB
	FROM [dbo].[TBL2_M_DatabaseFileInfo] a
		INNER JOIN @DatabaseFileInfo b 
		ON a.InstanceID = b.InstanceID AND a.database_id = b.database_id AND a.CollectDate = b.MaxCollectDate 
	WHERE a.FileGroupName is null
	GROUP BY CONVERT(DATETIME, CAST(CAST(CollectDate AS FLOAT) AS INT)), a.InstanceID, a.database_id, a.databaseName
	ORDER BY CONVERT(DATETIME, CAST(CAST(CollectDate AS FLOAT) AS INT)), a.InstanceID, a.database_id, a.databaseName
END