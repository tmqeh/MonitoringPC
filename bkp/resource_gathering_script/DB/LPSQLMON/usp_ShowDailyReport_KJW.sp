


/*******************************************************************************************
-- Author:		홍윤표
-- Create date: 2020.01.22
-- Description:	일일 점검 보고서
-- EXEC [dbo].[usp_ShowDailyReport]
*******************************************************************************************/
CREATE PROC [dbo].[usp_ShowDailyReport_KJW] 
AS
BEGIN
	SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
	SET NOCOUNT ON;


	SELECT	T1.JOB_NM
		  , CASE WHEN AGENT_WRK_FAIL_CNT > 0 THEN '[ERROR] AGENT JOB' ELSE '' END
		  + CASE WHEN ERR_LOG_CNT > 0 THEN '[ERROR] LOG' ELSE '' END 
		  + CASE WHEN BLK_TM > 10000 THEN '[ERROR] BLOCKING TIME' ELSE '' END
		  + CASE WHEN CPU_PCT > 90 THEN '[ERROR] CPU' ELSE '' END
		  + CASE WHEN MEM_CHECK <> 0 THEN '[ERROR] MEMORY' ELSE '' END
		  + CASE WHEN USE1 > 95 THEN '[ERROR] DRVIE : ' + DRV1 ELSE '' END
		  + CASE WHEN USE2 > 95 THEN '[ERROR] DRVIE : ' + DRV2 ELSE '' END
		  + CASE WHEN USE3 > 95 THEN '[ERROR] DRVIE : ' + DRV3 ELSE '' END
		  + CASE WHEN USE4 > 95 THEN '[ERROR] DRVIE : ' + DRV4 ELSE '' END
		  + CASE WHEN USE5 > 95 THEN '[ERROR] DRVIE : ' + DRV5 ELSE '' END
		  + CASE WHEN USE6 > 95 THEN '[ERROR] DRVIE : ' + DRV6 ELSE '' END
		  + CASE WHEN USE7 > 95 THEN '[ERROR] DRVIE : ' + DRV7 ELSE '' END
		  + CASE WHEN USE8 > 95 THEN '[ERROR] DRVIE : ' + DRV8 ELSE '' END
	FROM	
	(
		SELECT 
				DATEDIFF(SS,CLCT_DTM,GETDATE()) CLCT_CHK,
				[INST_ID],
				[JOB_NM],
				[IP_ADDR],
				[CLU_NODE_NM],
				[CLU_CMPS_YN],
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
				[CLCT_DTM]			
		FROM [dbo].[TB_DailyReport_S]
		WHERE INP_DTM = (SELECT MAX(INP_DTM) FROM  [dbo].[TB_DailyReport_S]) 
		AND	INST_ID IN (2, 4, 5, 6, 7, 8, 9, 11, 12, 13, 39, 50, 51, 52, 53, 54, 24, 27, 48, 21, 57, 56, 15, 16, 55, 79)
	) T1

END