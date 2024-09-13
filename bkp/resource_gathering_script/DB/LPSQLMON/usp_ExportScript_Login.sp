-- =============================================
-- Author: 이지수
-- Create date: 2024.07.30
-- Description: Export Database Login With Server Permission
-- History : 
--			 2024.07.30 이지수 최초작성
-- =============================================
CREATE PROCEDURE [dbo].[usp_ExportScript_Login]
	@in_FilePath			VARCHAR(1000) = 'D:\Backup\DDLBackup\'								
	, @in_FileName			VARCHAR(500) = 'createLogin_Script'
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
	DECLARE @loginScript NVARCHAR(MAX) = ''


	-- 1. 스크립트 생성
	SELECT @loginScript 
		= 'USE master'+ CHAR(10) + 'GO' + CHAR(10)
		+ STUFF((
			SELECT CHAR(10) +
					'CREATE LOGIN [' + L.name + ']'
						+ CHAR(10) + 'WITH PASSWORD = ' + CONVERT(VARCHAR(1000),L.password_hash, 1) + ' HASHED' 
						+ CHAR(10) + '	, SID = ' + CONVERT(VARCHAR(1000),L.sid, 1)
						+ CHAR(10) + '	, DEFAULT_DATABASE = [' + L.default_database_name + ']'
						+ CHAR(10) + '	, CHECK_EXPIRATION = ' + CASE WHEN L.is_expiration_checked = 0 THEN 'OFF' ELSE 'ON' END
						+ CHAR(10) + '	, CHECK_POLICY = ' + CASE WHEN L.is_policy_checked = 0 THEN 'OFF' ELSE 'ON' END
						+ CHAR(10) + 'GO'
						+ CASE WHEN L.is_disabled = 0 THEN '' ELSE CHAR(10) + 'ALTER LOGIN [' + L.name + '] DISABLE' + CHAR(10) + 'GO' END
			FROM sys.sql_logins L
			WHERE L.principal_id > 1    
			AND L.name NOT LIKE '##MS_%##' 
			AND L.type = 'S'
		FOR XML PATH('')),1,0,'') 

	SELECT @loginScript 
		+= STUFF((
			SELECT 
				CASE 
				WHEN SSP.name IS NULL THEN '' 
				ELSE CHAR(10) + 'ALTER SERVER ROLE [' + CONVERT(VARCHAR(10),SSP.name) + '] ADD MEMBER [' + L.name + ']' + CHAR(10) + 'GO' END
			FROM sys.sql_logins L
			INNER JOIN sys.server_principals AS USP ON USP.sid = L.sid 
			INNER JOIN sys.server_role_members AS RM ON RM.member_principal_id = USP.principal_id
			LEFT JOIN sys.server_principals AS SSP	ON RM.role_principal_id = SSP.principal_id  
			WHERE L.principal_id > 1    
			AND L.name NOT LIKE '##MS_%##' 
			AND L.type = 'S'
			AND USP.is_disabled = 0	
		FOR XML PATH('')),1,0,'') 	

--	PRINT @loginScript
	SET @totalScript += ISNULL(@loginScript,'')
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
