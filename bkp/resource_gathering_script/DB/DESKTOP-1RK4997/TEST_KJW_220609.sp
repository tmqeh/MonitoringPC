-- =============================================
-- Author:		<Author,,Name>
-- Create date: <Create Date,,>
-- Description:	<Description,,>
-- =============================================
CREATE PROCEDURE [dbo].[TEST_KJW_220609]
	-- Add the parameters for the stored procedure here
	--<@Param1, sysname, @p1> <Datatype_For_Param1, , int> = <Default_Value_For_Param1, , 0>, 
	--<@Param2, sysname, @p2> <Datatype_For_Param2, , int> = <Default_Value_For_Param2, , 0>

	@V_COLLECTDT    varchar(255)

AS
BEGIN
	-- SET NOCOUNT ON added to prevent extra result sets from
	-- interfering with SELECT statements.
	SET NOCOUNT ON;

    declare @V_TASKNAME		varchar(255)            
            

/****** SSMS의 SelectTopNRows 명령 스크립트 ******/
SELECT TOP (1)
       @V_TASKNAME = Task_Name
  FROM [MonitoringDB].[dbo].[TB_Dms_Rsrc_L] WITH(NOLOCK)
  WHERE CollectDT = @V_COLLECTDT
  AND	Rsrc_Name = 'CDCChangesDiskTarget'
  AND	CollectDTM = '2022-06-05 00:01:00.000';

  PRINT (@V_TASKNAME + '220609_KJW');

END
