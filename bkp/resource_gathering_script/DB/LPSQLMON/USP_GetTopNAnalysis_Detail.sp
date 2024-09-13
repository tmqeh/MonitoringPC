/*=============================================
-- Author:			이지수
-- Create date:		2022-11-25
-- Description:		리소스별 부하 쿼리 상세
					(통계 : MonitoringDB.dbo.USP_GetTopNAnalysis_Summary)
					
					<참고 - 대기유형> 
						CXPACKET, CXCONSUMER, EXECSYNC	: 병렬처리 관련
						WRITELOG						: TRANSACTION 관련(지나치게 잦은 커밋)
						SLEEP_TASK, IO_COMPLETION		: TEMPDB 관련(SLEEP_TASK : HASH, IO_COMPLETION : SORT)
						OLEDB							: 연결된 서버 관련(주로 다른 디비 연결하는데 원격지 DB에서 응답이 없어 기다릴때 나타남)	
						PAGEIOLATCH%					: PAGEIO LATCH(디스크IO 경합 : 메모리->디스크 올려줄때, 인덱스 스캔이나 물리 읽기 많이 발생하면 나타남)
						PAGELATCH%						: PAGE LATCH(페이지 할당 과정에서의 경합 : 인덱스나 PK에 DML 일어나는 경우..)
						LATCH%							: LATCH(메모리 경합 : 과도한 병렬처리, 데이터 증가시, 힙/BLOB 데이터에 대한 잦은 DML 등...)
						LCK%							: LOCK

-- Modify History: 
-- Example:	
	EXEC MonitoringDB.dbo.USP_GetTopNAnalysis_Detail
		@in_InstanceId		= 13
		, @in_query_hash	= 0x1CE372FDA04B4333
		, @in_dateFrom		= ''
		, @in_dataTo		= ''
		, @in_viewCnt		= 4
		, @in_searchType	= 0
	GO
	EXEC MonitoringDB.dbo.USP_GetTopNAnalysis_Detail
		@in_InstanceId		= 13
		, @in_query_hash	= 0x1CE372FDA04B4333
		, @in_dateFrom		= ''
		, @in_dataTo		= ''
		, @in_viewCnt		= 0
		, @in_searchType	= 4
	GO
=============================================*/
CREATE PROCEDURE dbo.USP_GetTopNAnalysis_Detail
	@in_InstanceId		INT						-- 대상 서버는 반드시 설정해야 함
	, @in_query_hash	VARBINARY(8)			-- 상세 페이지이므로 반드시 들어가야 함
	, @in_dateFrom		VARCHAR(10) = ''
	, @in_dataTo		VARCHAR(10) = ''
	, @in_viewCnt		TINYINT = 0				-- 0으로 설정하면 모두 보겠다는 뜻(통계에서는 순위 몇개까지 보여줄건지 설정하는거라 좀 다름)
	, @in_searchType	TINYINT = 0				-- 정렬 기준(0 : CollectDate, 1 : Elapsed Time, 2 : CPU Time, 3 : Logical Reads, 4 : Physical Reads, 5 : Used Memory, 6 : TempDB Allocation)
