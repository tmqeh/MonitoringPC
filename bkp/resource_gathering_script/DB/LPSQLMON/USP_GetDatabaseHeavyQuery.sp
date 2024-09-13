

/*=============================================
-- Author:			이지수
-- Create date:		2022-11-23
-- Description:		모니터링 DB에서 무거운 쿼리 뽑아내기(실시간)
-- Modify History: 
					2022-11-25	/	이지수	/	대기 유형 뜨는 쿼리 우선으로 보여주되, 중복으로 수집된 결과는 제거
-- Example:	
	EXEC MonitoringDB.dbo.USP_GetDatabaseHeavyQuery
		@in_InstanceId		= 13
		, @in_dateFrom		= ''
		, @in_viewCnt		= 200
	GO
	EXEC MonitoringDB.dbo.USP_GetDatabaseHeavyQuery
		@in_InstanceId		= 13
		, @in_dateFrom		= ''
		, @in_viewCnt		= 200
		, @in_objectName	= 'PR_MSIM_STCKM_GetWholeStckList'
	GO
=============================================*/
CREATE PROCEDURE [dbo].[USP_GetDatabaseHeavyQuery]
	@in_InstanceId		INT						-- 대상 서버는 반드시 설정해야 함
	, @in_dateFrom		VARCHAR(10) = ''
	, @in_viewCnt		SMALLINT = 100
	, @in_objectName	NVARCHAR(128) = ''
