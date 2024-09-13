
-- =============================================
-- Author:		홍윤표
-- Create date: 2019.12.10
-- Description:	월간 보고서 MS-SQL 리포트
-- =============================================
CREATE PROCEDURE [dbo].[usp_ShowMonthlyReport]
	-- Add the parameters for the stored procedure here
	
AS
BEGIN
	-- SET NOCOUNT ON added to prevent extra result sets from
	-- interfering with SELECT statements.
	/* 쿼리 몸체 */
	SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
	SET NOCOUNT ON;

	-- 디스크 사용량, 증가 추이
	WITH Result AS (
		SELECT CONVERT(CHAR(10), dku.CollectDate, 111) AS 'CollectDate',
			   ins.ServerName+ ' '+ dku.Drive AS 'SVR_Drive',
			   ISNULL (MAX( CONVERT(decimal(5, 2), ROUND((ISNULL(dku.TotalSpaceMB,dt.TotalSpaceMB) - dku.FreeSpaceMB) / ISNULL(dku.TotalSpaceMB,dt.TotalSpaceMB) * 100, 2))), 0) AS 'DiskUtilization'
		FROM [dbo].[META2_M_InstanceInfo] AS ins 
		INNER JOIN [dbo].[TBL2_M_DatabaseDiskUsage] AS dku ON ins.InstanceID = dku.InstanceID
		LEFT JOIN (
			SELECT 'F:\' AS Drive, 409597 AS TotalSpaceMB
			UNION ALL
			SELECT 'G:\' AS Drive, 153597 AS TotalSpaceMB
		) dt ON dku.Drive = dt.Drive AND dku.InstanceID = 21				-- SQL Server 2008 이하 버전에서는 TotalSpace가 수집이 안됨, 법인영업 드라이브 상수값으로 고정(이지수 수정 2022-11-21)
		WHERE ins.UseYN = 'Y'
		GROUP BY CONVERT(CHAR(10), dku.CollectDate, 111), ins.ServerName, dku.Drive
	)
	SELECT * 
	FROM Result
	PIVOT (MAX(Result.DiskUtilization) FOR Result.SVR_Drive IN ( "[MD]아카이브 E:\",
																"[MD]아카이브 F:\",
																"[MD]아카이브 G:\",
																"[MD]아카이브 H:\",
																"[MD]아카이브 I:\",
																"[MD]아카이브 J:\",
																"[POS] (구)전자저널 F:\",
																"[POS] (구)전자저널 G:\",
																"[POS] (구)전자저널 H:\",
																"[POS] (구)전자저널 I:\",
																"[POS] (구)전자저널 J:\",
																"[POS] (구)전자저널 K:\",
																"[POS] AMS#1 C:\",
																"[POS] AMS#1 D:\",
																"[POS] AMS#2 C:\",
																"[POS] AMS#2 E:\",
																"[POS] SCOM C:\",
																"[POS] SCOM E:\",
																"[POS] 동기화 D:\",
																"[POS] 동기화 E:\",
																"[POS] 동기화 F:\",
																"[POS] 동기화 G:\",
																"[POS] 매출 F:\",
																"[POS] 매출 G:\",
																"[POS] 매출 H:\",
																"[POS] 매출 I:\",
																"[POS] 푸드키오스크#1 C:\",
																"[POS] 푸드키오스크#1 D:\",
																"[POS] 푸드키오스크#1 E:\",
																"[POS] 푸드키오스크#2 C:\",
																"[POS] 푸드키오스크#2 D:\",
																"[POS] 푸드키오스크#2 E:\",
                                                                "[마케팅] (신)사은 F:\",
                                                                "[마케팅] (신)사은 G:\",
                                                                "[마케팅] (신)사은 H:\",
                                                                "[마케팅] (신)사은 I:\",
                                                                "[마케팅] (신)사은 J:\",
                                                                "[마케팅] (신)사은 O:\",
                                                                "[마케팅] (신)사은 P:\",
                                                                "[마케팅] (신)에누리 F:\",
                                                                "[마케팅] (신)에누리 G:\",
                                                                "[마케팅] (신)에누리 H:\",
                                                                "[마케팅] (신)에누리 I:\",
                                                                "[마케팅] (신)에누리 J:\",
                                                                "[마케팅] (신)에누리 N:\",
                                                                "[마케팅] (신)에누리 O:\",
                                                                "[마케팅] (신)에누리 P:\",
																"[마케팅] 법인영업 F:\",
																"[마케팅] 법인영업 G:\",
                                                                "[인프라] ECM#1 D:\",
                                                                "[인프라] ECM#1 F:\",
                                                                "[인프라] ECM#2 D:\",
                                                                "[인프라] ECM#2 F:\",
                                                                "[인프라] DRM F:\",
                                                                "[인프라] DRM O:\",
                                                                "[인프라] DRM P:\",
																"[인프라] SCCM C:\", 
																"[재무] 통합구매 F:\",
																"[재무] 통합구매 G:\",
																"[재무] 통합구매 H:\",
																"[재무] 통합구매 P:\",
																"[재무] 통합구매 O:\",
																"[재무] 통합구매 I:\",
																"[재무] EAI D:\",
																"[재무] EAI E:\",
																"[재무] EAI F:\",
																"[재무] 재무통합 D:\",
																"[재무] 재무통합 E:\",
																"[재무] 재무통합 F:\",
																"[재무] 증빙 G:\",
																"[재무] 증빙 H:\",
																"[재무] 증빙 i:\",
																"[재무] 내부회계 G:\",
																"[재무] 내부회계 H:\",
																"[재무] 내부회계 I:\" )
	) AS PVT
	ORDER BY CollectDate;

	/*-- 디스크 사용량, 증가 추이
		디스크 사용량, 데이터 증가 추이 상세 개발 필요
	*/
	

	-- 월별 CPU 사용량 평균
	WITH Result AS (
		SELECT ins.ServerName,
			   pef.hh_mm,
			   pef.CounterValue 
		FROM [dbo].[META2_M_InstanceInfo] AS ins 
			INNER JOIN [dbo].[TBL2_M_Perfmon_Avg_Month] AS pef 
			ON ins.InstanceID = pef.InstanceID
		WHERE pef.CounterName = 'Processor\% Processor Time(_Total)' AND
			  ins.UseYN = 'Y' AND 
		(hh_mm LIKE '00:00' OR hh_mm LIKE '01:00' OR hh_mm LIKE '02:00' OR hh_mm LIKE '03:00' OR hh_mm LIKE '04:00' OR hh_mm LIKE '05:00' OR
		 hh_mm LIKE '06:00' OR hh_mm LIKE '07:00' OR hh_mm LIKE '08:00' OR hh_mm LIKE '09:00' OR hh_mm LIKE '10:00' OR hh_mm LIKE '11:00' OR
		 hh_mm LIKE '12:00' OR hh_mm LIKE '13:00' OR hh_mm LIKE '14:00' OR hh_mm LIKE '15:00' OR hh_mm LIKE '16:00' OR hh_mm LIKE '17:00' OR
		 hh_mm LIKE '18:00' OR hh_mm LIKE '19:00' OR hh_mm LIKE '20:00' OR hh_mm LIKE '21:00' OR hh_mm LIKE '22:00' OR hh_mm LIKE '23:00')
	)
	SELECT *
	FROM Result
		 PIVOT (MAX(Result.CounterValue) FOR Result.ServerName IN ("[POS] 매출",
																   "[POS] 동기화",
																   "[POS] AMS#1",
																   "[POS] AMS#2",
																   "[POS] SCOM",
																   "[POS] 푸드키오스크#1",
																   "[POS] 푸드키오스크#2",
																   "[POS] (구)전자저널",
																   "[MD]아카이브",
                                                                   "[마케팅] (신)사은",
                                                                   "[마케팅] (신)에누리",
                                                                   "[인프라] ECM#1",
                                                                   "[인프라] ECM#2",
                                                                   "[인프라] DRM",
                                                                   "[인프라] SCCM"
																   )
	) AS PVT
	ORDER BY hh_mm;


	-- 월별 메모리 사용량 평균
	WITH Result AS (
		SELECT ins.ServerName,
			   pef.hh_mm,
			   ( (CONVERT(decimal, LEFT(sbi.PhysicalMemory, CHARINDEX(' ', sbi.PhysicalMemory))) - pef.CounterValue) 
			   / CONVERT(decimal, LEFT(sbi.PhysicalMemory, CHARINDEX(' ', sbi.PhysicalMemory))) ) * 100.0 AS CounterValue
		FROM [dbo].[META2_M_InstanceInfo] AS ins 
			INNER JOIN [dbo].[TBL2_M_Perfmon_Avg_Month] AS pef 
			ON ins.InstanceID = pef.InstanceID
				INNER JOIN  [dbo].[TBL2_M_ServerBasicInfo] AS sbi 
				ON pef.InstanceID = sbi.InstanceID AND CONVERT(VARCHAR(8), sbi.CollectDate, 112) = CONVERT(VARCHAR(8), GETDATE(), 112)
		WHERE pef.CounterName = 'Memory\Available MBytes' AND
			  ins.UseYN = 'Y' AND 
		(hh_mm LIKE '00:00' OR hh_mm LIKE '01:00' OR hh_mm LIKE '02:00' OR hh_mm LIKE '03:00' OR hh_mm LIKE '04:00' OR hh_mm LIKE '05:00' OR
		 hh_mm LIKE '06:00' OR hh_mm LIKE '07:00' OR hh_mm LIKE '08:00' OR hh_mm LIKE '09:00' OR hh_mm LIKE '10:00' OR hh_mm LIKE '11:00' OR
		 hh_mm LIKE '12:00' OR hh_mm LIKE '13:00' OR hh_mm LIKE '14:00' OR hh_mm LIKE '15:00' OR hh_mm LIKE '16:00' OR hh_mm LIKE '17:00' OR
		 hh_mm LIKE '18:00' OR hh_mm LIKE '19:00' OR hh_mm LIKE '20:00' OR hh_mm LIKE '21:00' OR hh_mm LIKE '22:00' OR hh_mm LIKE '23:00')
	)
	SELECT *
	FROM Result
		 PIVOT (MAX(Result.CounterValue) FOR Result.ServerName IN ("[POS] 매출",
																   "[POS] 동기화",
																   "[POS] AMS#1",
																   "[POS] AMS#2",
																   "[POS] SCOM",
																   "[POS] 푸드키오스크#1",
																   "[POS] 푸드키오스크#2",
																   "[POS] (구)전자저널",
																   "[MD]아카이브",
                                                                   "[마케팅] (신)사은",
                                                                   "[마케팅] (신)에누리",
                                                                   "[인프라] ECM#1",
                                                                   "[인프라] ECM#2",
                                                                   "[인프라] DRM",
                                                                   "[인프라] SCCM"
																   )
	) AS PVT
	ORDER BY hh_mm;
END