AS
BEGIN

	SET NOCOUNT ON
	SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED

	DECLARE @dateFrom DATETIME2(0) 
	DECLARE @dateTo DATETIME2(0) 

	-- 시간 설정(안들어오면 최근 일주일)
	IF ISNULL(@in_dateFrom,'') = '' OR ISDATE(@in_dateFrom) = 0
		SET @dateFrom = CONVERT(VARCHAR(10), GETDATE()-7, 121)
	ELSE
		SET @dateFrom = @in_dateFrom

	IF ISNULL(@in_dataTo,'') = '' OR ISDATE(@in_dataTo) = 0
		SET @dateTo = CONVERT(VARCHAR(10), GETDATE(), 121) + ' 23:59:59.997'
	ELSE 
		SET @dateTo = @in_dataTo + ' 23:59:59.997'

	
	SET ROWCOUNT @in_viewCnt

	SELECT 
		TOT.CollectDate
		, TOT.start_time
		, TOT.session_id
		, TOT.status
		, TOT.sql_text
		, TOT.WaitType
		, TOT.IsolationLevel
		, TOT.database_name
		, TOT.ObjectName
		, TOT.total_elapsed_time
		, TOT.CPU
		, TOT.tempdb_allocations
		, TOT.tempdb_current
		, TOT.used_memory
		, TOT.reads
		, TOT.physical_reads
		, TOT.login_name
		, TOT.open_tran_count
		, TOT.blocking_session_id
		, TOT.host_name
		, TOT.program_name		 
	FROM (
		SELECT
			-- 중복으로 수집되는 건들은 최근 한건만, 단 우선순위가 높은 WaitType이 있으면 그걸 우선적으로 보여줌
			ROW_NUMBER()OVER(
				PARTITION BY session_id, start_time 
				ORDER BY 
					(CASE 
						WHEN TOT.WaitType LIKE 'LCK%'			THEN 1		-- 락은 가장 중요
						WHEN TOT.WaitType LIKE 'PAGELATCH%' 
							OR TOT.WaitType LIKE 'PAGEIOLATCH%'	
							OR TOT.WaitType LIKE 'LATCH%'		THEN 2		-- 래치는 그 다음
						WHEN TOT.WaitType IN (								-- 일반적인 대기 유형
							'CXPACKET','CXCONSUMER','EXECSYNC'
							, 'WRITELOG'		
							, 'SLEEP_TASK','IO_COMPLETION')		THEN 3
						ELSE 999 END)
					, CollectDate DESC) ROWNUM								-- 정렬 기준을 다르게 했을때 OUTPUT이 다르면 혼란스러우니까 그냥 최근껄로 보여주자.
			, TOT.CollectDate
			, TOT.start_time
			, TOT.session_id
			, TOT.status
			, TOT.sql_text
			, TOT.WaitType
			, TOT.IsolationLevel
			, TOT.database_name
			, TOT.ObjectName
			, TOT.total_elapsed_time
			, TOT.CPU
			, TOT.tempdb_allocations
			, TOT.tempdb_current
			, TOT.used_memory
			, TOT.reads
			, TOT.physical_reads
			, TOT.login_name
			, TOT.open_tran_count
			, TOT.blocking_session_id
			, TOT.host_name
			, TOT.program_name		 
		FROM (
			SELECT
				CollectDate
				, start_time
				, session_id
				, status
				, sql_text
				, RTRIM(SUBSTRING(wait_info, CHARINDEX(')',wait_info) + 1, LEN(wait_info) - CHARINDEX(')',wait_info) - (LEN(wait_info) - CHARINDEX(' ',wait_info)))) AS WaitType
				, CASE transaction_isolation_level
					WHEN 0 THEN 'UNKNOWN'
					WHEN 1 THEN 'RU'	-- Read UnCommitted
					WHEN 2 THEN 'RC'	-- Read committed
					WHEN 3 THEN 'RR'	-- Repeatable Read
					WHEN 4 THEN 'SZ'	-- Serializable
					WHEN 5 THEN 'SN'	-- Snapshot
					END AS IsolationLevel
				, database_name
				, ObjectName
				, total_elapsed_time
				, CPU
				, tempdb_allocations
				, tempdb_current
				, used_memory
				, reads
				, physical_reads
				, login_name
				, open_tran_count
				, blocking_session_id
				, host_name
				, program_name
			FROM MonitoringDB.dbo.TBL2_M_WhoIsActive W 
			WHERE W.InstanceId = @in_InstanceId
			AND W.CollectDate BETWEEN @dateFrom AND @dateTo
			AND W.query_hash = @in_query_hash
		) TOT
	) TOT
	WHERE ROWNUM = 1	
	ORDER BY																-- 정렬 기준으로 정렬
		CASE @in_searchType WHEN 1 THEN total_elapsed_time END DESC
		, CASE @in_searchType WHEN 2 THEN CPU END DESC
		, CASE @in_searchType WHEN 3 THEN reads END DESC
		, CASE @in_searchType WHEN 4 THEN physical_reads END DESC
		, CASE @in_searchType WHEN 5 THEN used_memory END DESC
		, CASE @in_searchType WHEN 6 THEN tempdb_allocations END DESC
		, CollectDate DESC

	SET ROWCOUNT 0
END
