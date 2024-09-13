
-- =============================================
-- Author:  jyh
-- Create date: 2021.08.30
-- Description: for Grafana Variables 
-- =============================================
CREATE PROCEDURE [dbo].[usp_get_DBA_Target_Svr_KJW] 
(
	@format		NVARCHAR(128) = 'row'
   ,@PartName	NVARCHAR(128) = ''
)
AS
BEGIN
    IF @format IS NULL or @format = 'row'
    BEGIN
		SELECT T1.ServerName
		  FROM (
				SELECT ServerName
				FROM META2_M_InstanceInfo 
				WHERE ServerName IN ('[MD]아카이브',          -- 12
									  '[POS] AMS#1',           --  2
									  '[POS] AMS#2',           --  8
									  '[POS] SCOM',            -- 11
									  '[POS] 동기화',          --  5
									  '[POS] 매출',            --  7
									  '[POS] 푸드키오스크#1',  --  4
									  '[POS] 푸드키오스크#2',  --  6
									  '[마케팅] (신)사은',     -- 39
									  '[마케팅] (신)에누리',   -- 50
									  '[인프라] DRM',          -- 51
									  '[POS] AND#1',           -- 52
									  '[POS] AND#2',           -- 53
									  '[인프라] SCCM',         -- 54
									  '[상품권] 상품권',	   -- 13
									  '[마케팅] 문화센터',	   -- 20
									  '[경영지원] IM',		   -- 24
									  '[경영지원] 동료사원',   -- 27
									  '[경영지원] 전자결재',   -- 48
									  '[마케팅] 법인영업',	   -- 21
									  '[재무] 증빙',		   -- 15
									  '[재무] 내부회계',	   -- 16
									  '[재무] 통합구매',	   -- 49
									  '[재무] 재무통합',	   -- 55
									  '[재무] EAI'			   -- 56
									)
				) T1
		WHERE	T1.ServerName LIKE '%' + @PartName + '%'
    END

    ELSE IF @format = 'list' or @format = 'array'
    BEGIN
        SELECT stuff((select ',' + '''' + Servername + '''' 
          FROM META2_M_InstanceInfo 
         WHERE ServerName IN ('[MD]아카이브',          -- 12
                              '[POS] AMS#1',           --  2
                              '[POS] AMS#2',           --  8
                              '[POS] SCOM',            -- 11
                              '[POS] 동기화',          --  5
                              '[POS] 매출',            --  7
                              '[POS] 푸드키오스크#1',  --  4
                              '[POS] 푸드키오스크#2',  --  6
                              '[마케팅] (신)사은',     -- 39
                              '[마케팅] (신)에누리',   -- 50
                              '[인프라] DRM',          -- 51
                              '[POS] AND#1',           -- 52
                              '[POS] AND#2',           -- 53
                              '[인프라] SCCM',         -- 54
							  '[상품권] 상품권',	   -- 13
							  '[마케팅] 문화센터',	   -- 20
							  '[경영지원] IM',		   -- 24
							  '[경영지원] 동료사원',   -- 27
							  '[경영지원] 전자결재',   -- 48
							  '[마케팅] 법인영업',	   -- 21
							  '[재무] 증빙',		   -- 15
							  '[재무] 내부회계',	   -- 16
							  '[재무] 구매',		   -- 49
							  '[재무] 재무통합',	   -- 55
							  '[재무] EAI'			   -- 56
         ) for xml path('')), 1, 1, '');
    END
END
