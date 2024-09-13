
-- =============================================
-- Author: jyh
-- Create date: 2022.02.08
-- Description: DATA RETENTION BATCH
-- Exaple : EXEC usp_db_work_log '20220209', 'usp_db_work_log', 'TB_DB_WRK_LOG', '', 'S', '', CONVERT(VARCHAR,GETDATE(),112)
-- =============================================
CREATE PROCEDURE [dbo].[usp_db_work_log]
    @pJOBDT     varchar(8)   = NULL,   /* (작업일자) */
    @pJOBID     varchar(30)  = NULL,   /* (작업ID)   */
    @pTABLE     varchar(30)  = NULL,   /* 테이블명   */
    @pPARTITION varchar(30)  = NULL,   /* 파티션명   */
    @pPROCGBN   varchar(1)   = NULL,   /* (진행구분-S:시작,C:작업중,E:ERROR,F:종료) */
    @pCONTENT   varchar(500) = NULL,   /* (에러내역) */
    @pEXEDT     varchar(8)   = NULL,   /* (실행일자) */
    @pCNT       int          = NULL    /* (실행일자) */
AS
BEGIN
SET NOCOUNT ON
SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED 
/****************************************************************************/
/*  PROCEDURE NAME  :  PR_DB_WRK_LOG                                        */
/*  CONTENT         :  각종 에러내역 LOG                                    */
/*  VERSION         :  1.0                                                  */
/****************************************************************************/
declare @vCNT       int,
        @vERRMSG    varchar(4000)  = '에러로그',
        @PROCID     varchar(50)    = 'usp_db_work_log',
        @vEXEDT     varchar(8)     = NULL,
        @vPARTITION varchar(30)    = NULL

set @vERRMSG = '에러로그'
set @PROCID  = 'usp_db_work_log'

 set @vEXEDT = CONVERT(VARCHAR,GETDATE(),112)
 IF isnull(@pEXEDT,'Z') <> 'Z' 
    set @vEXEDT = @pEXEDT; 
 --END
 
 set @vPARTITION =  'NORMAL'
 IF @pPARTITION IS NOT NULL 
    set @vPARTITION = @pPARTITION;
 --END

 /*(0.기존 LOG SELECT)*/
 SELECT @vCNT = COUNT(1) 
   FROM TB_DB_WRK_LOG
  WHERE JOB_DT         = @pJOBDT
    AND JOB_ID         = @pJOBID
    AND TABLE_NAME     = @pTABLE
    AND PARTITION_NAME = @vPARTITION
    AND EXEC_DT        = @vEXEDT

--PRINT(@vCNT)

 /*(1.LOG 추가)*/
 IF @vCNT = 0 AND @pPROCGBN = 'S' 
    BEGIN
      INSERT INTO TB_DB_WRK_LOG
         (JOB_DT,                -- (작업일자 )
          EXEC_DT,               -- (실행일자 )
          JOB_ID,                -- (작업ID   )
          TABLE_NAME,            -- 테이블명
          PARTITION_NAME,        -- 파티션명
          STR_TIME,              -- (시작시간 )
          END_TIME,              -- (종료시간 )
          PROC_GBN,              -- (진행구분 )
          CONTENT)               -- (에러상세 )
      VALUES
         (@pJOBDT,                -- (작업일자 )
          @vEXEDT,                -- (실행일자 )
          @pJOBID,                -- (작업ID   )
          @pTABLE,                -- 테이블명
          @vPARTITION,            -- 파티션명
          CASE WHEN @pPROCGBN  = 'S' THEN getdate() END, -- (시작시간 )
          NULL,                  -- (종료시간 )
          @pPROCGBN,              -- (진행구분 )
          @pCONTENT)              -- (에러상세 )
    END
      
 /*(1.LOG 수정)*/
 ELSE
    BEGIN
      UPDATE TB_DB_WRK_LOG
         SET STR_TIME       = CASE WHEN @pPROCGBN  = 'S'  THEN getdate() ELSE STR_TIME END,
             END_TIME       = CASE WHEN @pPROCGBN <> 'S'  THEN getdate() ELSE NULL END,
             PROC_GBN       = @pPROCGBN,
             CONTENT        = CASE WHEN @pCONTENT IS NULL THEN CONTENT ELSE SUBSTRING(ISNULL(CONTENT,'') + ISNULL(@pCONTENT,''), 1,3000) END,
             CNT            = @pCNT
       WHERE JOB_DT         = @pJOBDT
         AND EXEC_DT        = @vEXEDT
         AND JOB_ID         = @pJOBID
         AND TABLE_NAME     = @pTABLE
         AND PARTITION_NAME = @vPARTITION
    END
 --END

END;