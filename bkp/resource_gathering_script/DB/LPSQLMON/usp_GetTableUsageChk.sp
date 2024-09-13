
-- =============================================
-- Author:  jyh
-- Create date: 2020.03.02
-- Description: Server Resource BULK INSERT MULTIPLE FILES From a Folder 
-- History : 
		-- 2022.10.24 김진우 hostname SUBSTRING 로직 변경
-- =============================================
CREATE PROCEDURE [dbo].[usp_GetTableUsageChk]
 -- Add the parameters for the stored procedure here
AS

BEGIN
    -- when File List Temp Table Exist, then reCreate
    IF OBJECT_ID(N'tempdb..#TB_Svr_TBL_filelist_T', 'U') IS NOT NULL
		DROP TABLE #TB_Svr_TBL_filelist_T;
    CREATE TABLE #TB_Svr_TBL_filelist_T (hostname VARCHAR(30), path VARCHAR(255),fileName varchar(255), )

    -- when Resource Bulk Insert Temp Table Exist, then reCreate
    IF OBJECT_ID(N'tempdb..#TB_Svr_TBL_Chk_L', 'U') IS NOT NULL
        DROP TABLE #TB_Svr_TBL_Chk_L;
    CREATE TABLE #TB_Svr_TBL_Chk_L (Value varchar(max));

    declare @filename varchar(255),
            @path     varchar(255),
            @sql      varchar(8000),
            @cmd      varchar(1000)


    -- get the list of files from Specific Directory
    -- be aware of xp_cmdShell
    SET @path = 'D:\gatherLog\'
    
    SET @cmd = 'dir ' + @path + '*.table_usage.log /b'
    INSERT INTO  #TB_Svr_TBL_filelist_T (fileName)
    EXEC Master..xp_cmdShell @cmd
    
    UPDATE #TB_Svr_TBL_filelist_T 
    SET path = @path 
    --, hostname = substring(filename, CHARINDEX('_', filename)+1, len(filename)- CHARINDEX('.', filename)-2) 
	, hostname = substring(filename, CHARINDEX('_', filename)+1, CHARINDEX('.', filename)-CHARINDEX('_', filename)-1) --2022.10.24 김진우 SUBSTRING 로직 변경
    where path is null

    -- cursor loop
    -- target is for only TODAY
    declare c1 cursor for SELECT path,fileName FROM #TB_Svr_TBL_filelist_T where fileName like convert(varchar, getdate(), 112) +'%.table_usage.log%'
    open c1 fetch next from c1 into @path,@filename
    print(@@fetch_status)
        While @@fetch_status <> -1
          begin
          -- bulk insert won't take a variable name, so make a sql and execute it instead:
          -- cuz of above that, need to use literal SQL
           set @sql = 'BULK INSERT #TB_Svr_TBL_Chk_L FROM ''' + @path + @filename + ''' '
               + '     WITH ( 
                       ROWTERMINATOR = ''0x0a'', 
                       FIRSTROW = 5
                    ) '
        -- to debug uncomment it
        -- print @sql

        exec (@sql)


		insert into TB_Svr_TBL_Chk_L (	 DBNAME
										,COLLECTDT
										,TABLE_NAME
										,ROW_COUNT
										,TOTAL_MB
										,RGPR_ID
										,RGST_DTM
										,MDFPR_ID
										,MDF_DTM )
		SELECT	DBNAME
				,COLLECTDT
				,TABLE_NAME
				,ROW_COUNT
				,TOTAL_MB
				,RGPR_ID
				,RGST_DTM
				,MDFPR_ID
				,MDF_DTM
		FROM (
			SELECT	SUBSTRING(T1.VALUE, 1, LEN1-1)				AS DBNAME
				   ,SUBSTRING(T1.VALUE, LEN1+1, LEN2-LEN1-1)	AS COLLECTDT
				   ,SUBSTRING(T1.VALUE, LEN2+1, LEN3-LEN2-1)	AS TABLE_NAME
				   ,SUBSTRING(T1.VALUE, LEN3+1, LEN4-LEN3-1)	AS ROW_COUNT
				   ,SUBSTRING(T1.VALUE, LEN4+1, LEN5-LEN4-1)	AS TOTAL_MB
				   ,'usp_GetTblUseChk'							AS RGPR_ID
				   ,GETDATE()									AS RGST_DTM
				   ,'usp_GetTblUseChk'							AS MDFPR_ID
				   ,GETDATE()									AS MDF_DTM
			FROM	(
					SELECT   CHARINDEX(',',T1.Value) AS LEN1
							,CHARINDEX(',',T1.Value,CHARINDEX(',',T1.Value)+1) AS LEN2
							,CHARINDEX(',',T1.Value,CHARINDEX(',',T1.Value,CHARINDEX(',',T1.Value)+1)+1) AS LEN3
							,CHARINDEX(',',T1.Value,CHARINDEX(',',T1.Value,CHARINDEX(',',T1.Value,CHARINDEX(',',T1.Value)+1)+1)+1) AS LEN4
							,LEN(T1.VALUE) AS LEN5
							,T1.*
					FROM	#TB_Svr_TBL_Chk_L T1
					) T1
			WHERE	LEN1 > 0
		) T
		/* 20240403 이지수, 중복키 실패 방지 로직 추가 */
		WHERE NOT EXISTS (
			SELECT TOP 1 1
			FROM TB_Svr_TBL_Chk_L
			WHERE DBNAME = T.DBNAME
			AND COLLECTDT = T.COLLECTDT
			AND TABLE_NAME = T.TABLE_NAME)


        -- for below continuous Cursor
        DELETE #TB_Svr_TBL_Chk_L


    -- u have to close all of cursor in MS-SQL
    fetch next from c1 into @path,@filename
      end
    close c1
    deallocate c1

END