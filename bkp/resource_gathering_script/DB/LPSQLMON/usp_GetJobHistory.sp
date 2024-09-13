/*=============================================
-- Author:			이지수
-- Create date:		2022-09-20
-- Description:		JOB 실행 이력 확인
-- Modify History:	
-- Example:	
	EXEC MonitoringDB.dbo.usp_GetJobHistory
	GO
	EXEC MonitoringDB.dbo.usp_GetJobHistory @in_job_name = '[DBA]Reorganize indexes_1'
	GO
	EXEC MonitoringDB.dbo.usp_GetJobHistory @in_job_name = '[DBA]Reorganize indexes_1', @in_step = 3
	GO
=============================================*/
create PROCEDURE dbo.usp_GetJobHistory 
	@in_job_name	VARCHAR(500) = ''
	, @in_step		INT = 0
AS
BEGIN

	SET NOCOUNT ON
	SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED

	IF ISNULL(@in_job_name,'') = ''
	BEGIN
		SELECT
			job_id 
			, job_name
			, step
			, subplan_name
			, backup_gubun
			, freq_interval
			, freq_subday_type
			, date_created
			, last_run_date
			, ISNULL(last_run_status,'-') AS last_run_status
			, CASE WHEN last_run_status IS NOT NULL THEN last_run_duration ELSE '-' END AS last_run_duration
			, CASE WHEN last_run_status IS NOT NULL THEN avg_run_duration END AS avg_run_duration
			, ISNULL(CONVERT(VARCHAR,DATEDIFF(MINUTE, avg_run_duration, last_run_duration)*60),'-') AS run_duration_diff
		FROM (
			SELECT
				job_id  
				, job_name
				, step
				, subplan_name
				, backup_gubun
				, freq_interval
				, CASE freq_subday_type
					WHEN 1 THEN '지정 시각(' + SUBSTRING(active_start_time,1,2) +':'+ SUBSTRING(active_start_time,3,2) +':'+ SUBSTRING(active_start_time,5,2) + ')'
					WHEN 2 THEN CONVERT(VARCHAR(2),freq_subday_interval) + '초 마다'
					WHEN 4 THEN CONVERT(VARCHAR(2),freq_subday_interval) + '분 마다'
					WHEN 8 THEN CONVERT(VARCHAR(2),freq_subday_interval) + '시 마다' END freq_subday_type
				, date_created
				, last_run_date + ' ' + SUBSTRING(last_run_time,1,2) + ':' + SUBSTRING(last_run_time, 3,2) + ':' + SUBSTRING(last_run_time, 5,2) AS last_run_date
				, last_run_status
				, SUBSTRING(last_run_duration,1,2) +':'+ SUBSTRING(last_run_duration,3,2) +':'+ SUBSTRING(last_run_duration,5,2) AS last_run_duration
				, avg_run_hour + ':' + avg_run_min + ':' + avg_run_sec AS avg_run_duration
			FROM (
				SELECT
					j.job_id 
					, j.name AS job_name
					, ISNULL(t.step_id,0) AS step
					, ISNULL(s.subplan_name, t.step_name) AS subplan_name
					, RIGHT('000000' + CONVERT(VARCHAR(6),d.active_start_time),6) AS active_start_time
					, RIGHT('000000' + CONVERT(VARCHAR(6),d.active_end_time),6) AS active_end_time
					, CASE d.freq_type
						WHEN 1 
							THEN '한 번'
						WHEN 4		
							THEN CONVERT(VARCHAR(2),freq_interval) + '일 마다'				-- 일 주기
						WHEN 8		
							THEN '매주 '
								+ STUFF(IIF (d.freq_interval & 1 = 1,', 일','')				-- 일요일(2의0승)
									+ IIF (d.freq_interval & 2 = 2,', 월','')				-- 월요일(2의1승)
									+ IIF (d.freq_interval & 4 = 4,', 화','')				-- 화요일(2의2승)
									+ IIF (d.freq_interval & 8 = 8,', 수','')				-- 수요일(2의3승)
									+ IIF (d.freq_interval & 16 = 16,', 목','')				-- 목요일(2의4승)
									+ IIF (d.freq_interval & 32 = 32,', 금','')				-- 금요일(2의5승)
									+ IIF (d.freq_interval & 64 = 64,', 토',''),1,2,'') 	-- 토요일(2의6승) 이므로 비트연산하면 해당 값이 나옴(이진법 생각하면 쉬움) 이렇게까지해야하나...ㅎㅎㅎ
						WHEN 16
							THEN '매월 ' + CONVERT(VARCHAR(2),freq_interval) + '일' 
						WHEN 32
							THEN '매월 ' 
								+ CASE d.freq_relative_interval
									WHEN 1	THEN '첫번째'
									WHEN 2	THEN '두번째'
									WHEN 4	THEN '세번째'
									WHEN 8	THEN '네번째'
									WHEN 16 THEN '마지막' 
									ELSE '' END 
								+ CASE d.freq_interval 
									WHEN 1	THEN '일요일'
									WHEN 2	THEN '월요일'
									WHEN 3	THEN '화요일'
									WHEN 4	THEN '수요일'
									WHEN 5	THEN '목요일'
									WHEN 6	THEN '금요일'
									WHEN 7	THEN '토요일'
									WHEN 8	THEN '일'
									WHEN 9	THEN '평일'
									WHEN 10 THEN '주말' END
						WHEN 64
							THEN 'SQL Server 에이전트 서비스가 시작될 때 실행'
						WHEN 128 
							THEN '컴퓨터가 유휴 상태일 때 실행' 
						ELSE '사용되지 않음' END AS freq_interval
					, d.freq_subday_type
					, d.freq_subday_interval
					, j.date_created
					, CASE t.last_run_outcome
						WHEN 0 THEN '실패'
						WHEN 1 THEN '성공'
						WHEN 2 THEN '다시 시도'
						WHEN 3 THEN '취소됨'
						WHEN 5 THEN '알 수 없음' END AS last_run_status
					, CONVERT(VARCHAR(10),CONVERT(DATE,CONVERT(VARCHAR(8),t.last_run_date))) AS last_run_date
					, RIGHT('000000' + CONVERT(VARCHAR(6),t.last_run_time), 6) AS last_run_time
					, RIGHT('000000' + CONVERT(VARCHAR(6),t.last_run_duration), 6) AS last_run_duration
					, CASE WHEN s.job_id IS NOT NULL THEN '유지관리계획' ELSE 'JOB' END AS backup_gubun
					, RIGHT('00' + CONVERT(VARCHAR(2),IIF(ha.avg_run_duration/3600 > 0, ha.avg_run_duration/3600,0)),2) AS avg_run_hour
					, RIGHT('00' + CONVERT(VARCHAR(2),IIF((ha.avg_run_duration%3600) / 60 > 0, (ha.avg_run_duration%3600) / 60,0)),2) AS avg_run_min
					, RIGHT('00' + CONVERT(VARCHAR(2),IIF((ha.avg_run_duration%3600) / 60 > 0, (ha.avg_run_duration%3600) / 60,0)),2) AS avg_run_sec					
				FROM msdb.dbo.sysjobs j		
				INNER JOIN msdb.dbo.sysjobschedules c ON j.job_id = c.job_id
				INNER JOIN msdb.dbo.sysschedules d ON c.schedule_id = d.schedule_id		
				LEFT JOIN msdb.dbo.sysjobsteps t ON j.job_id = t.job_id
				LEFT JOIN msdb.dbo.sysmaintplan_subplans s ON j.job_id = s.job_id
				OUTER APPLY (
					SELECT 
						AVG(CONVERT(INT,SUBSTRING(run_duration,1,2)) * 3600
							+ CONVERT(INT,SUBSTRING(run_duration,3,2)) * 60
							+ CONVERT(INT,SUBSTRING(run_duration,5,2))) AS avg_run_duration
					FROM (
						SELECT TOP 10 
							RIGHT('000000' + CONVERT(VARCHAR(6),run_duration),6) AS run_duration
						FROM msdb.dbo.sysjobhistory h 
						WHERE 1=1
						AND j.job_id = h.job_id
						AND h.step_id = 0
						ORDER BY run_date DESC, run_time DESC
					) HA
				) ha
				WHERE j.enabled = 1				-- 현재 사용하고 있는 JOB만 보여주도록
			) TOT
		) TOT
		ORDER BY job_id, step
		OPTION(MAXDOP 1)
	END
	ELSE 
	BEGIN

		DECLARE @job_id UNIQUEIDENTIFIER 

		SELECT @job_id = job_id
		FROM msdb.dbo.sysjobs
		WHERE name = @in_job_name

		IF @@ROWCOUNT = 0
			PRINT '존재하지 않는 Job'

		-- JOB 단위
		SELECT
			job_name
			, CASE WHEN [enabled] = 1 THEN 'Y' ELSE 'N' END is_enabled
			, date_created			
			, total_step
			, start_step_id
			, backup_gubun
			, ISNULL(last_run_date,'-') AS whole_last_run_date
			, ISNULL(last_run_status,'-') AS whole_last_run_status
			, CASE WHEN last_run_status IS NOT NULL THEN last_run_duration ELSE '-' END AS whole_last_run_duration
			, CASE WHEN last_run_status IS NOT NULL THEN avg_run_duration END AS whole_avg_run_duration
			, ISNULL(CONVERT(VARCHAR,DATEDIFF(MINUTE, avg_run_duration, last_run_duration)*60),'-') AS whole_run_duration_diff
		FROM (
			SELECT
				job_name
				, enabled
				, date_created
				, step AS total_step
				, start_step_id
				, backup_gubun
				, last_run_date
				, last_run_status
				, SUBSTRING(last_run_duration,1,2) +':'+ SUBSTRING(last_run_duration,3,2) +':'+ SUBSTRING(last_run_duration,5,2) AS last_run_duration
				, avg_run_hour + ':' + avg_run_min + ':' + avg_run_sec AS avg_run_duration
			FROM (
				SELECT
					j.job_id 
					, j.name AS job_name
					, j.enabled
					, j.date_created
					, ISNULL(t.step_id,0) AS step
					, j.start_step_id
					, RIGHT('000000' + CONVERT(VARCHAR(6),d.active_start_time),6) AS active_start_time
					, RIGHT('000000' + CONVERT(VARCHAR(6),d.active_end_time),6) AS active_end_time
					, CASE h.run_status 
						WHEN 0 THEN '실패'
						WHEN 1 THEN '성공'
						WHEN 2 THEN '다시 시도'
						WHEN 3 THEN '취소됨'
						WHEN 4 THEN '진행 중' END AS last_run_status
					, h.run_date + ' ' + SUBSTRING(h.run_time,1,2) + ':' + SUBSTRING(h.run_time, 3,2) + ':' + SUBSTRING(h.run_time, 5,2) AS last_run_date
					, RIGHT('000000' + CONVERT(VARCHAR(6),h.run_duration), 6) AS last_run_duration
					, CASE WHEN s.job_id IS NOT NULL THEN '유지관리계획' ELSE 'JOB' END AS backup_gubun
					, RIGHT('00' + CONVERT(VARCHAR(2),IIF(ha.avg_run_duration/3600 > 0, ha.avg_run_duration/3600,0)),2) AS avg_run_hour
					, RIGHT('00' + CONVERT(VARCHAR(2),IIF((ha.avg_run_duration%3600) / 60 > 0, (ha.avg_run_duration%3600) / 60,0)),2) AS avg_run_min
					, RIGHT('00' + CONVERT(VARCHAR(2),IIF((ha.avg_run_duration%3600) / 60 > 0, (ha.avg_run_duration%3600) / 60,0)),2) AS avg_run_sec
				FROM msdb.dbo.sysjobs j		
				INNER JOIN msdb.dbo.sysjobschedules c ON j.job_id = c.job_id
				INNER JOIN msdb.dbo.sysschedules d ON c.schedule_id = d.schedule_id	
				OUTER APPLY (
					SELECT TOP 1 t.step_id
					FROM msdb.dbo.sysjobsteps t 
					WHERE j.job_id = t.job_id
					ORDER BY t.step_id DESC
				) t
				LEFT JOIN msdb.dbo.sysmaintplan_subplans s ON j.job_id = s.job_id
				OUTER APPLY (
					SELECT TOP 1 
						run_status
						, run_duration
						, CONVERT(VARCHAR(10), CONVERT(DATE,CONVERT(VARCHAR(8),run_date))) AS run_date
						, RIGHT('000000'+ CONVERT(VARCHAR(6),run_time),6) AS run_time
					FROM msdb.dbo.sysjobhistory h 
					WHERE j.job_id = h.job_id
					AND h.step_id = 0
					ORDER BY run_date DESC, run_time DESC
				) h
				OUTER APPLY (
					SELECT 
						AVG(CONVERT(INT,SUBSTRING(run_duration,1,2)) * 3600
							+ CONVERT(INT,SUBSTRING(run_duration,3,2)) * 60
							+ CONVERT(INT,SUBSTRING(run_duration,5,2))) AS avg_run_duration
					FROM (
						SELECT TOP 10 
							RIGHT('000000' + CONVERT(VARCHAR(6),run_duration),6) AS run_duration
						FROM msdb.dbo.sysjobhistory h 
						WHERE 1=1
						AND j.job_id = h.job_id
						AND h.step_id = 0
						ORDER BY run_date DESC, run_time DESC
					) HA
				) ha
				WHERE j.job_id = @job_id
			) TOT
		) TOT
		OPTION(MAXDOP 1)

		IF @in_step = 0
		BEGIN
			-- Step 단위
			SELECT
				step
				, subplan_name
				, subsystem
				, freq_interval
				, freq_subday_type
				, ISNULL(last_run_date,'-') AS last_run_date
				, ISNULL(last_run_status,'-') AS last_run_status
				, CASE WHEN last_run_status IS NOT NULL THEN last_run_duration ELSE '-' END AS last_run_duration
				, CASE WHEN last_run_status IS NOT NULL THEN avg_run_duration END AS avg_run_duration
				, ISNULL(CONVERT(VARCHAR,DATEDIFF(MINUTE, avg_run_duration, last_run_duration)*60),'-') AS run_duration_diff
				, date_created
				, database_name
				, on_success_action
				, on_fail_action
				, command
			FROM (
				SELECT
					step
					, subplan_name
					, subsystem
					, freq_interval
					, CASE freq_subday_type
						WHEN 1 THEN '지정 시각(' + SUBSTRING(active_start_time,1,2) +':'+ SUBSTRING(active_start_time,3,2) +':'+ SUBSTRING(active_start_time,5,2) + ')'
						WHEN 2 THEN CONVERT(VARCHAR(2),freq_subday_interval) + '초 마다'
						WHEN 4 THEN CONVERT(VARCHAR(2),freq_subday_interval) + '분 마다'
						WHEN 8 THEN CONVERT(VARCHAR(2),freq_subday_interval) + '시 마다' END freq_subday_type
					, date_created
					, last_run_date + ' ' + SUBSTRING(last_run_time,1,2) + ':' + SUBSTRING(last_run_time, 3,2) + ':' + SUBSTRING(last_run_time, 5,2) AS last_run_date
					, last_run_status
					, SUBSTRING(last_run_duration,1,2) +':'+ SUBSTRING(last_run_duration,3,2) +':'+ SUBSTRING(last_run_duration,5,2) AS last_run_duration
					, avg_run_hour + ':' + avg_run_min + ':' + avg_run_sec AS avg_run_duration
					, command
					, database_name
					, on_success_action
					, on_fail_action
				FROM (
					SELECT
						ISNULL(t.step_id,0) AS step
						, ISNULL(s.subplan_name, t.step_name) AS subplan_name
						, RIGHT('000000' + CONVERT(VARCHAR(6),d.active_start_time),6) AS active_start_time
						, RIGHT('000000' + CONVERT(VARCHAR(6),d.active_end_time),6) AS active_end_time
						, CASE d.freq_type
							WHEN 1 
								THEN '한 번'
							WHEN 4		
								THEN CONVERT(VARCHAR(2),freq_interval) + '일 마다'				-- 일 주기
							WHEN 8		
								THEN '매주 '
									+ STUFF(IIF (d.freq_interval & 1 = 1,', 일','')				-- 일요일
										+ IIF (d.freq_interval & 2 = 2,', 월','')				-- 월요일
										+ IIF (d.freq_interval & 4 = 4,', 화','')				-- 화요일
										+ IIF (d.freq_interval & 8 = 8,', 수','')				-- 수요일
										+ IIF (d.freq_interval & 16 = 16,', 목','')				-- 목요일
										+ IIF (d.freq_interval & 32 = 32,', 금','')				-- 금요일
										+ IIF (d.freq_interval & 64 = 64,', 토',''),1,2,'') 	-- 토요일
							WHEN 16
								THEN '매월 ' + CONVERT(VARCHAR(2),freq_interval) + '일' 
							WHEN 32
								THEN '매월 ' 
									+ CASE d.freq_relative_interval
										WHEN 1	THEN '첫번째'
										WHEN 2	THEN '두번째'
										WHEN 4	THEN '세번째'
										WHEN 8	THEN '네번째'
										WHEN 16 THEN '마지막' 
										ELSE '' END 
									+ CASE d.freq_interval 
										WHEN 1	THEN '일요일'
										WHEN 2	THEN '월요일'
										WHEN 3	THEN '화요일'
										WHEN 4	THEN '수요일'
										WHEN 5	THEN '목요일'
										WHEN 6	THEN '금요일'
										WHEN 7	THEN '토요일'
										WHEN 8	THEN '일'
										WHEN 9	THEN '평일'
										WHEN 10 THEN '주말' END
							WHEN 64
								THEN 'SQL Server 에이전트 서비스가 시작될 때 실행'
							WHEN 128 
								THEN '컴퓨터가 유휴 상태일 때 실행' 
							ELSE '사용되지 않음' END AS freq_interval
						, d.freq_subday_type
						, d.freq_subday_interval
						, d.date_created
						, CASE t.last_run_outcome
							WHEN 0 THEN '실패'
							WHEN 1 THEN '성공'
							WHEN 2 THEN '다시 시도'
							WHEN 3 THEN '취소됨'
							WHEN 5 THEN '알 수 없음' END AS last_run_status
						, CONVERT(VARCHAR(10),CONVERT(DATE,CONVERT(VARCHAR(8),t.last_run_date))) AS last_run_date
						, RIGHT('000000' + CONVERT(VARCHAR(6),t.last_run_time), 6) AS last_run_time
						, RIGHT('000000' + CONVERT(VARCHAR(6),t.last_run_duration), 6) AS last_run_duration
						, RIGHT('00' + CONVERT(VARCHAR(2),IIF(ha.avg_run_duration/3600 > 0, ha.avg_run_duration/3600,0)),2) AS avg_run_hour
						, RIGHT('00' + CONVERT(VARCHAR(2),IIF((ha.avg_run_duration%3600) / 60 > 0, (ha.avg_run_duration%3600) / 60,0)),2) AS avg_run_min
						, RIGHT('00' + CONVERT(VARCHAR(2),IIF((ha.avg_run_duration%3600) / 60 > 0, (ha.avg_run_duration%3600) / 60,0)),2) AS avg_run_sec
						, t.subsystem
						, t.command
						, t.database_name
						, CASE t.on_success_action 
							WHEN 1 THEN '성공으로 종료'
							WHEN 2 THEN '(기본값) 실패로 종료'
							WHEN 3 THEN '다음 단계로 이동'
							WHEN 4 THEN CONVERT(VARCHAR(1), on_fail_step_id) + '단계로 이동' END AS on_success_action
						, CASE t.on_fail_action 
							WHEN 1 THEN '성공으로 종료'
							WHEN 2 THEN '(기본값) 실패로 종료'
							WHEN 3 THEN '다음 단계로 이동'
							WHEN 4 THEN CONVERT(VARCHAR(1), on_fail_step_id) + '단계로 이동' END AS on_fail_action
						, t.retry_attempts
						, t.retry_interval
					FROM msdb.dbo.sysjobs j		
					INNER JOIN msdb.dbo.sysjobschedules c ON j.job_id = c.job_id
					INNER JOIN msdb.dbo.sysschedules d ON c.schedule_id = d.schedule_id		
					LEFT JOIN msdb.dbo.sysjobsteps t ON j.job_id = t.job_id
					LEFT JOIN msdb.dbo.sysmaintplan_subplans s ON j.job_id = s.job_id
					OUTER APPLY (
						SELECT 
							AVG(CONVERT(INT,SUBSTRING(run_duration,1,2)) * 3600
								+ CONVERT(INT,SUBSTRING(run_duration,3,2)) * 60
								+ CONVERT(INT,SUBSTRING(run_duration,5,2))) AS avg_run_duration
						FROM (
							SELECT TOP 10 
								RIGHT('000000' + CONVERT(VARCHAR(6),run_duration),6) AS run_duration
							FROM msdb.dbo.sysjobhistory h 
							WHERE 1=1
							AND h.job_id = t.job_id
							AND h.step_id = t.step_id
							ORDER BY run_date DESC, run_time DESC
						) ha
					) ha
					WHERE j.job_id = @job_id
				) TOT
			) TOT
			ORDER BY step
			OPTION(MAXDOP 1)

			-- History
			SELECT
				run_date + ' ' + SUBSTRING(run_time,1,2) + ':' + SUBSTRING(run_time,3,2) + ':' + SUBSTRING(run_time,5,2) AS run_date			 
				, step_id
				, step_name				
				, run_status
				, h.message
				, h.server
				, SUBSTRING(run_duration,1,2) + ':' + SUBSTRING(run_duration,3,2) + ':' + SUBSTRING(run_duration,5,2) AS run_duration
			FROM (
				SELECT 
					t.step_id
					, t.step_name				
					, CASE h.run_status
						WHEN 0 THEN '실패'
						WHEN 1 THEN '성공'
						WHEN 2 THEN '다시 시도'
						WHEN 3 THEN '취소됨' 
						WHEN 4 THEN '진행 중' END AS run_status
					, CONVERT(VARCHAR(10),CONVERT(DATE,CONVERT(VARCHAR(8),h.run_date)),121) AS run_date
					, RIGHT('000000' + CONVERT(VARCHAR(6),h.run_time), 6) AS run_time
					, RIGHT('000000' + CONVERT(VARCHAR(6),run_duration), 6) run_duration	
					, h.message
					, h.server
				FROM msdb.dbo.sysjobsteps t
				INNER JOIN msdb.dbo.sysjobhistory h ON t.job_id = h.job_id AND t.step_id = h.step_id
				WHERE t.job_id = @job_id
				AND h.run_date > CONVERT(VARCHAR(8), DATEADD(DAY, -10, GETDATE()),112)
			) h
			ORDER BY h.run_date DESC, h.run_time DESC, h.step_id

		END
		ELSE
		BEGIN
			-- Step 단위
			SELECT
				step
				, subplan_name
				, subsystem
				, freq_interval
				, freq_subday_type
				, ISNULL(last_run_date,'-') AS last_run_date
				, ISNULL(last_run_status,'-') AS last_run_status
				, CASE WHEN last_run_status IS NOT NULL THEN last_run_duration ELSE '-' END AS last_run_duration
				, CASE WHEN last_run_status IS NOT NULL THEN avg_run_duration END AS avg_run_duration
				, ISNULL(CONVERT(VARCHAR,DATEDIFF(MINUTE, avg_run_duration, last_run_duration)*60),'-') AS run_duration_diff
				, date_created
				, database_name
				, on_success_action
				, on_fail_action
				, command
			FROM (
				SELECT
					step
					, subplan_name
					, subsystem
					, freq_interval
					, CASE freq_subday_type
						WHEN 1 THEN '지정 시각(' + SUBSTRING(active_start_time,1,2) +':'+ SUBSTRING(active_start_time,3,2) +':'+ SUBSTRING(active_start_time,5,2) + ')'
						WHEN 2 THEN CONVERT(VARCHAR(2),freq_subday_interval) + '초 마다'
						WHEN 4 THEN CONVERT(VARCHAR(2),freq_subday_interval) + '분 마다'
						WHEN 8 THEN CONVERT(VARCHAR(2),freq_subday_interval) + '시 마다' END freq_subday_type
					, date_created
					, last_run_date + ' ' + SUBSTRING(last_run_time,1,2) + ':' + SUBSTRING(last_run_time, 3,2) + ':' + SUBSTRING(last_run_time, 5,2) AS last_run_date
					, last_run_status
					, SUBSTRING(last_run_duration,1,2) +':'+ SUBSTRING(last_run_duration,3,2) +':'+ SUBSTRING(last_run_duration,5,2) AS last_run_duration
					, avg_run_hour + ':' + avg_run_min + ':' + avg_run_sec AS avg_run_duration
					, command
					, database_name
					, on_success_action
					, on_fail_action
				FROM (
					SELECT
						ISNULL(t.step_id,0) AS step
						, ISNULL(s.subplan_name, t.step_name) AS subplan_name
						, RIGHT('000000' + CONVERT(VARCHAR(6),d.active_start_time),6) AS active_start_time
						, RIGHT('000000' + CONVERT(VARCHAR(6),d.active_end_time),6) AS active_end_time
						, CASE d.freq_type
							WHEN 1 
								THEN '한 번'
							WHEN 4		
								THEN CONVERT(VARCHAR(2),freq_interval) + '일 마다'				-- 일 주기
							WHEN 8		
								THEN '매주 '
									+ STUFF(IIF (d.freq_interval & 1 = 1,', 일','')				-- 일요일
										+ IIF (d.freq_interval & 2 = 2,', 월','')				-- 월요일
										+ IIF (d.freq_interval & 4 = 4,', 화','')				-- 화요일
										+ IIF (d.freq_interval & 8 = 8,', 수','')				-- 수요일
										+ IIF (d.freq_interval & 16 = 16,', 목','')				-- 목요일
										+ IIF (d.freq_interval & 32 = 32,', 금','')				-- 금요일
										+ IIF (d.freq_interval & 64 = 64,', 토',''),1,2,'') 	-- 토요일
							WHEN 16
								THEN '매월 ' + CONVERT(VARCHAR(2),freq_interval) + '일' 
							WHEN 32
								THEN '매월 ' 
									+ CASE d.freq_relative_interval
										WHEN 1	THEN '첫번째'
										WHEN 2	THEN '두번째'
										WHEN 4	THEN '세번째'
										WHEN 8	THEN '네번째'
										WHEN 16 THEN '마지막' 
										ELSE '' END 
									+ CASE d.freq_interval 
										WHEN 1	THEN '일요일'
										WHEN 2	THEN '월요일'
										WHEN 3	THEN '화요일'
										WHEN 4	THEN '수요일'
										WHEN 5	THEN '목요일'
										WHEN 6	THEN '금요일'
										WHEN 7	THEN '토요일'
										WHEN 8	THEN '일'
										WHEN 9	THEN '평일'
										WHEN 10 THEN '주말' END
							WHEN 64
								THEN 'SQL Server 에이전트 서비스가 시작될 때 실행'
							WHEN 128 
								THEN '컴퓨터가 유휴 상태일 때 실행' 
							ELSE '사용되지 않음' END AS freq_interval
						, d.freq_subday_type
						, d.freq_subday_interval
						, d.date_created
						, CASE t.last_run_outcome
							WHEN 0 THEN '실패'
							WHEN 1 THEN '성공'
							WHEN 2 THEN '다시 시도'
							WHEN 3 THEN '취소됨'
							WHEN 5 THEN '알 수 없음' END AS last_run_status
						, CONVERT(VARCHAR(10),CONVERT(DATE,CONVERT(VARCHAR(8),t.last_run_date))) AS last_run_date
						, RIGHT('000000' + CONVERT(VARCHAR(6),t.last_run_time), 6) AS last_run_time
						, RIGHT('000000' + CONVERT(VARCHAR(6),t.last_run_duration), 6) AS last_run_duration
						, RIGHT('00' + CONVERT(VARCHAR(2),IIF(ha.avg_run_duration/3600 > 0, ha.avg_run_duration/3600,0)),2) AS avg_run_hour
						, RIGHT('00' + CONVERT(VARCHAR(2),IIF((ha.avg_run_duration%3600) / 60 > 0, (ha.avg_run_duration%3600) / 60,0)),2) AS avg_run_min
						, RIGHT('00' + CONVERT(VARCHAR(2),IIF((ha.avg_run_duration%3600) / 60 > 0, (ha.avg_run_duration%3600) / 60,0)),2) AS avg_run_sec
						, t.subsystem
						, t.command
						, t.database_name
						, CASE t.on_success_action 
							WHEN 1 THEN '성공으로 종료'
							WHEN 2 THEN '(기본값) 실패로 종료'
							WHEN 3 THEN '다음 단계로 이동'
							WHEN 4 THEN CONVERT(VARCHAR(1), on_fail_step_id) + '단계로 이동' END AS on_success_action
						, CASE t.on_fail_action 
							WHEN 1 THEN '성공으로 종료'
							WHEN 2 THEN '(기본값) 실패로 종료'
							WHEN 3 THEN '다음 단계로 이동'
							WHEN 4 THEN CONVERT(VARCHAR(1), on_fail_step_id) + '단계로 이동' END AS on_fail_action
						, t.retry_attempts
						, t.retry_interval
					FROM msdb.dbo.sysjobs j		
					INNER JOIN msdb.dbo.sysjobschedules c ON j.job_id = c.job_id
					INNER JOIN msdb.dbo.sysschedules d ON c.schedule_id = d.schedule_id		
					INNER JOIN msdb.dbo.sysjobsteps t ON j.job_id = t.job_id
					LEFT JOIN msdb.dbo.sysmaintplan_subplans s ON j.job_id = s.job_id
					OUTER APPLY (
						SELECT 
							AVG(CONVERT(INT,SUBSTRING(run_duration,1,2)) * 3600
								+ CONVERT(INT,SUBSTRING(run_duration,3,2)) * 60
								+ CONVERT(INT,SUBSTRING(run_duration,5,2))) AS avg_run_duration
						FROM (
							SELECT TOP 10 
								RIGHT('000000' + CONVERT(VARCHAR(6),run_duration),6) AS run_duration
							FROM msdb.dbo.sysjobhistory h 
							WHERE 1=1
							AND h.job_id = t.job_id
							AND h.step_id = t.step_id
							ORDER BY run_date DESC, run_time DESC
						) ha
					) ha
					WHERE t.job_id = @job_id
					AND t.step_id = @in_step
				) TOT
			) TOT
			ORDER BY step
			OPTION(MAXDOP 1)

			-- History
			SELECT
				run_date + ' ' + SUBSTRING(run_time,1,2) + ':' + SUBSTRING(run_time,3,2) + ':' + SUBSTRING(run_time,5,2) AS run_date			 
				, step_id
				, step_name				
				, run_status
				, h.message
				, h.server
				, SUBSTRING(run_duration,1,2) + ':' + SUBSTRING(run_duration,3,2) + ':' + SUBSTRING(run_duration,5,2) AS run_duration
			FROM (
				SELECT 
					t.step_id
					, t.step_name				
					, CASE h.run_status
						WHEN 0 THEN '실패'
						WHEN 1 THEN '성공'
						WHEN 2 THEN '다시 시도'
						WHEN 3 THEN '취소됨' 
						WHEN 4 THEN '진행 중' END AS run_status
					, CONVERT(VARCHAR(10),CONVERT(DATE,CONVERT(VARCHAR(8),h.run_date)),121) AS run_date
					, RIGHT('000000' + CONVERT(VARCHAR(6),h.run_time), 6) AS run_time
					, RIGHT('000000' + CONVERT(VARCHAR(6),run_duration), 6) run_duration	
					, h.message
					, h.server
				FROM msdb.dbo.sysjobsteps t
				INNER JOIN msdb.dbo.sysjobhistory h ON t.job_id = h.job_id AND t.step_id = h.step_id
				WHERE t.job_id = @job_id
				AND t.step_id = @in_step
				AND h.run_date > CONVERT(VARCHAR(8), DATEADD(MONTH, -1, GETDATE()),112)
			) h
			ORDER BY h.run_date DESC, h.run_time DESC, h.step_id
		END

	END

END
