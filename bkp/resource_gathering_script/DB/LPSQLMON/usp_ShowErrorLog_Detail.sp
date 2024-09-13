
-- =============================================
-- Author:		홍윤표
-- Create date: 2020.01.07
-- Description:	일일점검 보고서 MS-SQL 리포트 상세
-- =============================================
CREATE PROCEDURE [dbo].[usp_ShowErrorLog_Detail]
	-- Add the parameters for the stored procedure here
	
AS
BEGIN
	-- SET NOCOUNT ON added to prevent extra result sets from
	-- interfering with SELECT statements.
	SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
	SET NOCOUNT ON;
		
	/* [상세] SQL Error log 목록 */
	SELECT A.InstanceID, A.ServerName, B.CollectDate, B.LOG_DATE, B.PROCESS_INFO, B.ERRORLOG_TEXT
	FROM [META2_M_InstanceInfo] AS A 
		INNER JOIN [dbo].[TBL2_M_SqlErrorlog] AS B 
		ON A.InstanceID = B.InstanceID
	WHERE LOG_DATE >= CONVERT(VARCHAR(10), DATEADD(DAY, -1, GETDATE()), 23) + ' 00:00:00.000' AND
			PROCESS_INFO NOT IN ('Logon', '로그온', 'Backup', '백업') AND	
			(ERRORLOG_TEXT LIKE '%error%' OR ERRORLOG_TEXT LIKE '%failed%') AND
			(ERRORLOG_TEXT NOT LIKE '%Logging SQL Server messages in file%' AND 
			ERRORLOG_TEXT NOT LIKE '%The error log has been reinitialized. See the previous log for older entries.%' AND
			ERRORLOG_TEXT NOT LIKE 'Attempting to cycle%')
          -- 20201112 jyh 추가
          and A.InstanceID  IN (2, 4, 5, 6, 7, 8, 9, 11, 12, 13, 39, 50, 51, 52, 53, 54, 24, 27, 48, 21, 57, 56, 15, 16, 55, 79)
	ORDER BY A.InstanceID, B.LOG_DATE DESC
	/* [상세] SQL Error log 목록 */
END