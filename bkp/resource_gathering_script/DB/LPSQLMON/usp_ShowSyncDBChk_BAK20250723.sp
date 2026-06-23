
-- =============================================
-- Author:		홍윤표
-- Create date: 2020.03.11
-- Description:	동기화 DB 점검
-- =============================================
CREATE PROCEDURE [dbo].[usp_ShowSyncDBChk_BAK20250723]
	-- Add the parameters for the stored procedure here

AS
BEGIN
	-- SET NOCOUNT ON added to prevent extra result sets from
	-- interfering with SELECT statements.
	SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
	SET NOCOUNT ON;
	-- SET ANSI_WARNINGS OFF;
	/* 쿼리 몸체 */
	SELECT warning                    AS PUB_WARN
		 , publisher_db               AS PUB_DB
         , publication                AS PUB_NM
         , status                     AS PUB_STAT         
         , last_distsync              AS PUB_LAST_TIME
      FROM OPENROWSET('SQLOLEDB', '10.7.17.142,2001';'lpdbadmin';'lottedb_syn00', 
       'exec [dbo].[usp_ShowRepMonitoring]'
      ) A
	/* 쿼리 몸체 */
END