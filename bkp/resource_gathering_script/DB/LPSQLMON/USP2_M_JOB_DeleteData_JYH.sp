
/*===========================================================================================
프로그램ID    : USP2_M_JOB_DeleteData
업무  명    : 모니터링 로그 데이터 삭제 배치
프로그램명    : 내부 배치
프로그램설명: META2_M_ScheduleInfo 테이블에 있는 데이터 보관주기 정책에 맞게 과거 데이터 삭제
실행예제    : EXEC USP2_M_JOB_DeleteData_JYH
변경이력    : 2024-08-28 신규 생성 by DBA
=============================================================================================*/
CREATE PROCEDURE [dbo].[USP2_M_JOB_DeleteData_JYH] 
AS
BEGIN
	SET NOCOUNT ON
	SET XACT_ABORT ON

	DECLARE @DEL_TRG_CNT INT = 5000 /* 한번에 삭제할 데이터 건수 */    
	DECLARE @ROWS INT
	DECLARE @SQL_TEXT NVARCHAR(2048) /* 다이나믹 쿼리 변수 */
	DECLARE @TRG_TB VARCHAR(30), @INST_ID INT, @TRG_DT VARCHAR(10) /* TEMP TABLE 결과를 CURSOR로 OPEN할 때, 담을 변수 */
	DECLARE @LOG_TRG_DT VARCHAR(8), @LOG_PART_NM VARCHAR(30) /* LOG 적재 시 매개변수 변형 불가하여 추가 변수 선언 */
	DECLARE @DEL_TOT_CNT INT /* 로그에 기록할 전체 삭제 건수 */

	/* TEMP TABLE 존재하면 날리고 재생성 */
	IF OBJECT_ID(N'tempdb..#TB_M_JOB_DeleteData_T', 'U') IS NOT NULL
		DROP TABLE #TB_M_JOB_DeleteData_T;
    
	CREATE TABLE #TB_M_JOB_DeleteData_T (TRG_TB VARCHAR(30), INST_ID INT, TRG_DT VARCHAR(12)) -- sql_text NVARCHAR(2048)

	/* 보관주기 정책 TEMP TABLE에 INSERT */
	INSERT INTO #TB_M_JOB_DeleteData_T
	SELECT 'TBL2_M_'+CollectItem AS TRG_TB
		 , InstanceID AS INST_ID
		 , CASE WHEN (CollectItem LIKE 'AgentJob%' OR CollectItem = 'ServerActivity' OR CollectItem LIKE 'TopQueriesBy%') THEN CONVERT(VARCHAR(10), DATEADD(DAY, -RetentionMonth, GETDATE()), 121) 
					   ELSE CONVERT(VARCHAR(10), DATEADD(MONTH, -RetentionMonth,GETDATE()), 121) 
				   END AS TRG_DT
	  FROM dbo.META2_M_ScheduleInfo WITH(NOLOCK)
	-- SELECT * FROM @InstanceList 
	
    BEGIN TRY 
	    /* CURSOR 선언*/ 
        DECLARE CURSOR_JOB_DeleteData CURSOR FOR
            SELECT TRG_TB, INST_ID, TRG_DT
              FROM #TB_M_JOB_DeleteData_T
        OPEN CURSOR_JOB_DeleteData
        
		/* CURSOR FETCH */
        FETCH NEXT FROM CURSOR_JOB_DeleteData INTO @TRG_TB, @INST_ID, @TRG_DT
        
		/* FETCH 대상이 더이상 존재하지 않을때 까지 LOOP */
		WHILE (@@FETCH_STATUS <> -1)
        BEGIN
		    /* 1번째 DELETE는 무조건 실행하게 하기 위해 ROWS=1로 세팅 */
			SET @LOG_TRG_DT = REPLACE(@TRG_DT,'-','')
			SET @LOG_PART_NM = CONVERT(VARCHAR,@INST_ID)
			SET @DEL_TOT_CNT = 0
			EXEC usp_db_work_log @pJOBDT = @LOG_TRG_DT, @pJOBID = 'USP2_M_JOB_DeleteData', @pTABLE = @TRG_TB, @pPARTITION = @LOG_PART_NM, @pPROCGBN = 'S'
            SET @ROWS = @DEL_TRG_CNT
            SET @SQL_TEXT = 'WHILE (@ROWS = @DEL_TRG_CNT)
            BEGIN
            DELETE TOP (@DEL_TRG_CNT) FROM ' + @TRG_TB + ' 
			WHERE instanceid = @INST_ID
            AND CollectDate < @TRG_DT 
            
            SET @ROWS = @@ROWCOUNT
			SET @DEL_TOT_CNT = @DEL_TOT_CNT + @ROWS
			PRINT(@ROWS)
			PRINT(@INST_ID)
			PRINT(@DEL_TOT_CNT)
			PRINT(@@ROWCOUNT)
            END'

			/* 쿼리 문제 발생시 확인 목적 */
            -- PRINT (@SQL_TEXT)
            
			EXEC sp_executesql @SQL_TEXT, N'@DEL_TRG_CNT INT, @ROWS INT, @INST_ID INT, @TRG_DT VARCHAR(10), @DEL_TOT_CNT INT OUTPUT'
				, @DEL_TRG_CNT = @DEL_TRG_CNT
				, @ROWS = @ROWS
				, @INST_ID = @INST_ID
				, @TRG_DT = @TRG_DT
				, @DEL_TOT_CNT = @DEL_TOT_CNT OUTPUT
			
			EXEC usp_db_work_log @pJOBDT = @LOG_TRG_DT, @pJOBID = 'USP2_M_JOB_DeleteData', @pTABLE = @TRG_TB, @pPARTITION = @LOG_PART_NM, @pPROCGBN = 'F', @pCNT = @DEL_TOT_CNT
			/* 다음 CURSOR FETCH */
			FETCH NEXT FROM CURSOR_JOB_DeleteData INTO @TRG_TB, @INST_ID, @TRG_DT
        END

		BEGIN
		    CLOSE CURSOR_JOB_DeleteData
			DEALLOCATE CURSOR_JOB_DeleteData
		END
    END TRY

    BEGIN CATCH
        DECLARE @ErrorMessage NVARCHAR(4000);
        DECLARE @ErrorSeverity INT;
        DECLARE @ErrorState INT;

        SELECT @ErrorMessage = ERROR_MESSAGE(), @ErrorSeverity = ERROR_SEVERITY(), @ErrorState = ERROR_STATE();

        RAISERROR (@ErrorMessage, @ErrorSeverity, @ErrorState);
		EXEC usp_db_work_log @pJOBDT = @LOG_TRG_DT, @pJOBID = 'USP2_M_JOB_DeleteData', @pTABLE = @TRG_TB, @pPARTITION = @LOG_PART_NM, @pPROCGBN = 'E', @pCONTENT = @ErrorMessage

    END CATCH
END