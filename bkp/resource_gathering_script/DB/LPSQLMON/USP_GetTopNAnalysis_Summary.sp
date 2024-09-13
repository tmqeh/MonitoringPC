/*=============================================
-- Author:			이지수
-- Create date:		2022-11-24
-- Description:		리소스별 부하 쿼리 Top N 통계
					(상세 : MonitoringDB.dbo.USP_GetTopNAnalysis_Detail)

					1 : Elapsed Time		- 실행 시간이 긴 쿼리 TOP N
					2 : CPU Time			- CPU 시간이 긴 쿼리 TOP N
					3 : Logical Reads		- 논리적 읽기수가 높은 쿼리 TOP N
					4 : Physical Reads		- 물리적 읽기수가 높은 쿼리 TOP N
					5 : Used Memory			- 메모리 사용량이 높은 쿼리 TOP N
					6 : TempDB Allocation	- TempDB 할당량이 높은 쿼리 TOP N
					7 : Query plan			- 실행계획이 자주 바뀌는 쿼리 TOP N

-- Modify History: 
-- Example:	
	EXEC MonitoringDB.dbo.USP_GetTopNAnalysis_Summary
		@in_searchType		= 1				
		, @in_InstanceId	= 13			
		, @in_dateFrom		= ''
		, @in_dataTo		= ''
		, @in_rankCnt		= 5
	GO
	EXEC MonitoringDB.dbo.USP_GetTopNAnalysis_Summary
		@in_searchType		= 7			
		, @in_InstanceId	= 13			
		, @in_dateFrom		= ''
		, @in_dataTo		= ''
		, @in_rankCnt		= 5
	GO
=============================================*/
CREATE PROCEDURE [dbo].[USP_GetTopNAnalysis_Summary]
	@in_searchType		TINYINT = 1				-- 검색 타입(1 : Elapsed Time, 2 : CPU Time, 3 : Logical Reads, 4 : Physical Reads, 5 : Used Memory, 6 : TempDB Allocation, 7 : Query plan)
	, @in_InstanceId	INT						-- 대상 서버는 반드시 설정해야 함
	, @in_dateFrom		VARCHAR(10) = ''
	, @in_dataTo		VARCHAR(10) = ''
	, @in_rankCnt		TINYINT = 5				-- 순위를 몇위까지 보여줄건지
