


-- =============================================
-- Author:		홍윤표
-- Create date: 2020.01.07
-- Description:	일일점검 보고서 MS-SQL 리포트 상세
-- =============================================
CREATE PROCEDURE [dbo].[usp_ShowAgentJob_Detail_DBA_20240408]
	-- Add the parameters for the stored procedure here
	
AS
BEGIN
	-- SET NOCOUNT ON added to prevent extra result sets from
	-- interfering with SELECT statements.
	SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
	SET NOCOUNT ON;
		
	/* [상세] Agent Job 실패 목록 */
	SELECT DISTINCT A.InstanceID, 
		   A.ServerName, 
		   B.JobName, 
		   B.LastRunDateTime, 
		   B.LastRunStatusMessage, 
		   B.NextRunDateTime
	FROM [META2_M_InstanceInfo] AS A 
	INNER JOIN [dbo].[TBL2_M_AgentJobInfo] AS B ON A.InstanceID = B.InstanceID
	WHERE A.UseYN = 'Y' 
		  AND B.LastRunDateTime >= CONVERT(VARCHAR(10), DATEADD(DAY, -1, GETDATE()), 23) + ' 00:00:00.000' 
		  AND B.LastRunStatus = 'Failed' 
		  AND B.Enabled = 'Y' 
          AND A.InstanceID <> 1
          -- 20201112 jyh 추가
		  AND A.InstanceID IN (2, 4, 5, 6, 7, 8, 9, 11, 12, 13, 39, 50, 51, 52, 53, 54, 24, 27, 48, 21, 57, 56, 15, 16, 55, 79)
		  -- 20240401 jyh 추가
		  AND B.JobName not like '%SQLServerMonitor%'
	ORDER BY A.InstanceID, B.JobName, B.LastRunDateTime DESC, B.NextRunDateTime
	/* [상세] Agent Job 실패 목록 */
END
