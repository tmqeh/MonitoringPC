
-- =============================================
-- Author: 이지수
-- Create date: 2024.07.30
-- Description: Export Table Description with Indexes
-- History : 
--			2024.07.30 이지수 최초작성
--			2024.08.02 이지수 데이터베이스명 변수 추가
-- =============================================
CREATE PROCEDURE [dbo].[usp_ExportScript_Tables]
	@in_DatabaseName		VARCHAR(100) 
	, @in_FilePath			VARCHAR(1000) = 'D:\Backup\DDLBackup\'								
	, @in_FileName			VARCHAR(500) = 'createTable_Script'
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
	DECLARE @sSQL1 VARCHAR(MAX) = ''
	DECLARE @sSQL2 VARCHAR(MAX) = ''
	DECLARE @nSQL NVARCHAR(MAX) = ''

	IF DB_ID(@in_DatabaseName) IS NULL
		RETURN

	SET @sSQL1 = '
		-- 테이블 정보 관련 변수		
		DECLARE @tbScript VARCHAR(MAX) = ''''
		DECLARE @tbName VARCHAR(500) = ''''
		DECLARE @tbId INT = 0
		DECLARE @tbPK VARCHAR(MAX) = ''''
		DECLARE @tbFK VARCHAR(MAX) = ''''
		DECLARE @tbDF VARCHAR(MAX) = ''''
		DECLARE @tbCOL VARCHAR(MAX) = ''''
		DECLARE @tbCH VARCHAR(MAX) = ''''
		DECLARE @tbIdx VARCHAR(MAX) = ''''
		DECLARE @tbDes VARCHAR(MAX) = ''''

		SET @totalScript = ''''

		USE [' + @in_DatabaseName + ']

		SET @tbScript = CHAR(10) + ''USE [' + @in_DatabaseName + ']'' + CHAR(10) + ''GO'' 

		DECLARE tbList CURSOR LOCAL FOR
			SELECT 
				name
				, object_id
			FROM sys.tables
			WHERE is_ms_shipped = 0	-- MS 기본 생성 테이블 제외
		OPEN tbList

		FETCH NEXT FROM tbList INTO @tbName, @tbId

		WHILE @@FETCH_STATUS = 0
		BEGIN
	
			SET @tbPK = ''''
			SET @tbFK = ''''
			SET @tbDF = ''''
			SET @tbCOL = ''''
			SET @tbCH = ''''
			SET @tbIdx = ''''
			SET @tbDes = ''''	

			SET @tbScript += CHAR(10) + ''	
		/****** Object:  Table  ['' + OBJECT_SCHEMA_NAME(@tbId) + ''].[''+ @tbName + '']    Script Date: ''+ CONVERT(VARCHAR(30), CURRENT_TIMESTAMP, 121) +'' ******/	'' 


			-- 테이블 컬럼 정보
			SELECT @tbCOL = STUFF((
				SELECT '',''
					+ CHAR(10) 
					+ CHAR(9)
					+ ''['' + C.name + '']''
					+ '' ''
					+ ''['' + Y.name + '']''
						+ (CASE 
							WHEN Y.system_type_id IN (165,167,173,175,239) THEN ''('' + (CASE WHEN C.max_length = -1 THEN ''MAX'' ELSE CONVERT(VARCHAR(5),C.max_length) END) + '')''
							WHEN Y.system_type_id IN (231,239) THEN ''('' + (CASE WHEN C.max_length = -1 THEN ''MAX'' ELSE CONVERT(VARCHAR(5),C.max_length/2) END) + '')'' 
							ELSE '''' END)				-- 문자형일때
						+ (CASE WHEN Y.system_type_id IN (106, 108) THEN ''(''+ CONVERT(VARCHAR(5),c.precision) + '','' + CONVERT(VARCHAR(5),c.scale) + '')'' ELSE '''' END) 
					+ CASE c.is_nullable WHEN 0 THEN '' NOT NULL'' ELSE '''' END
				FROM sys.columns C 
				INNER JOIN sys.types Y ON C.system_type_id = Y.system_type_id AND C.system_type_id = CONVERT(TINYINT,Y.user_type_id) AND Y.user_type_id < 255							
				WHERE C.object_id = @tbId
			FOR XML PATH('''')), 1,1,'''') 

			-- PK 확인
			SELECT @tbPK = 
				'' CONSTRAINT ['' + CONVERT(VARCHAR(100),k.name COLLATE Korean_Wansung_CI_AS) + ''] PRIMARY KEY '' 
				+ CONVERT(VARCHAR(100),i.type_desc) COLLATE Korean_Wansung_CI_AS
				+ CHAR(10) + ''('' + kc.PrimaryKeyColumn 
				+ CHAR(10) + '')WITH (PAD_INDEX = '' + CASE i.is_padded WHEN 0 THEN ''OFF'' ELSE ''ON'' END
				+ '', IGNORE_DUP_KEY = '' + CASE i.ignore_dup_key WHEN 0 THEN ''OFF'' ELSE ''ON'' END
				+ '', ALLOW_ROW_LOCKS = '' + CASE i.allow_row_locks WHEN 0 THEN ''OFF'' ELSE ''ON'' END
				+ '', ALLOW_PAGE_LOCKS = '' + CASE i.allow_page_locks WHEN 0 THEN ''OFF'' ELSE ''ON'' END
				+ CASE WHEN i.fill_factor > 0 THEN '', FILLFACTOR = '' + CONVERT(VARCHAR(2),i.fill_factor) ELSE '''' END
				+ '') ON '' + ''['' + ISNULL(f.groupname,''PRIMARY'') + '']''
			FROM sys.key_constraints k
			INNER JOIN sys.indexes i ON k.parent_object_id = i.object_id
			INNER JOIN sys.sysindexes ix ON k.parent_object_id = ix.id
			LEFT JOIN sys.sysfilegroups f ON ix.groupid = f.groupid
			OUTER APPLY (
			   SELECT STUFF((
				   SELECT 
						'','' + CHAR(10) + CHAR(9) 
						+ ''['' + c.[name] + '']'' + (CASE WHEN ic.is_descending_key = 1 THEN '' DESC'' ELSE '' ASC'' END)
				   FROM sys.index_columns ic WITH(FORCESEEK)
				   INNER JOIN sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id
				   WHERE ic.object_id = k.parent_object_id
				   AND ic.index_id = k.unique_index_id
				   AND ic.is_included_column = 0
				   AND ic.key_ordinal > 0
				   ORDER BY ic.key_ordinal
			   FOR XML PATH('''')), 1,1,'''') PrimaryKeyColumn
			) kc
			WHERE k.parent_object_id = @tbId
			AND k.type = ''PK''
			AND k.is_ms_shipped = 0

			-- 기본 설정 & 테이블 생성 구문
			SELECT @tbScript 
				+= CASE t.uses_ansi_nulls WHEN 1 THEN CHAR(10) + ''SET ANSI_NULLS ON'' ELSE ''SET ANSI_NULLS OFF'' END
					+ CHAR(10) + ''GO''
					+ CHAR(10) 
				+ CHAR(10) + ''CREATE TABLE ['' + OBJECT_SCHEMA_NAME(@tbId) + ''].[''+ @tbName + '']('' + @tbCOL		
				+ CASE WHEN ISNULL(@tbPK,'''') != '''' THEN CHAR(10) + @tbPK ELSE '''' END
				+ CHAR(10) + '') ON ['' + ISNULL(f.groupname,''PRIMARY'') + '']''
				+ CHAR(10) + ''GO''
			FROM sys.tables t
			LEFT JOIN sys.indexes i ON t.object_id = i.object_id AND i.index_id IN (0,1)
			LEFT JOIN sys.sysfilegroups f ON i.data_space_id = f.groupid
			WHERE t.object_id = @tbId
		
			-- FK 
			SELECT @tbFK = CHAR(10) + STUFF((
				SELECT 
					CHAR(10) + CHAR(10)
					+ ''ALTER TABLE ['' + OBJECT_SCHEMA_NAME(@tbId) + ''].[''+ @tbName + ''] WITH ''
					+ CASE is_disabled WHEN 1 THEN ''NOCHECK'' ELSE ''CHECK'' END
					+ '' ADD CONSTRAINT ['' 
					+ f.name 
					+ ''] FOREIGN KEY ('' + fc.ForeignKeyColumn + '')''
					+ CHAR(10) + ''REFERENCES [''+ OBJECT_SCHEMA_NAME(f.referenced_object_id) + ''].[''+ r.name + ''] (''+ fc.ReferencedColumn +'')''
					+ CHAR(10) + ''GO''
					+ CHAR(10) + CHAR(10)
					+ ''ALTER TABLE ['' + OBJECT_SCHEMA_NAME(@tbId) + ''].[''+ @tbName + ''] '' 
					+ CASE is_disabled WHEN 1 THEN ''NOCHECK'' ELSE ''CHECK'' END + '' CONSTRAINT ['' + f.name + '']''
					+ CHAR(10)
					+ ''GO''
				FROM sys.foreign_keys f
				LEFT JOIN sys.objects r ON f.referenced_object_id = r.object_id
				OUTER APPLY (
					SELECT
						STUFF(fc.query(''/ForeignKeyColumn'').value(''/'',''VARCHAR(MAX)''),1,1,'''') AS ForeignKeyColumn
						, STUFF(fc.query(''/ReferencedColumn'').value(''/'',''VARCHAR(MAX)''),1,1,'''') AS ReferencedColumn
					FROM (
						SELECT (
							SELECT 
								'','' + ''['' + c.[name] + '']'' AS ForeignKeyColumn
								, '','' + ''['' + rc.[name] + '']'' AS ReferencedColumn
							FROM sys.foreign_key_columns fc 
							LEFT JOIN sys.columns c ON fc.parent_object_id = c.object_id AND fc.parent_column_id = c.column_id
							LEFT JOIN sys.columns rc ON fc.referenced_object_id = rc.object_id AND fc.referenced_column_id = rc.column_id
							WHERE fc.constraint_object_id = f.object_id
							ORDER BY fc.constraint_column_id
							FOR XML PATH(''''), type
						) fc
					) fc
				) fc
				WHERE f.parent_object_id = @tbId
			FOR XML PATH('''')), 1,1,'''') 

			-- DF
			SELECT @tbDF = 
				CHAR(10) + CHAR(10)
				+ ''ALTER TABLE ['' + OBJECT_SCHEMA_NAME(@tbId) + ''].[''+ @tbName 
				+ ''] ADD CONSTRAINT ['' + d.name + ''] DEFAULT '' + d.definition
				+ '' FOR ['' + c.name + '']''
				+ CHAR(10) + ''GO''
			FROM sys.default_constraints d
			LEFT JOIN sys.columns c ON d.parent_object_id = c.object_id AND d.parent_column_id = c.column_id
			WHERE d.parent_object_id = @tbId

			-- CHECK
			SELECT @tbCH = 
				CHAR(10) + CHAR(10)
				+ ''ALTER TABLE ['' + OBJECT_SCHEMA_NAME(@tbId) + ''].[''+ @tbName + ''] ''
				+ ''ADD CONSTRAINT ['' + name + '']''
				+ ''CHECK '' + definition 
				+ CHAR(10) + ''GO''
			FROM sys.check_constraints
			WHERE parent_object_id = @tbId '

	SET @sSQL2 = '

			-- INDEX
			SELECT @tbIdx = STUFF((
				SELECT
					CHAR(10)
					+ ''/****** Object:  Index ['' + i.name COLLATE Korean_Wansung_CI_AS + '']    Script Date: '' + CONVERT(VARCHAR(30), CURRENT_TIMESTAMP, 121) + '' ******/''
					+ CHAR(10) 
					+ ''CREATE '' + type_desc COLLATE Korean_Wansung_CI_AS + '' INDEX ['' + i.name COLLATE Korean_Wansung_CI_AS + ''] ON ['' + OBJECT_SCHEMA_NAME(@tbId) + ''].[''+ @tbName + ''] ''
					+ CHAR(10) + ''(''
					+ CHAR(10) + ic.IndexColumn 
					+ CHAR(10) + '')''
					+ CASE 
						WHEN icc.IncludeColumn IS NOT NULL THEN + CHAR(10) + ''INCLUDE'' + CHAR(10) + ''('' + ISNULL(icc.IncludeColumn,'''') + CHAR(10) + '')''
						ELSE '''' END
					+ ''WITH (PAD_INDEX = '' + CASE i.is_padded WHEN 0 THEN ''OFF'' ELSE ''ON'' END
					+ '', IGNORE_DUP_KEY = '' + CASE i.ignore_dup_key WHEN 0 THEN ''OFF'' ELSE ''ON'' END
					+ '', ALLOW_ROW_LOCKS = '' + CASE i.allow_row_locks WHEN 0 THEN ''OFF'' ELSE ''ON'' END
					+ '', ALLOW_PAGE_LOCKS = '' + CASE i.allow_page_locks WHEN 0 THEN ''OFF'' ELSE ''ON'' END
					+ CASE WHEN i.fill_factor > 0 THEN '', FILLFACTOR = '' + CONVERT(VARCHAR(3),i.fill_factor) ELSE '''' END
					+ '') ON '' + ''['' + ISNULL(f.groupname,''PRIMARY'') + '']''
					+ CHAR(10) + ''GO''
				FROM sys.indexes i
				INNER JOIN sys.sysindexes ix ON i.object_id = ix.id AND i.index_id = ix.indid
				LEFT JOIN sys.sysfilegroups f ON ix.groupid = f.groupid
				OUTER APPLY (
				   SELECT STUFF((
					   SELECT 
							'','' + CHAR(10) + CHAR(9) 
							+ ''['' + c.[name] + '']'' + (CASE WHEN ic.is_descending_key = 1 THEN '' DESC'' ELSE '' ASC'' END)
					   FROM sys.index_columns ic WITH(FORCESEEK)
					   INNER JOIN sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id
					   WHERE ic.object_id = i.object_id
					   AND ic.index_id = i.index_id
					   AND ic.is_included_column = 0
					   AND ic.key_ordinal > 0
					   ORDER BY ic.key_ordinal
				   FOR XML PATH('''')), 1,2,'''') AS IndexColumn
				) ic
				OUTER APPLY (
					SELECT STUFF((
						SELECT 
							'','' + CHAR(10) + CHAR(9) 
							+ c.[name] 
						FROM sys.index_columns ic WITH(FORCESEEK)
						INNER JOIN sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id
						WHERE ic.object_id = i.object_id
						AND i.index_id = ic.index_id
						AND ic.is_included_column = 1
					FOR XML PATH('''')), 1,2,'''') IncludeColumn
				) icc
				WHERE i.object_id = @tbId
				AND is_primary_key = 0
				AND index_id > 0
			FOR XML PATH('''')), 1,0,'''') 

			-- Column Description
			SELECT @tbDes = CHAR(10) + STUFF((
				SELECT
					CHAR(10)
					+ ''EXEC sys.sp_addextendedproperty @name='''''' + CONVERT(VARCHAR(30), xp.name) 
						+ '''''', @value=N'''''' + CONVERT(VARCHAR(100), xp.value) 
						+ '''''', @level0type=N''''SCHEMA'''',@level0name=N'''''' + OBJECT_SCHEMA_NAME(@tbId) 
						+ '''''', @level1type=N''''TABLE'''',@level1name=N'''''' + OBJECT_NAME(@tbId) 
						+  '''''', @level2type=N''''COLUMN'''',@level2name=N'''''' + c.name + ''''''''
					+ CHAR(10)
					+ ''GO''
				FROM sys.columns c
				INNER JOIN sys.extended_properties xp ON xp.major_id = c.object_id AND xp.minor_id = c.column_id AND xp.name = CONVERT(SYSNAME,''MS_Description'') 
				WHERE c.object_id = @tbId
			FOR XML PATH('''')), 1,0,'''') 

			-- Table Description
			SELECT TOP 1 @tbDes += CHAR(10) 
				+ ''EXEC sys.sp_addextendedproperty @name=N'''''' + CONVERT(VARCHAR(30), xp.name) 
					+ '''''', @value=N'''''' + CONVERT(VARCHAR(100), xp.value) 
					+ '''''' , @level0type=N''''SCHEMA'''',@level0name=N'''''' + OBJECT_SCHEMA_NAME(@tbId) 
					+ '''''', @level1type=N''''TABLE'''',@level1name=N'''''' + OBJECT_NAME(@tbId) + ''''''''
					+ CHAR(10)
					+ ''GO''
			FROM sys.extended_properties xp
			WHERE xp.major_id = @tbId
			AND xp.minor_id = 0
			AND xp.name = CONVERT(SYSNAME,''MS_Description'')

			SET @tbScript += ISNULL(@tbFK,'''') + ISNULL(@tbDF,'''') + ISNULL(@tbCH,'''') + ISNULL(@tbIdx,'''') + ISNULL(@tbDes,'''')
	
			FETCH NEXT FROM tbList INTO @tbName, @tbId
		END

	
			SET @totalScript += ISNULL(@tbScript,'''')

		CLOSE tbList
		DEALLOCATE tbList '

	SET @nSQL = @sSQL1 + @sSQL2
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