AS
BEGIN

	SET NOCOUNT ON
	SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED

	DECLARE @dateFrom DATETIME2(0) 
	DECLARE @dateTo DATETIME2(0) 

	CREATE TABLE #TMP_GetTopNAnalysis_Summary_Phase1 (
		query_hash			VARBINARY(8)
		, start_time		DATETIME
		, session_id		INT
		, Indicators		BIGINT
	)
	CREATE TABLE #TMP_GetTopNAnalysis_Summary_Phase2 (
		query_hash			VARBINARY(8)
		, ExecuteCnt		INT
		, TotalIndicators	BIGINT
		, AvgIndicators		BIGINT
	)


	-- 시간 설정(안들어오면 최근 일주일)
	IF ISNULL(@in_dateFrom,'') = '' OR ISDATE(@in_dateFrom) = 0
		SET @dateFrom = CONVERT(VARCHAR(10), GETDATE()-7, 121)
	ELSE
		SET @dateFrom = @in_dateFrom

	IF ISNULL(@in_dataTo,'') = '' OR ISDATE(@in_dataTo) = 0
		SET @dateTo = CONVERT(VARCHAR(10), GETDATE(), 121) + ' 23:59:59.997'
	ELSE 
		SET @dateTo = @in_dataTo + ' 23:59:59.997'


	-- Elapsed Time
	IF @in_searchType = 1		
	BEGIN
		INSERT INTO #TMP_GetTopNAnalysis_Summary_Phase1 		
		SELECT 
			query_hash
			, start_time
			, session_id
			, MAX(total_elapsed_time) total_elapsed_time
		FROM MonitoringDB.dbo.TBL2_M_WhoIsActive W 
		WHERE W.InstanceId = @in_InstanceId 
		AND W.CollectDate BETWEEN @dateFrom AND @dateTo
		AND W.query_hash IS NOT NULL
		GROUP BY 
			query_hash
			, start_time
			, session_id
		OPTION(KEEPFIXED PLAN)

		INSERT INTO #TMP_GetTopNAnalysis_Summary_Phase2
		SELECT TOP (@in_rankCnt)
			TMP.query_hash
			, COUNT(*) AS executeCnt
			, SUM(TMP.Indicators) AS TotalIndicators
			, AVG(TMP.Indicators) AS AvgIndicators
		FROM #TMP_GetTopNAnalysis_Summary_Phase1 TMP
		GROUP BY TMP.query_hash
		ORDER BY AVG(TMP.Indicators) DESC
		OPTION(KEEPFIXED PLAN)

		SELECT
			ROW_NUMBER()OVER(ORDER BY TMP.AvgIndicators DESC) Seq
			, TMP.query_hash
			, W.sql_text
			, W.ObjectName
			, W.database_name
			, W.host_name 
			, TMP.ExecuteCnt
			, TMP.TotalIndicators AS Sum_total_elapsed_time
			, TMP.AvgIndicators AS Avg_total_elapsed_time
			, W.total_elapsed_time AS Last_total_elapsed_time
			, W.start_time AS Last_execute_time			
		FROM #TMP_GetTopNAnalysis_Summary_Phase2 TMP
		CROSS APPLY (
			SELECT TOP 1 
				W.total_elapsed_time
				, W.sql_text
				, W.database_name
				, W.ObjectName
				, W.host_name
				, W.start_time
			FROM MonitoringDB.dbo.TBL2_M_WhoIsActive W 
			WHERE W.InstanceId = @in_InstanceId 
			AND W.query_hash = TMP.query_hash
			ORDER BY W.CollectDate DESC
		) W
	END
	-- CPU Time
	ELSE IF @in_searchType = 2		
	BEGIN
		INSERT INTO #TMP_GetTopNAnalysis_Summary_Phase1 		
		SELECT 
			query_hash
			, start_time
			, session_id
			, MAX(CPU) CPU
		FROM MonitoringDB.dbo.TBL2_M_WhoIsActive W 
		WHERE W.InstanceId = @in_InstanceId 
		AND W.CollectDate BETWEEN @dateFrom AND @dateTo
		AND W.query_hash IS NOT NULL
		GROUP BY 
			query_hash
			, start_time
			, session_id
		OPTION(KEEPFIXED PLAN)

		INSERT INTO #TMP_GetTopNAnalysis_Summary_Phase2
		SELECT TOP (@in_rankCnt)
			TMP.query_hash
			, COUNT(*) AS executeCnt
			, SUM(TMP.Indicators) AS TotalIndicators
			, AVG(TMP.Indicators) AS AvgIndicators
		FROM #TMP_GetTopNAnalysis_Summary_Phase1 TMP
		GROUP BY TMP.query_hash
		ORDER BY AVG(TMP.Indicators) DESC
		OPTION(KEEPFIXED PLAN)

		SELECT
			ROW_NUMBER()OVER(ORDER BY TMP.AvgIndicators DESC) Seq
			, TMP.query_hash
			, W.sql_text
			, W.ObjectName
			, W.database_name
			, W.host_name 
			, TMP.ExecuteCnt
			, TMP.TotalIndicators AS Sum_CPU
			, TMP.AvgIndicators AS Avg_CPU
			, W.CPU AS Last_CPU
			, W.start_time AS Last_execute_time
		FROM #TMP_GetTopNAnalysis_Summary_Phase2 TMP
		CROSS APPLY (
			SELECT TOP 1 
				W.CPU
				, W.sql_text
				, W.database_name
				, W.ObjectName
				, W.host_name
				, W.start_time
			FROM MonitoringDB.dbo.TBL2_M_WhoIsActive W 
			WHERE W.InstanceId = @in_InstanceId 
			AND W.query_hash = TMP.query_hash
			ORDER BY W.CollectDate DESC
		) W
	END
	-- Logical Reads
	ELSE IF @in_searchType = 3
	BEGIN
		INSERT INTO #TMP_GetTopNAnalysis_Summary_Phase1 		
		SELECT 
			query_hash
			, start_time
			, session_id
			, MAX(reads) reads
		FROM MonitoringDB.dbo.TBL2_M_WhoIsActive W 
		WHERE W.InstanceId = @in_InstanceId 
		AND W.CollectDate BETWEEN @dateFrom AND @dateTo
		AND W.query_hash IS NOT NULL
		GROUP BY 
			query_hash
			, start_time
			, session_id
		OPTION(KEEPFIXED PLAN)

		INSERT INTO #TMP_GetTopNAnalysis_Summary_Phase2
		SELECT TOP (@in_rankCnt)
			TMP.query_hash
			, COUNT(*) AS executeCnt
			, SUM(TMP.Indicators) AS TotalIndicators
			, AVG(TMP.Indicators) AS AvgIndicators
		FROM #TMP_GetTopNAnalysis_Summary_Phase1 TMP
		GROUP BY TMP.query_hash
		ORDER BY AVG(TMP.Indicators) DESC
		OPTION(KEEPFIXED PLAN)

		SELECT
			ROW_NUMBER()OVER(ORDER BY TMP.AvgIndicators DESC) Seq
			, TMP.query_hash
			, W.sql_text
			, W.ObjectName
			, W.database_name
			, W.host_name 
			, TMP.ExecuteCnt
			, TMP.TotalIndicators AS Sum_reads
			, TMP.AvgIndicators AS Avg_reads
			, W.reads AS Last_reads
			, W.start_time AS Last_execute_time
		FROM #TMP_GetTopNAnalysis_Summary_Phase2 TMP
		CROSS APPLY (
			SELECT TOP 1 
				W.reads
				, W.sql_text
				, W.database_name
				, W.ObjectName
				, W.host_name
				, W.start_time
			FROM MonitoringDB.dbo.TBL2_M_WhoIsActive W 
			WHERE W.InstanceId = @in_InstanceId 
			AND W.query_hash = TMP.query_hash
			ORDER BY W.CollectDate DESC
		) W	
	END
	-- Physical Reads
	ELSE IF @in_searchType = 4
	BEGIN
		INSERT INTO #TMP_GetTopNAnalysis_Summary_Phase1 		
		SELECT 
			query_hash
			, start_time
			, session_id
			, MAX(physical_reads) physical_reads
		FROM MonitoringDB.dbo.TBL2_M_WhoIsActive W 
		WHERE W.InstanceId = @in_InstanceId 
		AND W.CollectDate BETWEEN @dateFrom AND @dateTo
		AND W.query_hash IS NOT NULL
		GROUP BY 
			query_hash
			, start_time
			, session_id
		OPTION(KEEPFIXED PLAN)

		INSERT INTO #TMP_GetTopNAnalysis_Summary_Phase2
		SELECT TOP (@in_rankCnt)
			TMP.query_hash
			, COUNT(*) AS executeCnt
			, SUM(TMP.Indicators) AS TotalIndicators
			, AVG(TMP.Indicators) AS AvgIndicators
		FROM #TMP_GetTopNAnalysis_Summary_Phase1 TMP
		GROUP BY TMP.query_hash
		ORDER BY AVG(TMP.Indicators) DESC
		OPTION(KEEPFIXED PLAN)

		SELECT
			ROW_NUMBER()OVER(ORDER BY TMP.AvgIndicators DESC) Seq
			, TMP.query_hash
			, W.sql_text
			, W.ObjectName
			, W.database_name
			, W.host_name 
			, TMP.ExecuteCnt
			, TMP.TotalIndicators AS Sum_physical_reads
			, TMP.AvgIndicators AS Avg_physical_reads
			, W.physical_reads AS Last_physical_reads
			, W.start_time AS Last_execute_time
		FROM #TMP_GetTopNAnalysis_Summary_Phase2 TMP
		CROSS APPLY (
			SELECT TOP 1 
				W.physical_reads
				, W.sql_text
				, W.database_name
				, W.ObjectName
				, W.host_name
				, W.start_time
			FROM MonitoringDB.dbo.TBL2_M_WhoIsActive W 
			WHERE W.InstanceId = @in_InstanceId 
			AND W.query_hash = TMP.query_hash
			ORDER BY W.CollectDate DESC
		) W	
	END
	-- Used Memory
	ELSE IF @in_searchType = 5
	BEGIN
		INSERT INTO #TMP_GetTopNAnalysis_Summary_Phase1 		
		SELECT 
			query_hash
			, start_time
			, session_id
			, MAX(used_memory) used_memory
		FROM MonitoringDB.dbo.TBL2_M_WhoIsActive W 
		WHERE W.InstanceId = @in_InstanceId 
		AND W.CollectDate BETWEEN @dateFrom AND @dateTo
		AND W.query_hash IS NOT NULL
		GROUP BY 
			query_hash
			, start_time
			, session_id
		OPTION(KEEPFIXED PLAN)

		INSERT INTO #TMP_GetTopNAnalysis_Summary_Phase2
		SELECT TOP (@in_rankCnt)
			TMP.query_hash
			, COUNT(*) AS executeCnt
			, SUM(TMP.Indicators) AS TotalIndicators
			, AVG(TMP.Indicators) AS AvgIndicators
		FROM #TMP_GetTopNAnalysis_Summary_Phase1 TMP
		GROUP BY TMP.query_hash
		ORDER BY AVG(TMP.Indicators) DESC
		OPTION(KEEPFIXED PLAN)

		SELECT
			ROW_NUMBER()OVER(ORDER BY TMP.AvgIndicators DESC) Seq
			, TMP.query_hash
			, W.sql_text
			, W.ObjectName
			, W.database_name
			, W.host_name 
			, TMP.ExecuteCnt
			, TMP.TotalIndicators AS Sum_used_memory
			, TMP.AvgIndicators AS Avg_used_memory
			, W.used_memory AS Last_used_memory
			, W.start_time AS Last_execute_time
		FROM #TMP_GetTopNAnalysis_Summary_Phase2 TMP
		CROSS APPLY (
			SELECT TOP 1 
				W.used_memory
				, W.sql_text
				, W.database_name
				, W.ObjectName
				, W.host_name
				, W.start_time
			FROM MonitoringDB.dbo.TBL2_M_WhoIsActive W 
			WHERE W.InstanceId = @in_InstanceId 
			AND W.query_hash = TMP.query_hash
			ORDER BY W.CollectDate DESC
		) W	
	END
	-- TempDB Allocation
	ELSE IF @in_searchType = 6
	BEGIN
		INSERT INTO #TMP_GetTopNAnalysis_Summary_Phase1 		
		SELECT 
			query_hash
			, start_time
			, session_id
			, MAX(tempdb_allocations) tempdb_allocations
		FROM MonitoringDB.dbo.TBL2_M_WhoIsActive W 
		WHERE W.InstanceId = @in_InstanceId 
		AND W.CollectDate BETWEEN @dateFrom AND @dateTo
		AND W.query_hash IS NOT NULL
		GROUP BY 
			query_hash
			, start_time
			, session_id
		OPTION(KEEPFIXED PLAN)

		INSERT INTO #TMP_GetTopNAnalysis_Summary_Phase2
		SELECT TOP (@in_rankCnt)
			TMP.query_hash
			, COUNT(*) AS executeCnt
			, SUM(TMP.Indicators) AS TotalIndicators
			, AVG(TMP.Indicators) AS AvgIndicators
		FROM #TMP_GetTopNAnalysis_Summary_Phase1 TMP
		GROUP BY TMP.query_hash
		ORDER BY AVG(TMP.Indicators) DESC
		OPTION(KEEPFIXED PLAN)

		SELECT
			ROW_NUMBER()OVER(ORDER BY TMP.AvgIndicators DESC) Seq
			, TMP.query_hash
			, W.sql_text
			, W.ObjectName
			, W.database_name
			, W.host_name 
			, TMP.ExecuteCnt
			, TMP.TotalIndicators AS Sum_tempdb_allocations
			, TMP.AvgIndicators AS Avg_tempdb_allocations
			, W.tempdb_allocations AS Last_tempdb_allocations
			, W.start_time AS Last_execute_time
		FROM #TMP_GetTopNAnalysis_Summary_Phase2 TMP
		CROSS APPLY (
			SELECT TOP 1 
				W.tempdb_allocations
				, W.sql_text
				, W.database_name
				, W.ObjectName
				, W.host_name
				, W.start_time
			FROM MonitoringDB.dbo.TBL2_M_WhoIsActive W 
			WHERE W.InstanceId = @in_InstanceId 
			AND W.query_hash = TMP.query_hash
			ORDER BY W.CollectDate DESC
		) W		
	END
	-- Query plan
	ELSE IF @in_searchType = 7
	BEGIN
		-- 얘는 집계 기준이 전혀 다름(전체 쿼리 실행 대비 Plan이 여러개인-재사용률이 낮은- 쿼리)
		CREATE TABLE #TMP_GetTopNAnalysis_Summary_Pre (
			query_hash			VARBINARY(8)
			, start_time		DATETIME
			, session_id		INT
			, query_plan_hash	VARBINARY(8)
		)

		INSERT INTO #TMP_GetTopNAnalysis_Summary_Pre
		SELECT DISTINCT 
			query_hash
			, start_time
			, session_id
			, query_plan_hash
		FROM MonitoringDB.dbo.TBL2_M_WhoIsActive W 
		WHERE W.InstanceId = @in_InstanceId 
		AND W.CollectDate BETWEEN @dateFrom AND @dateTo
		AND W.query_hash IS NOT NULL
		OPTION(KEEPFIXED PLAN)


		SELECT 
			ROW_NUMBER()OVER(ORDER BY TMP.Plan_per DESC) Seq
			, TMP.query_hash
			, W.sql_text
			, W.ObjectName
			, W.database_name
			, W.host_name 
			, TMP.ExecuteCnt
			, TMP.executeCnt			
			, TMP.PlanCnt
			, CONVERT(INT,TMP.Plan_per) AS Plan_reuse_percent
			, W.start_time AS Last_execute_time			
		FROM (
			SELECT TOP (@in_rankCnt) 
				query_hash
				, PlanCnt
				, executeCnt
				, ROUND(CONVERT(REAL,PlanCnt) / CONVERT(REAL,executeCnt), 4) * 100 AS Plan_per
			FROM (
				SELECT 
					query_hash
					, COUNT(DISTINCT query_plan_hash) PlanCnt
					, COUNT(*) AS executeCnt
				FROM #TMP_GetTopNAnalysis_Summary_Pre
				GROUP BY query_hash				
			) TMP
			WHERE executeCnt > 1
			AND PlanCnt > 1
			ORDER BY Plan_per DESC
		) TMP
		CROSS APPLY (
			SELECT TOP 1 
				W.sql_text
				, W.database_name
				, W.ObjectName
				, W.host_name
				, W.start_time
			FROM MonitoringDB.dbo.TBL2_M_WhoIsActive W 
			WHERE W.InstanceId = @in_InstanceId 
			AND W.query_hash = TMP.query_hash
			ORDER BY W.CollectDate DESC
		) W		
		OPTION(KEEPFIXED PLAN)

		DROP TABLE #TMP_GetTopNAnalysis_Summary_Pre
	END

	DROP TABLE #TMP_GetTopNAnalysis_Summary_Phase1
	DROP TABLE #TMP_GetTopNAnalysis_Summary_Phase2
END
