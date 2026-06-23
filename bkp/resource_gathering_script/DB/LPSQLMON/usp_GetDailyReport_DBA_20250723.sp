
-- =============================================
-- Author:		홍윤표
-- Create date: 2019.12.10
-- Description:	일일점검 보고서 MS-SQL 리포트
-- =============================================
CREATE PROCEDURE [dbo].[usp_GetDailyReport_DBA_20250723]
	-- Add the parameters for the stored procedure here
	
AS
BEGIN
	-- SET NOCOUNT ON added to prevent extra result sets from
	-- interfering with SELECT statements.
	SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
	SET NOCOUNT ON;
	SET ANSI_WARNINGS OFF;

	---------------------------------------------------------------------------
	--BlockingInfo, 2021-02-26 Blocking모니터링 추가 [dbo].[USP2_M_SEL_DashBoardAll]에서 발췌	
	---------------------------------------------------------------------------
	DECLARE @DateSearchTo DATETIME 
	DECLARE @DateSearchFrom DATETIME

	--최근 15분동안 
	SET @DateSearchTo = GETDATE()
	SET @DateSearchFrom = DATEADD(minute, -10, @DateSearchTo)

	IF OBJECT_ID('tempdb..#TMP_GetDailyReport_ServerActivity') IS NOT NULL
		DROP TABLE #TMP_GetDailyReport_ServerActivity

	IF OBJECT_ID('tempdb..#TMP_GetDailyReport_DiskUsage') IS NOT NULL
		DROP TABLE #TMP_GetDailyReport_DiskUsage

	DECLARE @TABLEBlocking TABLE (
		 InstanceID				INT
		,BlockingWaittime		BIGINT
	)
	CREATE TABLE #TMP_GetDailyReport_ServerActivity (
		ClusterOwnerNode		NVARCHAR(200)
		, InstanceID			INT
		, CollectDate			DATETIME	
	)
	CREATE TABLE #TMP_GetDailyReport_DiskUsage (
		InstanceID				INT
		, DRV1					VARCHAR(5)
		, USE1					INT
		, DRV2					VARCHAR(5)
		, USE2					INT
		, DRV3					VARCHAR(5)
		, USE3					INT
		, DRV4					VARCHAR(5)
		, USE4					INT
		, DRV5					VARCHAR(5)
		, USE5					INT
		, DRV6					VARCHAR(5)
		, USE6					INT
		, DRV7					VARCHAR(5)
		, USE7					INT
		, DRV8					VARCHAR(5)
		, USE8					INT
		, DRV9					VARCHAR(5)
		, USE9					INT
	)

	INSERT INTO @TABLEBlocking
	SELECT InstanceID, CONVERT(BIGINT,MAX(BlockingWaittime)) BlockingWaittime
	FROM (
		SELECT
			a.InstanceID,	
				a.total_elapsed_time BlockingWaittime
		FROM	[dbo].[TBL2_M_WhoIsActive] a WITH (NOLOCK)
		INNER	JOIN dbo.META2_M_LastCollectInfo d WITH (NOLOCK) ON		a.InstanceID = d.InstanceID AND		d.CollectItem = N'WhoIsActive'
		CROSS	APPLY (
			SELECT	TOP 1 CollectDate LastCollectDate 
			FROM	dbo.[TBL2_M_WhoIsActive] WITH (NOLOCK)
			WHERE	InstanceID = a.InstanceID
			AND		CollectDate BETWEEN DATEADD(MINUTE, DATEDIFF(MINUTE, LastCollectDateMonitoring, LastCollectDateTarget), @DateSearchFrom)
			AND		DATEADD(MINUTE, DATEDIFF(MINUTE, LastCollectDateMonitoring, LastCollectDateTarget), @DateSearchTo)
			ORDER	BY CollectDate DESC
		) c
		WHERE	a.CollectDate = c.LastCollectDate
		AND		a.CollectDate BETWEEN DATEADD(MINUTE, DATEDIFF(MINUTE, d.LastCollectDateMonitoring, d.LastCollectDateTarget), @DateSearchFrom)
		AND		DATEADD(MINUTE, DATEDIFF(MINUTE, d.LastCollectDateMonitoring, d.LastCollectDateTarget), @DateSearchTo)
		AND		blocking_session_id > 0
	) AS a
	GROUP BY InstanceID

	INSERT INTO #TMP_GetDailyReport_ServerActivity
	SELECT 
		ClusterOwnerNode
		, InstanceID
		, CollectDate
	FROM (
		SELECT
			ROW_NUMBER()OVER(PARTITION BY InstanceID ORDER BY CollectDate DESC) RN
			, ClusterOwnerNode
			, InstanceID
			, CollectDate
		FROM [dbo].[TBL2_M_ServerActivity]           --서버 Active 3정보 (2분 마다 수집)
		WHERE CollectDate >= CONVERT(VARCHAR(10), GETDATE(), 23) + ' 00:00:00.000'
		AND CollectDate < CONVERT(VARCHAR(10), DATEADD(DAY, 1, GETDATE()), 23) + ' 00:00:00.000'
	) sa
	WHERE sa.RN = 1
	OPTION(KEEPFIXED PLAN, MAXDOP 1)

	INSERT INTO #TMP_GetDailyReport_DiskUsage
	SELECT InstanceID,
			MAX("DRV1") as DRV1, MAX("USE1") as USE1,
			MAX("DRV2") as DRV2, MAX("USE2") as USE2,
           MAX("DRV3") as DRV3, MAX("USE3") as USE3,
           MAX("DRV4") as DRV4, MAX("USE4") as USE4,
           MAX("DRV5") as DRV5, MAX("USE5") as USE5,
           MAX("DRV6") as DRV6, MAX("USE6") as USE6,
           MAX("DRV7") as DRV7, MAX("USE7") as USE7,
           MAX("DRV8") as DRV8, MAX("USE8") as USE8,
           MAX("DRV9") as DRV9, MAX("USE9") as USE9
	FROM (
		SELECT INSTANCEID, DRIVE, USEDDISK, 
				CASE WHEN LETTER_RNK = 1 THEN 'DRV1'
					WHEN LETTER_RNK = 2 THEN 'DRV2'
					WHEN LETTER_RNK = 3 THEN 'DRV3'
					WHEN LETTER_RNK = 4 THEN 'DRV4'
					WHEN LETTER_RNK = 5 THEN 'DRV5'
					WHEN LETTER_RNK = 6 THEN 'DRV6'
					WHEN LETTER_RNK = 7 THEN 'DRV7'
					WHEN LETTER_RNK = 8 THEN 'DRV8'
					WHEN LETTER_RNK = 9 THEN 'DRV9'
				END as LETTER_RNK,
				CASE WHEN USED_RNK = 1 THEN 'USE1'
					WHEN USED_RNK = 2 THEN 'USE2'
					WHEN USED_RNK = 3 THEN 'USE3'
					WHEN USED_RNK = 4 THEN 'USE4'
					WHEN USED_RNK = 5 THEN 'USE5'
					WHEN USED_RNK = 6 THEN 'USE6'
					WHEN USED_RNK = 7 THEN 'USE7'
					WHEN USED_RNK = 8 THEN 'USE8'
					WHEN USED_RNK = 9 THEN 'USE9'
				END AS USED_RNK
		FROM (
           SELECT      iB.InstanceID
                       ,CASE WHEN iB.Drive LIKE '\\%' THEN 'NAS' ELSE iB.Drive END Drive
                       ,iB.UsedDisk
                       ,RANK() OVER(PARTITION BY iB.InstanceID ORDER BY iB.drive) LETTER_RNK
                       ,RANK() OVER(PARTITION BY iB.InstanceID ORDER BY iB.drive) USED_RNK
           FROM (
               SELECT    InstanceID
                           ,CONVERT(VARCHAR(10), MAX(CollectDate), 23) AS "CollectDate"
               FROM    TBL2_M_DatabaseDiskUsage
               GROUP   BY InstanceID
           ) AS iA
           INNER   JOIN(
				SELECT   CONVERT(VARCHAR(10), DU.CollectDate, 23) AS "CollectDate"
						,DU.InstanceID
						,DU.Drive
						,CONVERT(decimal(5, 2), ROUND(MAX(ISNULL(DU.TotalSpaceMB, DT.TotalSpaceMB) - FreeSpaceMB) / MAX(ISNULL(DU.TotalSpaceMB, DT.TotalSpaceMB)) * 100, 2)) AS "UsedDisk"							
				FROM    TBL2_M_DatabaseDiskUsage DU                                                                  -- 디스크 사용량 정보 (매일 7:30시 수집)
				LEFT JOIN (
					SELECT 'F:\' AS Drive, 409597 AS TotalSpaceMB
					UNION ALL
					SELECT 'G:\' AS Drive, 153597 AS TotalSpaceMB
				) DT ON DU.Drive = DT.Drive AND DU.InstanceID = 21													-- SQL Server 2008 이하 버전에서는 TotalSpace가 수집이 안됨, 법인영업 드라이브 상수값으로 고정(이지수 수정 2022-11-21)
				WHERE   CollectDate >= CONVERT(VARCHAR(10), DATEADD(DAY, -1, GETDATE()), 23) + ' 00:00:00.000'
				AND     CollectDate < CONVERT(VARCHAR(10), DATEADD(DAY, 1, GETDATE()), 23) + ' 00:00:00.000'
				GROUP   BY CONVERT(VARCHAR(10), DU.CollectDate, 23), DU.InstanceID, DU.Drive
           ) AS iB ON iA.CollectDate = iB.CollectDate AND iA.InstanceID = iB.InstanceID
		) AS X
	) AS A
	PIVOT (MAX(Drive)    FOR LETTER_RNK IN("DRV1","DRV2","DRV3","DRV4","DRV5","DRV6","DRV7","DRV8","DRV9")) AS PVT
	PIVOT (MAX(USEDDISK) FOR USED_RNK   IN("USE1","USE2","USE3","USE4","USE5","USE6","USE7","USE8","USE9")) AS PVT2
	GROUP BY InstanceID
	OPTION(KEEPFIXED PLAN, MAXDOP 1)


	/* 쿼리 몸체 */
	INSERT INTO [dbo].[TB_DailyReport_S] (
		[CLCT_DTM],
		[INST_ID], 
		[JOB_NM],
		[IP_ADDR], 
		[CLU_NODE_NM],
		[CLU_CMPS_YN],
		[AGENT_WRK_FAIL_CNT],
		[ERR_LOG_CNT],	
		[CPU_PCT],
		[MEM_TOTAL_SIZE],
		[MEM_FREE_SIZE],
		[MEM_USE_PCT],
		[MEM_CHECK],
		[DRV1] ,
		[USE1] ,
		[DRV2] ,
		[USE2] ,
		[DRV3] ,
		[USE3] ,
		[DRV4] ,
		[USE4] ,
		[DRV5] ,
		[USE5] ,
		[DRV6] ,
		[USE6] ,
		[DRV7] ,
		[USE7] ,
		[DRV8] ,
		[USE8] ,
		[DRV9] ,
		[USE9] ,
		[BLK_TM] )
	SELECT   
		sa.CollectDate
		,ii.InstanceID
		,ii.ServerName                                          AS "업무"
		,sb.ServiceIP                                           AS "IP"
		,sa.ClusterOwnerNode                                    AS "클러스터 Active 노드"
		,CASE WHEN sb.IsClustered = 1 THEN 'Y' ELSE 'N' END     AS "클러스터 구성 여부"
		,ISNULL(aj.FailedCount, 0)                              AS "Agent Job 실패 건수"
		,ISNULL(er.ErrorCount , 0)                              AS "Error 로그 건수"
		,CPU.CPU_PCT                                            AS "CPU 사용량(%)"
		,CONVERT(decimal(10, 2), ROUND(um.TotalMemSize, 2))     AS "물리 메모리 TOTAL"
		,CONVERT(decimal(10, 2), ROUND(um.FreeMemSize, 2))      AS "물리 메모리 FREE"
		,CONVERT(decimal(5, 2), ROUND(um.UsedMemory, 2))        AS "물리 메모리 사용량(%)"
		,CASE WHEN CONVERT(decimal(5, 2), ROUND(um.UsedMemory, 2)) > 85 AND CONVERT(decimal(10, 2), ROUND(um.FreeMemSize, 2)) < 4096 THEN '1' --경고
			  ELSE '0' --정상
	     END                                                    AS "MEM_CHECK"
		--ud.[A:\], ud.[B:\], ud.[C:\], ud.[D:\], ud.[E:\], ud.[F:\], ud.[G:\], ud.[H:\], ud.[I:\], ud.[J:\], ud.[K:\], ud.[L:\], ud.[M:\], 
		--ud.[N:\], ud.[O:\], ud.[P:\], ud.[Q:\], ud.[R:\], ud.[S:\], ud.[T:\], ud.[U:\], ud.[V:\], ud.[W:\], ud.[X:\], ud.[Y:\], ud.[Z:\]
		,dk.DRV1, dk.USE1
		,dk.DRV2, dk.USE2
		,dk.DRV3, dk.USE3
		,dk.DRV4, dk.USE4
		,dk.DRV5, dk.USE5
		,dk.DRV6, dk.USE6
		,dk.DRV7, dk.USE7
		,dk.DRV8, dk.USE8
		,dk.DRV9, dk.USE9
		,ISNULL(tb.BlockingWaittime, 0)
	FROM [dbo].[META2_M_InstanceInfo] AS ii                      -- 인스턴스 기본 정보
	INNER LOOP JOIN [dbo].[TBL2_M_ServerBasicInfo] AS sb ON ii.InstanceID = sb.InstanceID AND sb.CollectDate BETWEEN CONVERT(varchar(10), GETDATE(), 121) AND CONVERT(varchar(10), GETDATE(), 121) + ' 23:59:59.997' -- 서버 기본 정보 (매일 0:00시 수집)
	LEFT OUTER JOIN @TABLEBlocking tb ON ii.InstanceID = tb.InstanceID													-- [Blocking 정보 JOIN]	
	LEFT OUTER JOIN #TMP_GetDailyReport_ServerActivity AS sa ON ii.InstanceID = sa.InstanceID
    LEFT OUTER JOIN (                                                                                                            -- [AgentJob 정보 JOIN]
		SELECT   
			InstanceID 
		    ,COUNT(DISTINCT JobName +  CONVERT(VARCHAR,LastRunDateTime) +  LastRunStatusMessage + CONVERT(VARCHAR,NextRunDateTime) +  CONVERT(VARCHAR,CreatedDate ))  AS "FailedCount"
		FROM [dbo].[TBL2_M_AgentJobInfo]
		WHERE LastRunDateTime >= CONVERT(varchar(10), DATEADD(DAY, -1, GETDATE()), 23) + ' 00:00:00.000' --전일부터 당일까지의 실패 수집
		AND LastRunStatus IN ('Failed','Warning')														/* 마지막 실행 상태 Warning 추가(2024-04-08, 이지수) */
		AND Enabled = 'Y'
		GROUP BY InstanceID
    ) AS aj ON ii.InstanceID = aj.InstanceID
	LEFT OUTER JOIN (
		SELECT InstanceID, COUNT(*) AS ErrorCount
		FROM (
			SELECT InstanceID, CONVERT(VARCHAR, LOG_DATE) LOG_DATE, PROCESS_INFO, ERRORLOG_TEXT
			FROM    [dbo].[TBL2_M_SqlErrorlog]
			WHERE   LOG_DATE >= CONVERT(varchar(10), DATEADD(DAY, -1, GETDATE()), 23) + ' 00:00:00.000'         --전일부터 당일까지의 에러 로그 수집
 			AND     PROCESS_INFO NOT IN ('Logon', '로그온', 'Backup', '백업')	
 			AND	    (ERRORLOG_TEXT LIKE '%error%' OR ERRORLOG_TEXT LIKE '%failed%')
 			AND		(ERRORLOG_TEXT NOT LIKE '%Logging SQL Server messages in file%' AND 
 						ERRORLOG_TEXT NOT LIKE '%The error log has been reinitialized. See the previous log for older entries.%' AND
 						ERRORLOG_TEXT NOT LIKE 'Attempting to cycle%')
			GROUP BY InstanceID, CONVERT(VARCHAR, LOG_DATE), PROCESS_INFO, ERRORLOG_TEXT
		) AS er
 		GROUP BY instanceID	
	) AS er ON ii.InstanceID = er.InstanceID
	LEFT OUTER JOIN (																							-- 물리 메모리 사용량 JOIN -> 수정 필요
		SELECT   
			A.InstanceID
			, MAX(A.CollectDate) AS "CollectDate"
			, MAX(CAST(LEFT(A.PhysicalMemory, CHARINDEX('(', A.PhysicalMemory) - 1) AS decimal) - B.CounterValue) / MAX(CAST(LEFT(A.PhysicalMemory, CHARINDEX('(', A.PhysicalMemory) - 1) AS decimal)) * 100 AS "UsedMemory"
			, MAX(CAST(LEFT(A.PhysicalMemory, CHARINDEX('(', A.PhysicalMemory) - 1) AS decimal)) AS "TotalMemSize"
			, MAX(B.CounterValue) AS "FreeMemSize"
		FROM TBL2_M_ServerBasicInfo AS A 
		CROSS APPLY (
			SELECT DISTINCT
				AA.InstanceID
				, CONVERT(VARCHAR(8),AA.CollectDate,112) CollectDate
				, AA.CounterValue
			FROM (
				SELECT TOP 1 
					CollectDate
					, InstanceID 
				FROM TBL2_M_Perfmon
				WHERE CounterName = 'Memory\Available MBytes'
				AND InstanceID = A.InstanceID 
				ORDER BY CollectDate DESC
			) BB
			INNER JOIN TBL2_M_Perfmon AS AA ON AA.InstanceID = BB.InstanceID AND AA.CollectDate = BB.CollectDate
			WHERE AA.CounterName = 'Memory\Available MBytes'
		) B
		WHERE B.CollectDate = CONVERT(varchar(8), A.CollectDate, 112)
		GROUP BY A.InstanceID
	) AS um ON ii.InstanceID = um.InstanceID
	LEFT OUTER JOIN (																					   -- CPU 사용량 JOIN
        SELECT InstanceID
              ,CounterName
              ,CollectDate
              ,CounterValue AS "CPU_PCT"
          FROM (
                SELECT InstanceID
                      ,CounterName
                	  ,CollectDate
                	  ,CounterValue
                	  ,ROW_NUMBER()  OVER(PARTITION BY InstanceID ORDER BY CollectDate DESC) AS RN
                  FROM [dbo].[TBL2_M_Perfmon]
                 WHERE 1=1
                   AND CounterName = 'Processor\% Processor Time(_Total)'
        		   AND CollectDate >= SUBSTRING(CONVERT(VARCHAR, GETDATE(), 120), 1, 11) + ' 00:00:00'
               ) CPU
         WHERE CPU.RN = 1
	) AS cpu ON ii.InstanceID = cpu.InstanceID
	LEFT OUTER JOIN #TMP_GetDailyReport_DiskUsage AS dk ON ii.InstanceID = dk.InstanceID															-- 디스크 사용량 JOIN		
	WHERE ii.UseYN = 'Y'
	OPTION(HASH GROUP, MAXDOP 1)

	DROP TABLE #TMP_GetDailyReport_ServerActivity
	DROP TABLE #TMP_GetDailyReport_DiskUsage
END
