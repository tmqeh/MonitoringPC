

/*=============================================
-- Author:			이지수
-- Create date:		2022-09-19
-- Description:		특정 문자열이 포함된 Object 조회
-- Modify History : 
-- Example:	
	EXEC MonitoringDB.dbo.usp_SearchTextObject 'MonitoringDB','WHOISACTIVE'
	GO
=============================================*/
CREATE PROCEDURE [dbo].[usp_SearchTextObject] 
	@in_Database		VARCHAR(128)
	, @in_TextData		VARCHAR(100)
AS
BEGIN
	SET NOCOUNT ON
	SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED

	DECLARE @sSQL VARCHAR(MAX) = ''
	DECLARE @nSQL NVARCHAR(MAX) = ''
	DECLARE @nPARAM NVARCHAR(100) = ''

	SET @sSQL = '
		USE ' + @in_Database + '
		
		DECLARE @nTextData NVARCHAR(100) = @in_TextData
		DECLARE @TMP_ObjectId TABLE (
			object_id		INT
		)

		INSERT INTO @TMP_ObjectId
		SELECT id
		FROM sys.syscomments
		WHERE text LIKE ''%'' + @nTextData + ''%''

		INSERT INTO @TMP_ObjectId
		SELECT m.object_id
		FROM sys.sql_modules m 
		WHERE definition LIKE ''%'' + @nTextData + ''%''
		AND NOT EXISTS (
			SELECT 1
			FROM @TMP_ObjectId
			WHERE object_id = m.object_id )

		SELECT
			ROW_NUMBER()OVER(ORDER BY o.object_id) AS SEQ
			, o.type_desc 
			, DB_NAME() + ''.'' + s.name + ''.'' + o.name AS ObjectName
		FROM sys.objects o WITH(FORCESEEK)
		INNER JOIN sys.schemas s ON o.schema_id = s.schema_id
		WHERE EXISTS (
			SELECT 1
			FROM @TMP_ObjectId
			WHERE object_id = o.object_id )
		AND o.type IN (''P'',''TF'',''FN'',''V'',''IF'',''X'',''TR'')	'

	SET @nSQL = @sSQL
	SET @nPARAM = '
		@in_Database		VARCHAR(128)
		, @in_TextData		VARCHAR(100)	'

	EXEC SP_EXECUTESQL @nSQL, @nPARAM
		, @in_Database	= @in_Database	
		, @in_TextData	= @in_TextData	

END
