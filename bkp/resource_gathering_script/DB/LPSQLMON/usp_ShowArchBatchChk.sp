
-- =============================================
-- Author:		jyh
-- Create date: 2020.02.14
-- Description:	아카이브 배치 정상 처리 확인
-- =============================================
CREATE PROCEDURE [dbo].[usp_ShowArchBatchChk]
	-- Add the parameters for the stored procedure here
	
AS
BEGIN
	-- SET NOCOUNT ON added to prevent extra result sets from
	-- interfering with SELECT statements.
	SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
	SET NOCOUNT ON;
	-- SET ANSI_WARNINGS OFF;
	/* 쿼리 몸체 */
	SELECT '아카이빙' GBN, COUNT(1) DATA_TRMS_CHK
      FROM OPENROWSET('SQLOLEDB', '10.7.17.106,1433';'lpdbadmin';'Tltmxpa12!', 
       'SELECT WRK_DTMV, PGM_NM, PGM_EXEC_TM_VAL, SRCE_ETCT_QTY, LOAD_QTY, SRCE_ETCT_QTY-LOAD_QTY AS GAP
          FROM LDSPSALE_ARC.dbo.ETL_JOB_LOG with (nolock)
         WHERE WRK_DTMV=CONVERT(CHAR(8), GETDATE(),112)'
      ) A
     WHERE GAP<>0
	/* 쿼리 몸체 */
END
