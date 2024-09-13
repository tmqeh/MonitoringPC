
/*******************************************************************************************
-- Author:		홍윤표
-- Create date: 2019.12.30
-- Description:	데이터베이스 사용량 추이
-- EXEC [dbo].[usp_ShowDatabaseSizeGrowth]
*******************************************************************************************/
CREATE PROC [dbo].[usp_ShowDatabaseSizeGrowth] 

AS
BEGIN
	SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
	SET NOCOUNT ON;

	--데이터베이스 사용 추이
	SELECT B.CollectDate,
	   A.ServerName,
	   B.databaseName,
	   B.TotalSizeMB,
	   B.UsedSizeMB
	FROM [dbo].[META2_M_InstanceInfo] AS A
		INNER JOIN [dbo].[TB_DataSizeGrowth_S] AS B
		ON A.InstanceID = B.instanceID
    ORDER BY B.CollectDate

	SELECT B.CollectDate,
		   A.ServerName,
		   B.databaseName,
		   B.TotalSizeMB,
		   B.UsedSizeMB
	FROM [dbo].[META2_M_InstanceInfo] AS A
		INNER JOIN [dbo].[TB_LogSizeGrowth_S] AS B
		ON A.InstanceID = B.instanceID
    ORDER BY B.CollectDate
END