
-- =============================================
-- Author: 이지수
-- Create date: 2024.07.30
-- Description: Export Database Permissions On Database Users & Roles
-- History : 
--			2024.07.30 이지수 최초작성
--			2024.08.02 이지수 데이터베이스명 변수 추가
-- =============================================
CREATE PROCEDURE [dbo].[usp_ExportScript_DatabasePermissions]
	@in_DatabaseName		VARCHAR(100) 
	, @in_FilePath			VARCHAR(1000) = 'D:\Backup\DDLBackup\'									
	, @in_FileName			VARCHAR(500) = 'creatDatabasePermission_Script'
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
	DECLARE @chkOAP BIT = 0
	DECLARE @sSQL VARCHAR(MAX) = ''
	DECLARE @nSQL NVARCHAR(MAX) = ''

	IF DB_ID(@in_DatabaseName) IS NULL
		RETURN

	SET @sSQL = '
		USE [' + @in_DatabaseName + ']

		DECLARE @userSID VARBINARY(85) 
		DECLARE @userPrincipal INT = 0
		DECLARE @userScript VARCHAR(MAX) = ''''
		SET @totalScript = ''''

		SET @totalScript = CHAR(10) + CHAR(9) + ''USE [' + @in_DatabaseName + ']'' + CHAR(10) + CHAR(9) + ''GO'' 

		SELECT @totalScript += CHAR(10) + CHAR(10) + CHAR(9) 
			+ ''/****** Object:  DatabaseRole ['' + p.name + '']    Script Date: '' + CONVERT(VARCHAR(30), CURRENT_TIMESTAMP, 121) + '' ******/''
			+ CHAR(10) + CHAR(9) + ''CREATE ROLE ['' + p.name + '']''
			+ CHAR(10) + CHAR(9) + ''GO''
			+ CASE WHEN m.state_desc IS NOT NULL THEN CHAR(10) + CHAR(9) + m.state_desc COLLATE Korean_Wansung_CI_AS + '' '' + m.permission_name COLLATE Korean_Wansung_CI_AS + '' TO ['' + p.name + '']'' + CHAR(10) + CHAR(9) + ''GO'' ELSE '''' END
		FROM sys.database_principals p
		LEFT JOIN (
			SELECT DISTINCT
				grantee_principal_id
				 , state_desc 
				 , i.permission_name
			FROM sys.database_permissions m
			OUTER APPLY (
				SELECT STUFF((
					SELECT '', '' + permission_name
					FROM sys.database_permissions i
					WHERE m.grantee_principal_id = i.grantee_principal_id
					FOR XML PATH('''')),1,2,'''') AS permission_name
			) i
			WHERE NOT EXISTS (
				SELECT 1
				FROM sys.sysobjects
				WHERE id = m.major_id
				AND m.grantee_principal_id > 0)
		) m ON m.grantee_principal_id = p.principal_id
		WHERE p.type = ''R''
		AND is_fixed_role = 0
		AND p.principal_id > 0

	
		DECLARE userList CURSOR LOCAL FOR
			SELECT principal_id, sid
			FROM sys.database_principals p		
			WHERE type = ''S''
			AND authentication_type > 0			-- 별도 인증방법이 존재하는 User만 스크립팅
			AND EXISTS (
				SELECT 1
				FROM sys.syslogins 
				WHERE p.sid = sid )
		OPEN userList

		FETCH NEXT FROM userList INTO @userPrincipal, @userSID

		WHILE @@FETCH_STATUS = 0
		BEGIN

			SELECT @userScript = 
				CHAR(10) + CHAR(10) + CHAR(9) + ''/****** Object:  User ['' + u.name + '']    Script Date: '' + CONVERT(VARCHAR(30), CURRENT_TIMESTAMP, 121) + '' ******/''
				+ CHAR(10) + CHAR(9) 
				+ ''CREATE USER ['' + u.name + ''] FOR LOGIN ['' + l.loginname + ''] WITH DEFAULT_SCHEMA=['' + u.default_schema_name + '']''
				+ CHAR(10) + CHAR(9) + ''GO''
			FROM sys.database_principals u
			INNER JOIN sys.syslogins l ON u.sid = l.sid
			WHERE u.sid = @userSID

			SELECT @userScript += 
				CHAR(10) + CHAR(9) 
				+ ''ALTER ROLE ['' + p.name + ''] ADD MEMBER ['' + m.name + '']'' + CHAR(10) + CHAR(9) + ''GO''
			FROM sys.database_role_members r
			LEFT JOIN sys.database_principals m ON r.member_principal_id = m.principal_id
			LEFT JOIN sys.database_principals p ON r.role_principal_id = p.principal_id
			WHERE r.member_principal_id = @userPrincipal

			SET @totalScript += ISNULL(@userScript,'''')
		
			FETCH NEXT FROM userList INTO @userPrincipal, @userSID
		END	

		CLOSE userList
		DEALLOCATE userList

		SET @totalScript += CHAR(10)
		SELECT 
			@totalScript += CHAR(10) + CHAR(9) 
			+ p.state_desc + '' '' + p.permission_name + '' ON object::['' + OBJECT_SCHEMA_NAME(i.object_id) + ''].['' + i.name + ''] TO ['' + d.name + '']''
			+ CHAR(10) + CHAR(9) + ''GO''
		FROM sys.objects i
		INNER JOIN (
			SELECT DISTINCT
				m.grantee_principal_id
				, m.state_desc
				, m.major_id 
				, s.permission_name			
			FROM sys.database_permissions m		
			OUTER APPLY (
				SELECT STUFF((
					SELECT '', '' + permission_name
					FROM sys.database_permissions s
					WHERE s.grantee_principal_id = m.grantee_principal_id
					AND s.major_id = m.major_id
					AND s.state_desc = m.state_desc
					FOR XML PATH('''')),1,2,'''') AS permission_name			
			)  s
			WHERE m.major_id <> 0
		) p ON i.object_id = p.major_id
		LEFT JOIN sys.database_principals d ON p.grantee_principal_id = d.principal_id	'

--	PRINT @sSQL
	SET @nSQL = @sSQL
	EXEC sp_executesql 
		@nSQL
		, N'@databaseName		VARCHAR(100) 
			, @totalScript		VARCHAR(MAX) OUTPUT '
		, @databaseName			= @in_DatabaseName
		, @totalScript			= @out_totalScript OUTPUT

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
