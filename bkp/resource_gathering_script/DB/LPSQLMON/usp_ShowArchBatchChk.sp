
-- =============================================
-- Author:		jyh
-- Create date: 2020.02.14
-- Description:	아카이브 배치 정상 처리 확인
-- Modify :	파라미터 입력시 날짜 지정, 날짜 파라미터 추가
-- Execute : EXEC usp_ShowArchBatchChk '20250721'
-- =============================================
CREATE PROCEDURE [dbo].[usp_ShowArchBatchChk]
	@in_DATE		VARCHAR(8) = ''
AS
BEGIN

	SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
	SET NOCOUNT ON;

	IF ISDATE(@in_DATE) = 1			-- 날짜가 들어오면 해당 날짜로 조회
	BEGIN
		DECLARE @nSQL NVARCHAR(MAX) = ''
		SET @nSQL = '

		SELECT 
			''아카이빙'' GBN
			, COUNT(1) DATA_TRMS_CHK
		FROM OPENROWSET(
			''SQLOLEDB''
			, ''10.7.17.106,1433'';''lpdbadmin'';''Tltmxpa12!''
			, ''SELECT 
					WRK_DTMV
					, PGM_NM
					, PGM_EXEC_TM_VAL
					, SRCE_ETCT_QTY
					, LOAD_QTY
					, SRCE_ETCT_QTY-LOAD_QTY AS GAP
				FROM LDSPSALE_ARC.dbo.ETL_JOB_LOG WITH(NOLOCK)
				WHERE WRK_DTMV = ''''' + CONVERT(VARCHAR(8), CONVERT(DATE, @in_DATE),112) + ''''' ''
		) A
		WHERE GAP <> 0 '
		
--		PRINT @nSQL
		EXEC sp_executesql @nSQL
	END
	ELSE
		SELECT 
			'아카이빙' GBN
			, COUNT(1) DATA_TRMS_CHK
		FROM OPENROWSET(
			'SQLOLEDB'
			, '10.7.17.106,1433';'lpdbadmin';'Tltmxpa12!'
			, '	SELECT 
					WRK_DTMV
					, PGM_NM
					, PGM_EXEC_TM_VAL
					, SRCE_ETCT_QTY
					, LOAD_QTY
					, SRCE_ETCT_QTY-LOAD_QTY AS GAP
				FROM LDSPSALE_ARC.dbo.ETL_JOB_LOG WITH(NOLOCK)
				WHERE WRK_DTMV = CONVERT(VARCHAR(8), GETDATE(),112)'
		) A
		WHERE GAP <> 0
END
