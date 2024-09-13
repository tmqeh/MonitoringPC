-- =============================================
-- Author: 이지수
-- Create date: 2024.07.30
-- Description: Export Agent Jobs
-- History : 
--			2024.07.30 이지수 최초작성
-- =============================================
CREATE PROCEDURE [dbo].[usp_ExportScript_AgentJobs]
	@in_FilePath			VARCHAR(1000) = 'D:\Backup\DDLBackup\'								
	, @in_FileName			VARCHAR(500) = 'createAgentJobs_Script'
AS
BEGIN
	SET NOCOUNT ON
	SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED

	-- 스크립팅 관련 변수
	DECLARE @File VARCHAR(1000)
	DECLARE @FileID INT
	DECLARE @IsFileExist INT 
	DECLARE @IsFileCreate INT
	DECLARE @totalScript VARCHAR(MAX) = ''
	DECLARE @chkOAP BIT = 0
	DECLARE @exeDB NVARCHAR(500) = ''

	DECLARE @jobScript VARCHAR(MAX) = ''
	DECLARE @job_id UNIQUEIDENTIFIER

	SET @jobScript = CHAR(10) + CHAR(9) + 'USE msdb' + CHAR(10) + CHAR(9) + 'GO'

	DECLARE jobList CURSOR FOR
		SELECT job_id
		FROM msdb.dbo.sysjobs
		WHERE name NOT IN ('syspolicy_purge_history','[SQLServerMonitor]Target CollectActiveData','[SQLServerMonitor]Target CollectPerfmonData')	-- 시스템 기본 JOB(syspolicy_purge_history), 모니터링JOB 제외
	OPEN jobList

	FETCH NEXT FROM jobList INTO @job_id

	WHILE @@FETCH_STATUS = 0
	BEGIN
		SELECT @jobScript = '
	/****** Object:  Job [' + CONVERT(VARCHAR(100),J.name) + ']    Script Date: ' + CONVERT(VARCHAR(24), GETDATE(), 121) + ' ******/
	BEGIN TRANSACTION
		DECLARE @ReturnCode INT = 0

		/****** Object:  JobCategory [' + CONVERT(VARCHAR(100),C.name) + ']]    Script Date: ' + CONVERT(VARCHAR(24), GETDATE(), 121) + ' ******/
		IF NOT EXISTS (
			SELECT 1
			FROM msdb.dbo.syscategories 
			WHERE name=N''[Uncategorized (Local)]'' 
			AND category_class=1)
		BEGIN
			EXEC @ReturnCode = msdb.dbo.sp_add_category 
				@class=N''JOB''
				, @type=N''LOCAL''
				, @name=N''[Uncategorized (Local)]''

			IF (@@ERROR <> 0 OR @ReturnCode <> 0) 
				GOTO QuitWithRollback
		END

		DECLARE @jobId BINARY(16)	

		EXEC @ReturnCode = msdb.dbo.sp_add_job 
			@job_name=N''' + CONVERT(VARCHAR(100),J.name) + '''
			, @enabled=' + CONVERT(VARCHAR,J.enabled) + '
			, @notify_level_eventlog=' + CONVERT(VARCHAR, J.notify_level_eventlog) + '
			, @notify_level_email=' + CONVERT(VARCHAR, J.notify_level_email) + '
			, @notify_level_netsend=' + CONVERT(VARCHAR, J.notify_level_netsend) + '
			, @notify_level_page=' + CONVERT(VARCHAR, J.notify_level_page) + '
			, @delete_level=' + CONVERT(VARCHAR, J.delete_level) + '
			, @description=N''' + ISNULL(J.description,'') + '''
			, @category_name=N''' + CONVERT(VARCHAR,C.name) + '''
			, @owner_login_name=N''' + CONVERT(VARCHAR, L.name) + '''
			, @job_id = @jobId OUTPUT
	
		IF (@@ERROR <> 0 OR @ReturnCode <> 0) 
			GOTO QuitWithRollback	'
		FROM msdb.dbo.sysjobs J
		LEFT JOIN msdb.dbo.syscategories C ON J.category_id = C.category_id
		LEFT JOIN sys.syslogins L ON J.owner_sid = L.sid
		WHERE J.job_id = @job_id
	
		SELECT @jobScript += STUFF((
		SELECT '

	/****** Object:  Step [' + CONVERT(VARCHAR(100),step_name) + ']    Script Date: ' + CONVERT(VARCHAR(24), GETDATE(), 121) + ' ******/
		EXEC @ReturnCode = msdb.dbo.sp_add_jobstep 
			@job_id=@jobId
			, @step_name=N''' + CONVERT(VARCHAR(100),step_name) + '''
			, @step_id=' + CONVERT(VARCHAR,step_id) + '
			, @cmdexec_success_code=' + CONVERT(VARCHAR, cmdexec_success_code) + '
			, @on_success_action=' + CONVERT(VARCHAR, on_success_action) + '
			, @on_success_step_id='+ CONVERT(VARCHAR, on_success_step_id) + '
			, @on_fail_action=' + CONVERT(VARCHAR, on_fail_action) + '
			, @on_fail_step_id=' + CONVERT(VARCHAR, on_fail_step_id) + '
			, @retry_attempts=' + CONVERT(VARCHAR, retry_attempts) + '
			, @retry_interval=' + CONVERT(VARCHAR, retry_interval) + '
			, @os_run_priority=' + CONVERT(VARCHAR, os_run_priority) + '
			, @subsystem=N''' + CONVERT(VARCHAR(50), subsystem) + '''
			, @command=N''' + REPLACE(CONVERT(VARCHAR(1000), ISNULL(command,'')),'''','''''') + ''''
				+ CASE WHEN database_name IS NULL THEN '' ELSE + ', @database_name=N''' + CONVERT(VARCHAR, ISNULL(database_name,'')) + '''' END
			+ '
			, @flags=0

		IF (@@ERROR <> 0 OR @ReturnCode <> 0) 
			GOTO QuitWithRollback	'
				+ CHAR(10)
			FROM msdb.dbo.sysjobsteps 
			WHERE job_id = @job_id
			ORDER BY step_id
		FOR XML PATH('')),1,0,'') 

		SET @jobScript += '
		EXEC @ReturnCode = msdb.dbo.sp_update_job 
			@job_id = @jobId
			, @start_step_id = 1

		IF (@@ERROR <> 0 OR @ReturnCode <> 0) 
			GOTO QuitWithRollback	'
			+ CHAR(10)

		SELECT @jobScript += STUFF((
			SELECT '
		EXEC @ReturnCode = msdb.dbo.sp_add_jobschedule 
			@job_id=@jobId
			, @name=N''' + CONVERT(VARCHAR(100),S.name) + '''
			, @enabled=' + CONVERT(VARCHAR, S.enabled) + '
			, @freq_type=' + CONVERT(VARCHAR, S.freq_type) + '
			, @freq_interval=' + CONVERT(VARCHAR, S.freq_interval) + '
			, @freq_subday_type=' + CONVERT(VARCHAR, S.freq_subday_type) + '
			, @freq_subday_interval=' + CONVERT(VARCHAR, S.freq_subday_interval) + '
			, @freq_relative_interval=' + CONVERT(VARCHAR, S.freq_relative_interval) + '
			, @freq_recurrence_factor=' + CONVERT(VARCHAR, S.freq_recurrence_factor) + '
			, @active_start_date=' + CONVERT(VARCHAR, S.active_start_date) + '
			, @active_end_date=' + CONVERT(VARCHAR, S.active_end_date) + '
			, @active_start_time=' + CONVERT(VARCHAR, S.active_start_time) + ' 
			, @active_end_time=' + CONVERT(VARCHAR, S.active_end_time) + '
	
		IF (@@ERROR <> 0 OR @ReturnCode <> 0) 
			GOTO QuitWithRollback	'
				+ CHAR(10)
			FROM msdb.dbo.sysjobschedules J
			INNER JOIN msdb.dbo.sysschedules S ON J.schedule_id = S.schedule_id
			WHERE J.job_id = @job_id
			ORDER BY J.schedule_id
		FOR XML PATH('')),1,0,'') 

		SELECT @jobScript += '
		EXEC @ReturnCode = msdb.dbo.sp_add_jobserver 
			@job_id = @jobId
			, @server_name = N''' +CASE WHEN S.server_id = 0 THEN '(local)' ELSE V.name END + '''

		IF (@@ERROR <> 0 OR @ReturnCode <> 0) 
			GOTO QuitWithRollback

	COMMIT TRANSACTION
	
	GOTO EndSave
	
	QuitWithRollback:
		IF (@@TRANCOUNT > 0) 
			ROLLBACK TRANSACTION
	EndSave:
	GO	'
			+ CHAR(10)
		FROM msdb.dbo.sysjobservers S
		LEFT JOIN SYS.servers V ON S.server_id = V.server_id
		WHERE S.job_id = @job_id

		SET @jobScript = REPLACE(REPLACE(REPLACE(@jobScript,'&#x0D;',''),'&lt;','<'),'&gt;','>')
		SET @totalScript += ISNULL(@jobScript,'')

		FETCH NEXT FROM jobList INTO @job_id
	END

	CLOSE jobList
	DEALLOCATE jobList

	SET @File = @in_FilePath + @in_FileName + '_' + CONVERT(VARCHAR(8), GETDATE(),112) + '.sql'

	-- 2. 파일로 저장
	EXEC master.sys.xp_fileexist @File, @IsFileExist OUT

	SELECT @chkOAP = CONVERT(BIT,value)
	FROM sys.configurations
	WHERE name = 'Ole Automation Procedures'

	IF @chkOAP = 0 
	BEGIN
		EXEC sp_configure 'Ole Automation Procedures', 1;
		RECONFIGURE;
	END

	EXEC SP_OACREATE  'SCRIPTING.FILESYSTEMOBJECT', @IsFileCreate OUT
	EXEC SP_OAMETHOD @IsFileCreate, 'OPENTEXTFILE', @FileID OUT, @File, 8, 1

	EXEC SP_OAMETHOD @FileID, 'WRITELINE', NULL, @totalScript
	EXECUTE SP_OADESTROY @FileID
	EXECUTE SP_OADESTROY @IsFileCreate

	IF @chkOAP = 0 
	BEGIN
		EXEC sp_configure 'Ole Automation Procedures', 0;
		RECONFIGURE;
	END
END
