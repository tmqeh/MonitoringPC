


/*******************************************************************************************
-- Author:		홍윤표
-- Create date: 2020.01.22
-- Description:	일일 점검 보고서
-- EXEC [dbo].[usp_ShowDailyReport]
-- Modify :	파라미터 입력시 날짜 지정, 날짜 파라미터 추가
-- Execute : EXEC usp_ShowDailyReport '20250721'
*******************************************************************************************/
CREATE PROC [dbo].[usp_ShowDailyReport] 
	@in_DATE		VARCHAR(8) = ''
AS
BEGIN
	SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
	SET NOCOUNT ON;

	IF ISDATE(@in_DATE) = 1
	BEGIN
		DECLARE @in_INP_DTM DATETIME 
		
		SELECT @in_INP_DTM = MAX(INP_DTM) 
		FROM  [dbo].[TB_DailyReport_S] 
		WHERE INP_DTM BETWEEN CONVERT(VARCHAR(10), CONVERT(DATE, @in_DATE), 121) AND CONVERT(VARCHAR(10), CONVERT(DATE, @in_DATE), 121) + ' 23:59:59.997'

		SELECT 
				DATEDIFF(SS,CLCT_DTM,GETDATE()) CLCT_CHK,
				[INST_ID],
				[JOB_NM],			
				[IP_ADDR],
				[CLU_NODE_NM],
				[CLU_CMPS_CD],
				[AGENT_WRK_FAIL_CNT],
				[ERR_LOG_CNT],
				[BLK_TM],
				[CPU_PCT],
				CASE WHEN [MEM_CHECK] = 1 THEN FORMAT(MEM_USE_PCT, '#') + '%(' + FORMAT(MEM_FREE_SIZE / 1024, '#.#') + 'GB)'
					 ELSE [MEM_CHECK] 
				END AS [MEM_CHECK],
				[DRV1],[USE1],
				[DRV2],[USE2],
				[DRV3],[USE3],
				[DRV4],[USE4],
				[DRV5],[USE5],
				[DRV6],[USE6],
				[DRV7],[USE7],
				[DRV8],[USE8],
				-- [DRV9],[USE9],
				[INP_DTM],
				[CLCT_DTM],
				SUBSTRING([JOB_NM], 2, CHARINDEX(']', JOB_NM)-2) AS PART_NM
		FROM [dbo].[TB_DailyReport_S]
		WHERE INP_DTM = @in_INP_DTM
		AND	INST_ID IN (2, 4, 5, 6, 7, 8, 9, 11, 12, 13, 39, 50, 51, 52, 53, 54, 24, 27, 48, 21, 57, 56, 15, 16, 55, 79, 91)
		ORDER BY INST_ID ASC
	END
	ELSE
	BEGIN
		SELECT 
				DATEDIFF(SS,CLCT_DTM,GETDATE()) CLCT_CHK,
				[INST_ID],
				[JOB_NM],			
				[IP_ADDR],
				[CLU_NODE_NM],
				[CLU_CMPS_CD],
				[AGENT_WRK_FAIL_CNT],
				[ERR_LOG_CNT],
				[BLK_TM],
				[CPU_PCT],
				CASE WHEN [MEM_CHECK] = 1 THEN FORMAT(MEM_USE_PCT, '#') + '%(' + FORMAT(MEM_FREE_SIZE / 1024, '#.#') + 'GB)'
					 ELSE [MEM_CHECK] 
				END AS [MEM_CHECK],
				[DRV1],[USE1],
				[DRV2],[USE2],
				[DRV3],[USE3],
				[DRV4],[USE4],
				[DRV5],[USE5],
				[DRV6],[USE6],
				[DRV7],[USE7],
				[DRV8],[USE8],
				-- [DRV9],[USE9],
				[INP_DTM],
				[CLCT_DTM],
				SUBSTRING([JOB_NM], 2, CHARINDEX(']', JOB_NM)-2) AS PART_NM
		FROM [dbo].[TB_DailyReport_S]
		WHERE INP_DTM = (SELECT MAX(INP_DTM) FROM  [dbo].[TB_DailyReport_S]) 
		AND	INST_ID IN (2, 4, 5, 6, 7, 8, 9, 11, 12, 13, 39, 50, 51, 52, 53, 54, 24, 27, 48, 21, 57, 56, 15, 16, 55, 79, 91)
		ORDER BY INST_ID ASC
	END
END