AS
BEGIN

	SET NOCOUNT ON
	SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED

	IF ISNULL(@in_dateFrom,'') = ''
		SET @in_dateFrom = CONVERT(VARCHAR(10), GETDATE(), 121)

	IF ISNULL(@in_objectName,'') <> ''
	BEGIN
		SELECT TOP (@in_viewCnt) 
			Gubun
			, TOT.CollectDate
			, start_time
			, session_id
			, status
			, sql_text
			, WaitType
			, IsolationLevel
			, database_name
			, ObjectName
			, total_elapsed_time
			, tempdb_current
			, used_memory
			, reads
			, physical_reads
			, login_name
			, open_tran_count
			, blocking_session_id
			, host_name
			, program_name
	--		, CONVERT(XML,p.query_plan_text) query_plan
		FROM (
			SELECT 
				ROW_NUMBER()OVER(PARTITION BY session_id, start_time ORDER BY (CASE WHEN Gubun = 1 THEN 1 ELSE 999 END), CollectDate DESC) ROWNUM
				, *
			FROM (
				-- 대기 유형이 뜨는 쿼리
				SELECT TOP (@in_viewCnt)
					1 AS Gubun 
					, *
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
						, tempdb_current
						, used_memory
						, reads
						, physical_reads
						, login_name
						, open_tran_count
						, blocking_session_id
						, host_name
						, program_name
						, query_hash
						, query_plan_hash
					FROM MonitoringDB.dbo.TBL2_M_WhoIsActive W 
					WHERE W.CollectDate > @in_dateFrom
					AND W.InstanceId = @in_InstanceId
					AND W.ObjectName = @in_objectName
				) W
				WHERE W.WaitType IN (
					'CXPACKET','CXCONSUMER','EXECSYNC'	-- 병렬처리 관련
					, 'WRITELOG'						-- TRANSACTION 관련(지나치게 잦은 커밋)
					, 'SLEEP_TASK','IO_COMPLETION'		-- TEMPDB 관련(SLEEP_TASK : HASH, IO_COMPLETION : SORT)
					, 'OLEDB' )							-- 연결된 서버 관련(주로 다른 디비 연결하는데 원격지 DB에서 응답이 없어 기다릴때 나타남)	
				OR W.WaitType LIKE 'PAGEIOLATCH%'		-- PAGEIO LATCH(디스크IO 경합 : 메모리->디스크 올려줄때, 인덱스 스캔이나 물리 읽기 많이 발생하면 나타남)
				OR W.WaitType LIKE 'PAGELATCH%'			-- PAGE LATCH(페이지 할당 과정에서의 경합 : 인덱스나 PK에 DML 일어나는 경우..)
				OR W.WaitType LIKE 'LATCH%'				-- LATCH(메모리 경합 : 과도한 병렬처리, 데이터 증가시, 힙/BLOB 데이터에 대한 잦은 DML 등...)
				OR W.WaitType LIKE 'LCK%'				-- LOCK
				ORDER BY CollectDate DESC
				UNION ALL
				-- tempdb 사용량이 높은 쿼리
				SELECT TOP (@in_viewCnt)
					2 AS Gubun 
					, *
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
							WHEN 5 THEN 'SH'	-- Snapshot
							END AS IsolationLevel
						, database_name
						, ObjectName
						, total_elapsed_time
						, tempdb_current
						, used_memory
						, reads
						, physical_reads
						, login_name
						, open_tran_count
						, blocking_session_id
						, host_name
						, program_name
						, query_hash
						, query_plan_hash
					FROM MonitoringDB.dbo.TBL2_M_WhoIsActive W 
					WHERE W.CollectDate > @in_dateFrom
					AND W.InstanceId = @in_InstanceId
					AND W.ObjectName = @in_objectName
					AND (W.tempdb_allocations > 100 OR W.used_memory > 100)
				) W
				WHERE W.WaitType NOT IN ('WAITFOR','ASYNC_IO_COMPLETION','BACKUPIO','ASYNC_NETWORK_IO')		-- 의도적인 대기, 네트워크 관련, 백업 관련 대기는 제외
				ORDER BY CollectDate DESC
				UNION ALL
				-- Physical Read 발생 쿼리
				SELECT TOP (@in_viewCnt)
					3 AS Gubun 
					, *
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
							WHEN 5 THEN 'SH'	-- Snapshot
							END AS IsolationLevel
						, database_name
						, ObjectName
						, total_elapsed_time
						, tempdb_current
						, used_memory
						, reads
						, physical_reads
						, login_name
						, open_tran_count
						, blocking_session_id
						, host_name
						, program_name
						, query_hash
						, query_plan_hash
					FROM MonitoringDB.dbo.TBL2_M_WhoIsActive W 
					WHERE W.CollectDate > @in_dateFrom
					AND W.InstanceId = @in_InstanceId
					AND W.ObjectName = @in_objectName
					AND W.physical_reads > 0	
				) W
				WHERE W.WaitType NOT IN ('WAITFOR','ASYNC_IO_COMPLETION','BACKUPIO','ASYNC_NETWORK_IO')		-- 의도적인 대기, 네트워크 관련, 백업 관련 대기는 제외
				ORDER BY CollectDate DESC
				UNION ALL 
				-- Logical Read 높은 쿼리
				SELECT TOP (@in_viewCnt)
					4 AS Gubun 
					, *
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
							WHEN 5 THEN 'SH'	-- Snapshot
							END AS IsolationLevel
						, database_name
						, ObjectName
						, total_elapsed_time
						, tempdb_current
						, used_memory
						, reads
						, physical_reads
						, login_name
						, open_tran_count
						, blocking_session_id
						, host_name
						, program_name
						, query_hash
						, query_plan_hash
					FROM MonitoringDB.dbo.TBL2_M_WhoIsActive W 
					WHERE W.CollectDate > @in_dateFrom
					AND W.InstanceId = @in_InstanceId
					AND W.ObjectName = @in_objectName
					AND W.reads > 1000	
				) W
				WHERE W.WaitType NOT IN ('WAITFOR','ASYNC_IO_COMPLETION','BACKUPIO','ASYNC_NETWORK_IO')		-- 의도적인 대기, 네트워크 관련, 백업 관련 대기는 제외
				ORDER BY CollectDate DESC
			) TOT		
		) TOT
		LEFT JOIN dbo.TBL2_M_Queryplan p ON p.InstanceID = @in_InstanceId AND p.query_hash = TOT.query_hash AND p.query_plan_hash = TOT.query_plan_hash
		WHERE TOT.ROWNUM = 1
		ORDER BY TOT.CollectDate DESC
		OPTION(CONCAT UNION)
	END
	ELSE
	BEGIN
		SELECT TOP (@in_viewCnt) 
			Gubun
			, TOT.CollectDate
			, start_time
			, session_id
			, status
			, sql_text
			, WaitType
			, IsolationLevel
			, database_name
			, ObjectName
			, total_elapsed_time
			, tempdb_current
			, used_memory
			, reads
			, physical_reads
			, login_name
			, open_tran_count
			, blocking_session_id
			, host_name
			, program_name
	--		, CONVERT(XML,p.query_plan_text) query_plan
		FROM (
			SELECT 
				ROW_NUMBER()OVER(PARTITION BY session_id, start_time ORDER BY CollectDate DESC) ROWNUM
				, *
			FROM (
				-- 대기 유형이 뜨는 쿼리
				SELECT TOP (@in_viewCnt)
					1 AS Gubun 
					, *
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
						, tempdb_current
						, used_memory
						, reads
						, physical_reads
						, login_name
						, open_tran_count
						, blocking_session_id
						, host_name
						, program_name
						, query_hash
						, query_plan_hash
					FROM MonitoringDB.dbo.TBL2_M_WhoIsActive W 
					WHERE W.CollectDate > @in_dateFrom
					AND W.InstanceId = @in_InstanceId
				) W
				WHERE W.WaitType IN (
					'CXPACKET','CXCONSUMER','EXECSYNC'	-- 병렬처리 관련
					, 'WRITELOG'						-- TRANSACTION 관련(지나치게 잦은 커밋)
					, 'SLEEP_TASK','IO_COMPLETION'		-- TEMPDB 관련(SLEEP_TASK : HASH, IO_COMPLETION : SORT)
					, 'OLEDB' )							-- 연결된 서버 관련(주로 다른 디비 연결하는데 원격지 DB에서 응답이 없어 기다릴때 나타남)	
				OR W.WaitType LIKE 'PAGEIOLATCH%'		-- PAGEIO LATCH(디스크IO 경합 : 메모리->디스크 올려줄때, 인덱스 스캔이나 물리 읽기 많이 발생하면 나타남)
				OR W.WaitType LIKE 'PAGELATCH%'			-- PAGE LATCH(페이지 할당 과정에서의 경합 : 인덱스나 PK에 DML 일어나는 경우..)
				OR W.WaitType LIKE 'LATCH%'				-- LATCH(메모리 경합 : 과도한 병렬처리, 데이터 증가시, 힙/BLOB 데이터에 대한 잦은 DML 등...)
				OR W.WaitType LIKE 'LCK%'				-- LOCK
				ORDER BY CollectDate DESC
				UNION ALL
				-- tempdb 사용량이 높은 쿼리
				SELECT TOP (@in_viewCnt)
					2 AS Gubun 
					, *
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
							WHEN 5 THEN 'SH'	-- Snapshot
							END AS IsolationLevel
						, database_name
						, ObjectName
						, total_elapsed_time
						, tempdb_current
						, used_memory
						, reads
						, physical_reads
						, login_name
						, open_tran_count
						, blocking_session_id
						, host_name
						, program_name
						, query_hash
						, query_plan_hash
					FROM MonitoringDB.dbo.TBL2_M_WhoIsActive W 
					WHERE W.CollectDate > @in_dateFrom
					AND W.InstanceId = @in_InstanceId
					AND (W.tempdb_allocations > 100 OR W.used_memory > 100)
				) W
				WHERE W.WaitType NOT IN ('WAITFOR','ASYNC_IO_COMPLETION','BACKUPIO','ASYNC_NETWORK_IO')		-- 의도적인 대기, 네트워크 관련, 백업 관련 대기는 제외
				ORDER BY CollectDate DESC
				UNION ALL
				-- Physical Read 발생 쿼리
				SELECT TOP (@in_viewCnt)
					3 AS Gubun 
					, *
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
							WHEN 5 THEN 'SH'	-- Snapshot
							END AS IsolationLevel
						, database_name
						, ObjectName
						, total_elapsed_time
						, tempdb_current
						, used_memory
						, reads
						, physical_reads
						, login_name
						, open_tran_count
						, blocking_session_id
						, host_name
						, program_name
						, query_hash
						, query_plan_hash
					FROM MonitoringDB.dbo.TBL2_M_WhoIsActive W 
					WHERE W.CollectDate > @in_dateFrom
					AND W.InstanceId = @in_InstanceId
					AND W.physical_reads > 0	
				) W
				WHERE W.WaitType NOT IN ('WAITFOR','ASYNC_IO_COMPLETION','BACKUPIO','ASYNC_NETWORK_IO')		-- 의도적인 대기, 네트워크 관련, 백업 관련 대기는 제외
				ORDER BY CollectDate DESC
				UNION ALL 
				-- Logical Read 높은 쿼리
				SELECT TOP (@in_viewCnt)
					4 AS Gubun 
					, *
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
							WHEN 5 THEN 'SH'	-- Snapshot
							END AS IsolationLevel
						, database_name
						, ObjectName
						, total_elapsed_time
						, tempdb_current
						, used_memory
						, reads
						, physical_reads
						, login_name
						, open_tran_count
						, blocking_session_id
						, host_name
						, program_name
						, query_hash
						, query_plan_hash
					FROM MonitoringDB.dbo.TBL2_M_WhoIsActive W 
					WHERE W.CollectDate > @in_dateFrom
					AND W.InstanceId = @in_InstanceId
					AND W.reads > 1000	
				) W
				WHERE W.WaitType NOT IN ('WAITFOR','ASYNC_IO_COMPLETION','BACKUPIO','ASYNC_NETWORK_IO')		-- 의도적인 대기, 네트워크 관련, 백업 관련 대기는 제외
				ORDER BY CollectDate DESC
			) TOT		
		) TOT
		LEFT JOIN dbo.TBL2_M_Queryplan p ON p.InstanceID = @in_InstanceId AND p.query_hash = TOT.query_hash AND p.query_plan_hash = TOT.query_plan_hash
		WHERE TOT.ROWNUM = 1
		ORDER BY TOT.CollectDate DESC
		OPTION(CONCAT UNION)
	END

END
