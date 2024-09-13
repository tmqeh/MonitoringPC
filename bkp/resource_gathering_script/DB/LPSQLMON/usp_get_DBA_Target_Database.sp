


-- =============================================
-- Author:  KJW
-- Create date: 2023.07.06
-- Description: for Grafana Variables 

-- format : 
--         1) row : MSSSQL 월간 레포트(CPU, MEMORY, DISK) 파트별 서버 리스트 생성
--         2) list : 레포트 생성 시 피벗을 위해 작성했으나 미사용으로 추정
--         3) array : 레포트 생성 시 피벗을 위해 작성했으나 미사용으로 추정

-- Modify : 
--			USE = 'Y' 인 것들만 인서트, 중복 제거 (2022.12.20 ljs)

/*
 @ServerName 값의 NULL 분기 처리가 필요 없는 이유
 : 항상 1개 이상의 값이 선택되기 때문 (ALL 선택시엔, NULL이 아닌 전체 대상이 선택된다)
*/

-- =============================================
CREATE PROCEDURE [dbo].[usp_get_DBA_Target_Database]
(
    @format       NVARCHAR(128) = 'row'
   ,@ServerName   NVARCHAR(128) = ''
)
AS
BEGIN
    IF @format IS NULL or @format = 'row'
    BEGIN

      CREATE TABLE #tempDatabaseName (
	                                  DatabaseName varchar(30)
									 ,database_id int
									 )

         BEGIN
			INSERT INTO #tempDatabaseName (DatabaseName, database_id)
            SELECT T1.name
				  ,T1.database_id
            FROM   TBL2_M_DatabaseInfo T1
                  ,META2_M_InstanceInfo T2
            WHERE  1=1
            AND    T1.CollectDate >= CONVERT(VARCHAR(10), GETDATE(), 121)
            AND    T1.name NOT IN ('master', 'msdb', 'tempdb', 'model')
            --T2
            AND    T1.InstanceID = T2.InstanceID
            AND    T2.ServerName = @ServerName			
         END

      SELECT DatabaseName
      FROM   #tempDatabaseName
	  ORDER BY database_id

	  DROP TABLE #tempDatabaseName

    END
END
