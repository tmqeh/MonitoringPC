


-- =============================================
-- Author:  jyh
-- Create date: 2021.08.30
-- Description: for Grafana Variables 

-- format : 
--         1) row : MSSSQL 월간 레포트(CPU, MEMORY, DISK) 파트별 서버 리스트 생성
--         2) list : 레포트 생성 시 피벗을 위해 작성했으나 미사용으로 추정
--         3) array : 레포트 생성 시 피벗을 위해 작성했으나 미사용으로 추정

-- Modify : 
--			USE = 'Y' 인 것들만 인서트, 중복 제거 (2022.12.20 ljs)

/*
 @PartName 값의 NULL 분기 처리가 필요 없는 이유
 : 항상 1개 이상의 값이 선택되기 때문 (ALL 선택시엔, NULL이 아닌 전체 대상이 선택된다)
*/

-- =============================================
CREATE PROCEDURE [dbo].[usp_get_DBA_Target_Svr]
(
   @format      NVARCHAR(128) = 'row'
   ,@PartName   NVARCHAR(128) = ''
)
AS
BEGIN
    IF @format IS NULL or @format = 'row'
    BEGIN

      CREATE TABLE #tempServerName (ServerName varchar(30))
      
      IF @PartName LIKE '%POS%'

         BEGIN

            INSERT INTO #tempServerName(ServerName)
            SELECT ServerName
            FROM META2_M_InstanceInfo 
            WHERE ServerName IN (
                        '[POS] AMS',             --  2
                        '[POS] SCOM',            -- 11
                        '[POS] 동기화',          --  5
                        '[POS] 매출',            --  7
                        '[POS] 푸드키오스크1',  --  4
                        '[POS] 푸드키오스크2',  --  6
                        '[POS] AND',           -- 52
						'[POS] (구)전자저널',	 -- 9
						'[POS] 아카이브'           -- 12
                            )
			AND UseYN = 'Y'
         END

      IF @PartName LIKE '%상품권%'

         BEGIN

            INSERT INTO #tempServerName(ServerName)
            SELECT ServerName
            FROM META2_M_InstanceInfo 
            WHERE ServerName IN (
                        '[상품권] 상품권'        -- 13
                            )
			AND UseYN = 'Y'
         END

      IF @PartName LIKE '%MD%'

         BEGIN

            INSERT INTO #tempServerName(ServerName)
            SELECT ServerName
            FROM META2_M_InstanceInfo 
            WHERE ServerName IN (
                        ''
                            )
			AND UseYN = 'Y'
         END

      IF @PartName LIKE '%마케팅%'

         BEGIN

            INSERT INTO #tempServerName(ServerName)
            SELECT ServerName
            FROM META2_M_InstanceInfo 
            WHERE ServerName IN (
                        '[마케팅] (신)사은',     -- 39
                        '[마케팅] (신)에누리',   -- 50
						'[마케팅] (신)문화센터', -- 79
                        '[마케팅] 법인영업'      -- 21
                            )
			AND UseYN = 'Y'
         END

      IF @PartName LIKE '%인프라%'

         BEGIN

            INSERT INTO #tempServerName(ServerName)
            SELECT ServerName
            FROM META2_M_InstanceInfo 
            WHERE ServerName IN (
                        '[인프라] DRM',          -- 51                             
                        '[인프라] SCCM',         -- 54
						'[인프라] TCOStream'     -- 90
                            )
			AND UseYN = 'Y'
         END

      IF @PartName LIKE '%경영지원%'

         BEGIN

            INSERT INTO #tempServerName(ServerName)
            SELECT ServerName
            FROM META2_M_InstanceInfo 
            WHERE ServerName IN (
                        '[경영지원] IM',         -- 24
                        '[경영지원] 동료사원',   -- 27
                        '[경영지원] 전자결재'    -- 48
                            )
			AND UseYN = 'Y'
         END

      IF @PartName LIKE '%재무%'

         BEGIN

            INSERT INTO #tempServerName(ServerName)
            SELECT ServerName
            FROM META2_M_InstanceInfo 
            WHERE ServerName IN (
                        '[재무] 증빙',          -- 15
                        '[재무] 내부회계',      -- 16
                        '[재무] 통합구매',      -- 57
                        '[재무] 재무통합',      -- 55
                        '[재무] EAI'            -- 56
                            )
			AND UseYN = 'Y'
         END

      IF @PartName = '' -- PartName 없는 대시보드 All 변수 활용 목적

         BEGIN

            INSERT INTO #tempServerName(ServerName)
            SELECT ServerName
            FROM META2_M_InstanceInfo 
            WHERE ServerName IN (                              
                              '[POS] AMS',             --  2
                              '[POS] SCOM',            -- 11
                              '[POS] 동기화',          --  5
                              '[POS] 매출',            --  7
                              '[POS] 푸드키오스크1',   --  4
                              '[POS] 푸드키오스크2',   --  6
							  '[POS]아카이브',         -- 12
                              '[마케팅] (신)사은',     -- 39
                              '[마케팅] (신)에누리',   -- 50
							  '[마케팅] (신)문화센터', -- 79
                              '[인프라] DRM',          -- 51
							  '[인프라] TCOStream',    -- 90
                              '[POS] AND',             -- 52
                              '[인프라] SCCM',         -- 54
                              '[상품권] 상품권',       -- 13
                              --'[마케팅] 문화센터',   -- 20
                              '[경영지원] IM',         -- 24
                              '[경영지원] 동료사원',   -- 27
                              '[경영지원] 전자결재',   -- 48
                              '[마케팅] 법인영업',     -- 21
                              '[재무] 증빙',           -- 15
                              '[재무] 내부회계',       -- 16
                              '[재무] 통합구매',       -- 57
                              '[재무] 재무통합',       -- 55
                              '[재무] EAI'             -- 56
                              )
			AND UseYN = 'Y'
         END

      SELECT   ServerName
      FROM   #tempServerName

	  DROP TABLE #tempServerName

    END

    ELSE IF @format = 'list' or @format = 'array'
    BEGIN
        SELECT stuff((select ',' + '''' + Servername + '''' 
		FROM META2_M_InstanceInfo 
		WHERE ServerName IN ( '[POS] AMS',           --  2
                              '[POS] SCOM',            -- 11
                              '[POS] 동기화',          --  5
                              '[POS] 매출',            --  7
                              '[POS] 푸드키오스크1',  --  4
                              '[POS] 푸드키오스크2',  --  6
							  '[POS]아카이브',         -- 12
                              '[마케팅] (신)사은',     -- 39
                              '[마케팅] (신)에누리',   -- 50
							  '[마케팅] (신)문화센터', -- 79
                              '[인프라] DRM',          -- 51
                              '[POS] AND',           -- 52
                              '[인프라] SCCM',         -- 54
							  '[인프라] TCOStream',    -- 90
                              '[상품권] 상품권',       -- 13
                              --'[마케팅] 문화센터',     -- 20
                              '[경영지원] IM',         -- 24
                              '[경영지원] 동료사원',   -- 27
                              '[경영지원] 전자결재',   -- 48
                              '[마케팅] 법인영업',     -- 21
                              '[재무] 증빙',           -- 15
                              '[재무] 내부회계',       -- 16
                              '[재무] 통합구매',       -- 57
                              '[재무] 재무통합',       -- 55
                              '[재무] EAI'             -- 56
         )
		 AND UseYN = 'Y' 
		 for xml path('')), 1, 1, '');
    END
END
