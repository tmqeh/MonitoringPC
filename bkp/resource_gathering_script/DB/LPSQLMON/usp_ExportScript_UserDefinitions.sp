
-- =============================================
-- Author: 이지수
-- Create date: 2024.07.30
-- Description: Export User Description (SP, VW, FN, SQ)
-- History : 
--			2024.07.30 이지수 최초작성
--			2024.08.02 이지수 데이터베이스명 변수 추가
-- =============================================
CREATE PROCEDURE [dbo].[usp_ExportScript_UserDefinitions]
	@in_DatabaseName		VARCHAR(100) 
	, @in_FilePath			VARCHAR(1000) = 'D:\Backup\DDLBackup\'								
	, @in_FileName			VARCHAR(500) = 'createUserDefinitions_Script'
AS
BEGIN
	SET NOCOUNT ON
	SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED

	-- 스크립팅 관련 변수
	DECLARE @out_totalScript VARCHAR(MAX) = ''
	DECLARE @File VARCHAR(1000)
	DECLARE @FileID INT
	DECLARE @IsFileExist INT 
	DECLARE @IsFileCreate INT
	DECLARE @totalScript VARCHAR(MAX) = ''
	DECLARE @chkOAP BIT = 0
	DECLARE @sSQL VARCHAR(MAX) = ''
	DECLARE @nSQL NVARCHAR(MAX) = ''

	IF DB_ID(@in_DatabaseName) IS NULL
		RETURN

	SET @sSQL = '		
		USE [' + @in_DatabaseName + ']

		SET @totalScript = ''''
		SET @totalScript = CHAR(10) + ''USE [' + @in_DatabaseName + ']'' + CHAR(10) + ''GO'' 

		SELECT @totalScript += CHAR(10) + CHAR(10) 
			+ ''/****** Object:  '' + 
				CASE o.type 
					WHEN ''P''	THEN ''StoredProcedure''				-- SQL 저장 프로시저
					WHEN ''FN''	THEN ''UserDefinedFunction''			-- SQL 스칼라 함수
					WHEN ''IF''	THEN ''UserDefinedFunction''			-- SQL TVF(인라인 테이블 반환 함수) 
					WHEN ''V''	THEN ''View'' END						-- View
			+ '' ['' + s.name + ''].['' + o.name + '']    Script Date: ''+ CONVERT(VARCHAR(30), CURRENT_TIMESTAMP, 121) +'' ******/''
			+ CHAR(10) + CASE m.uses_ansi_nulls WHEN 1 THEN ''SET ANSI_NULLS ON'' ELSE ''SET ANSI_NULLS OFF'' END + CHAR(10) + ''GO''
			+ CHAR(10) + CASE m.uses_quoted_identifier WHEN 1 THEN ''SET QUOTED_IDENTIFIER ON'' ELSE ''SET QUOTED_IDENTIFIER OFF'' END + CHAR(10) + ''GO''
			+ m.definition + CHAR(10) + ''GO''
			+ CHAR(10)
		FROM sys.objects o
		LEFT JOIN sys.schemas s ON o.schema_id = s.schema_id
		LEFT JOIN sys.sql_modules m ON o.object_id = m.object_id
		WHERE o.is_ms_shipped = 0
		AND o.type IN (''P'',''FN'',''IF'',''V'')

		-- Sequence 개체 
		IF EXISTS (
			SELECT 1
			FROM sys.objects o
			WHERE o.is_ms_shipped = 0
			AND o.type = ''SO'' )
		BEGIN
			SELECT @totalScript += CHAR(10) + CHAR(10) 
				+ ''/****** Object:  Sequence ['' + s.name + ''].['' + o.name + '']    Script Date: ''+ CONVERT(VARCHAR(30), CURRENT_TIMESTAMP, 121) + '' ******/''
				+ CHAR(10) + ''CREATE SEQUENCE ['' + s.name + ''].['' + o.name + '']''
				+ CHAR(10) + ''AS ['' + y.name + '']''
				+ CHAR(10) + ''START WITH '' + CONVERT(VARCHAR(20), q.start_value)
				+ CHAR(10) + ''INCREMENT BY '' + CONVERT(VARCHAR(20), q.increment)
				+ CHAR(10) + ''MINVALUE '' + CONVERT(VARCHAR(20), q.minimum_value)
				+ CHAR(10) + ''MAXVALUE '' + CONVERT(VARCHAR(20), q.maximum_value)
				+ CHAR(10) + CASE WHEN is_cycling = 1 THEN ''CYCLE'' ELSE '''' END 
				+ CHAR(10) + CASE WHEN is_cached = 1 THEN ''CACHE '' + CONVERT(VARCHAR(20), cache_size) ELSE '''' END 
				+ CHAR(10) + ''GO'' + CHAR(10)
			FROM sys.objects o 
			LEFT JOIN sys.schemas s ON o.schema_id = s.schema_id
			LEFT JOIN sys.sequences q ON o.object_id = q.object_id
			LEFT JOIN sys.types y ON q.system_type_id = y.system_type_id AND q.system_type_id = CONVERT(TINYINT,y.user_type_id) AND y.user_type_id < 255							
			WHERE o.is_ms_shipped = 0
			AND o.type = ''SO'' 
		END '
		
	SET @nSQL = @sSQL
	EXEC sp_executesql 
		@nSQL
		, N'@databaseName		VARCHAR(100) 
			, @totalScript		VARCHAR(MAX) OUTPUT '
		, @databaseName			= @in_DatabaseName
		, @totalScript			= @out_totalScript OUTPUT

--	PRINT @sSQL
--	PRINT @out_totalScript

	-- 2. 파일로 저장
	SET @File = @in_FilePath + @in_FileName + '_' + @in_DatabaseName + '_' + CONVERT(VARCHAR(8), GETDATE(),112) + '.sql'
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

	EXEC SP_OAMETHOD @FileID, 'WRITELINE', NULL, @out_totalScript
	EXECUTE SP_OADESTROY @FileID
	EXECUTE SP_OADESTROY @IsFileCreate

	IF @chkOAP = 0 
	BEGIN
		EXEC sp_configure 'Ole Automation Procedures', 0;
		RECONFIGURE;
	END

END
