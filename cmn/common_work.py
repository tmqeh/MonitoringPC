# common & configuration
from cmn.common import get_cur_func_nm as func_nm
from cmn.common_db import workDB
from cmn.common_datetime import YMD



# 영업일 체크 : 책임당직이 없을 경우로 판단
def check_working_day(args=YMD):
    try :
      conn = workDB(func_nm())

      # SQL 호출
      sqlTxt = """SELECT TOP 1 1
                    FROM SCHEDULE A
                   WHERE DATEADD(DAY, +0, GETDATE()) BETWEEN STARTDATE AND ENDDATE
                     AND CONTENT = '주말근무'
               """ 
      #print(sqlTxt)
      conn.execute(sqlTxt)
      result = conn.fetchone()    

      conn.close()
      return result[0]
    
    except Exception as e:
       print(e)
       return None


# 영업일 체크 : 책임당직이 없을 경우로 판단
def check_working_day_start():
    conn = workDB()

    # SQL 호출
    sqlTxt = """
                 WITH dummy_DT as (
                        -- 근태 공백 제거를 위한 날짜 더미 테이블 (재귀 사용)
                        SELECT GETDATE()-6 as DT_DATE, CONVERT(VARCHAR, GETDATE()-6, 112) as DT, DATEPART(WEEK, getdate()-6) WK 
                        UNION ALL
                        SELECT DATEADD(DAY, 1, DT_DATE) as DT_DATE, CONVERT(VARCHAR, DATEADD(DAY, 1, DT_DATE), 112) as DT, DATEPART(WEEK, DATEADD(DAY, 1, DT_DATE))
                          FROM dummy_DT
                         WHERE DT_DATE < GETDATE()-6+14-1
                        ),
                        holyday_CHK as (
                      -- 책임당직 유무를 통해 휴일인지 확인 (명절 당일에는 책임당직이 없으므로 체크 로직 추가 필요)
                       SELECT Z.DT
                         FROM SCHEDULE A, MEMBER B, dummy_DT Z
                        WHERE B.GRADE = 2 
                          AND B.ID = A.MEMBERID
                          AND DATEADD(DAY, +0, z.DT_DATE) BETWEEN STARTDATE AND ENDDATE
                          AND CONTENT = '책임당직'
                        )
                        SELECT COUNT(1)
                        FROM (
                        SELECT A.DT,  CASE WHEN WK = DATEPART(WEEK, getdate()) THEN 'SAME_WEEK' ELSE NULL END as WEEK_CHK
                        , RANK() OVER(PARTITION BY WK ORDER BY DT) as FIRST_DT_CHK
                        FROM dummy_DT A
                        WHERE NOT EXISTS(SELECT 1 FROM holyday_CHK X WHERE  X.DT = A.DT)
                        ) A
                        WHERE WEEK_CHK = 'SAME_WEEK'
                        AND A.DT = CONVERT(VARCHAR,GETDATE(),112)
                        AND FIRST_DT_CHK = 1
                """ 
    # print(sqlTxt)    
    conn.execute(sqlTxt)
    result = conn.fetchone()
    # print(result)
    conn.close()
    return result[0]