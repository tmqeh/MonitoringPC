import datetime

# common & configuration
import cmn.common_msgr as msgr
from cmn.common import get_cur_func_nm as func_nm, get_cur_file_nm as file_nm, get_func_tree as func_tree
from cmn.common_db import psysql, monDB, monPC, maxgDB, metaDB, batDB
from cmn.common_datetime import YMDHH24MISS


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------        
def list_ora_err(args=YMDHH24MISS):
    print("ORAError " + args)
    # postgresql (maxg)

    try:
        conn = None
        conn = maxgDB(func_nm())
        sqlTxt = ""
        
        inst_list = ["lpsis1","lpsis2","lottehrs1","lottehrs2"]

        for target in inst_list :

            # SQL 호출
            # whereas in Python single quotes can be left unescaped if the string is delimited by double quotes.
            # e.g) "{}" => "lpsis1", {} => "lpsis1"
            sqlTxt = psysql.SQL(""" SELECT time, '{}' as inst_id, value as err_detail
                                  FROM {}.{} Z
                                  WHERE TIME >= '{}'
                                  AND VALUE NOT LIKE '%KILL SESSION%'
                                  AND VALUE NOT LIKE '%aborting process unknown ospid%'
                                  AND VALUE NOT LIKE '%ORA-01013%'
                                  AND VALUE NOT LIKE '%SQL Analyze time limit interrupt%' """).format(
                              psysql.Identifier(target),
                              psysql.Identifier(target),
                              psysql.Identifier("ora_alertlog_history"),
                              psysql.Identifier(args)
                          )

            # print(sqlTxt)
            data = conn.query(sqlTxt)

            if conn.rows() > 0:
                result = [dict((conn.description()[i][0], value) \
                                for i, value in enumerate(row)) for row in data]
                
                content=""
                for sms_txt in result :
                    content = content + "일시 : " + sms_txt["time"].strftime("%Y-%m-%d %H:%M:%S") + "\n"
                    content = content + "서버 : " + sms_txt["inst_id"] + "\n"
                    content = content + "내용 : \n```\n" + sms_txt["err_detail"] + "\n```"
                    # print(content)
                    # msgr.put_msgr_target(content, "DB0001")
                    msgr.put_msgr_target(content, grp_cd="DB0003", send_title="**" + func_nm() + "**", msgr_color="RED")
                    
                    content="\n"

    except Exception as e:
        # print(func_nm() + ": " + str(e))
        msgr.put_msgr_target(func_tree() + ":\n" + str(e), grp_cd="DB9993", send_title="**" + func_nm() + "**", msgr_color="RED")
        
    finally:
        if conn:
            conn.close()


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def list_ms_err(args=YMDHH24MISS):
    print("MSError " + args)

    try:
        # DB 기본 접속 정보
        conn  = None
        conn2 = None
        conn3 = None
        conn  = monDB()
        conn2 = monDB()
        conn3 = monDB()

        sqlTxt = ""
        sqlTxt2 = ""
        sqlTxt3= ""

        # SQL 호출
        sqlTxt = """/* [상세] Agent Job 실패 목록 */
                    SELECT A.InstanceID, A.ServerName
                         , B.JobName
                         , B.LastRunDateTime
                         , B.LastRunStatusMessage
                         , B.NextRunDateTime, B.CollectDate
                      FROM META2_M_InstanceInfo AS A with (nolock)
                     CROSS APPLY (SELECT B.JobName
                                       , B.LastRunDateTime
                                       , B.LastRunStatusMessage
                                       , B.NextRunDateTime, B.CollectDate
                                    FROM (SELECT ROW_NUMBER()OVER(PARTITION BY B.LastRunDateTime ORDER BY CollectDate ASC) AS ROWNUM
                                               , B.JobName
                                               , B.LastRunDateTime
                                               , B.LastRunStatusMessage
                                               , B.NextRunDateTime, B.CollectDate
                                            FROM [dbo].[TBL2_M_AgentJobInfo] AS B with (nolock)
                                           WHERE A.InstanceID = B.InstanceID
                                             AND B.CollectDate  >= '{}' -- 날짜 부분 변수로 들어 갈 수 있도록
                                             AND B.Enabled = 'Y'
                                             AND B.LastRunStatus in ('Failed','Warnig')
                                         ) B
                                    WHERE B.ROWNUM = 1
                                   ) B
                     WHERE A.UseYN = 'Y'
                       AND A.InstanceID  IN (2, 4, 5, 6, 7, 8, 11, 12, 13, 15, 16, 21, 24, 27, 39, 48, 50, 51, 52, 53, 54, 55, 56, 57, 79)
                       AND A.InstanceID <> 1
                       -- 20240401 jyh 추가
                       AND B.JobName not like '%SQLServerMonitor%'
                       AND B.CollectDate  >= '{}' -- 날짜 부분 변수로 들어 갈 수 있도록  """.format(args[0:10],args)

        sqlTxt2 = """/* [상세] SQL Error log 목록 */
                    SELECT distinct A.InstanceID, A.ServerName
                        , dateadd(millisecond, -datepart(millisecond, B.CollectDate), B.CollectDate) as CollectDate
                        , dateadd(millisecond, -datepart(millisecond, B.LOG_DATE), B.LOG_DATE) as LOG_DATE
                        , B.PROCESS_INFO, B.ERRORLOG_TEXT
                    FROM [META2_M_InstanceInfo] AS A with (nolock)
                    INNER JOIN [dbo].[TBL2_M_SqlErrorlog] AS B with (nolock)
                        ON A.InstanceID = B.InstanceID
                    WHERE CollectDate >= '{}' -- 날짜 부분 변수로 들어 갈 수 있도록
                        -- AND DATEDIFF(MI, B.LOG_DATE, B.CollectDate) < 1500 -- 하루에 한번만 수집, 수집할때 전체 수집하는걸로
                        AND PROCESS_INFO NOT IN ('Logon', '로그온', 'Backup', '백업')
                        AND (ERRORLOG_TEXT LIKE '%error%' OR ERRORLOG_TEXT LIKE '%failed%')
                        AND (ERRORLOG_TEXT NOT LIKE '%Logging SQL Server messages in file%'
                        AND ERRORLOG_TEXT NOT LIKE '%The error log has been reinitialized. See the previous log for older entries.%'
                        AND ERRORLOG_TEXT NOT LIKE 'Attempting to cycle%')
                        AND A.InstanceID  IN (2, 4, 5, 6, 7, 8, 11, 12, 13, 15, 16, 21, 24, 27, 39, 48, 50, 51, 52, 53, 54, 55, 56, 57, 79)
                    ORDER BY A.InstanceID, LOG_DATE DESC """.format(args)

        sqlTxt3 = """/* [실시간] 락모니터링 추가 */
                     SELECT Z.[수집시간], Z.[시스템명], Z.[락지속시간(s)], Z.[인스턴스ID]
                          , X.[타입],     X.[대기정보], X.[오브젝트명],    X.[시작시간],  X.[호스트명]
                          , X.[SQL_TEXT]
                          -- , X.수집시간
                      FROM (SELECT [수집시간], [시스템명], [락지속시간(s)], [인스턴스ID]
                              FROM (SELECT CLCT_DTM [수집시간]
                                          , JOB_NM [시스템명]
                                          , ROUND(BLK_TM/1000,0) [락지속시간(s)]
                                          , INST_ID [인스턴스ID]
                                          , ROW_NUMBER() OVER(PARTITION BY JOB_NM ORDER BY CLCT_DTM DESC) RNUM
                                      FROM TB_DAILYREPORT_S with (nolock)
                                      WHERE CLCT_DTM >= '{}'
                                      AND INST_ID IN (2, 4, 5, 6, 7, 8, 11, 12, 13, 15, 16, 21, 24, 27, 39, 48, 50, 51, 52, 53, 54, 55, 56, 57, 79)
                                      -- DRM
                                      -- AND INST_ID NOT IN (51)
                                      -- 1분
                                      AND BLK_TM > 60000
                                      ) Z
                              WHERE RNUM = 1 
                          ) Z 
                      LEFT JOIN (SELECT DISTINCT
                                          A.INSTANCEID AS [인스턴스ID], A.COLLECTDATE AS [수집시간]
                                      , N'BLOCKED' + ' (' + CONVERT(VARCHAR,SESSION_ID) + ' by ' + CONVERT(VARCHAR,A.BLOCKING_SESSION_ID) + ')' AS [타입]
                                      -- , LOGIN_NAME
                                      , REPLACE(REPLACE(REPLACE(REPLACE(WAIT_INFO,CHAR(9),' '),' ','<>'),'><',''),'<>',' ') AS [대기정보]
                                      , OBJECTNAME AS [오브젝트명]
                                      , TRAN_START_TIME AS [시작시간]
                                      , HOST_NAME AS [호스트명]
                                      -- , PROGRAM_NAME
                                      , SUBSTRING(REPLACE(REPLACE(REPLACE(REPLACE(SQL_TEXT,CHAR(9),' '),' ','<>'),'><',''),'<>',' '),1,200) AS [SQL_TEXT]
                                      -- , ROW_NUMBER() OVER (PARTITION BY A.INSTANCEID,  SESSION_ID, OBJECTNAME, TRAN_START_TIME ORDER BY A.COLLECTDATE DESC) AS RNUM
                                      , ROW_NUMBER() OVER (PARTITION BY A.INSTANCEID ORDER BY A.COLLECTDATE DESC) AS RNUM
                                  FROM [DBO].[TBL2_M_WHOISACTIVE] A WITH(NOLOCK)
                                  WHERE 1=1
                                      -- AND A.INSTANCEID = 50
                                      AND A.COLLECTDATE >= '{}'
                                      AND BLOCKING_SESSION_ID <> 0
                                      AND TOTAL_ELAPSED_TIME > 60000
                                  UNION ALL
                                  SELECT DISTINCT
                                      A.INSTANCEID AS [인스턴스ID], A.COLLECTDATE AS [수집시간]
                                      , N'HOLDER' + ' (' + CONVERT(VARCHAR,A.SESSION_ID) + ')' AS [타입]
                                      -- , LOGIN_NAME
                                      , REPLACE(REPLACE(REPLACE(REPLACE(WAIT_INFO,CHAR(9),' '),' ','<>'),'><',''),'<>',' ') AS [대기정보]
                                      , OBJECTNAME AS [오브젝트명]
                                      , TRAN_START_TIME AS [시작시간]
                                      , HOST_NAME AS [호스트명]
                                      -- , PROGRAM_NAME
                                      , SUBSTRING(REPLACE(REPLACE(REPLACE(REPLACE(SQL_TEXT,CHAR(9),' '),' ','<>'),'><',''),'<>',' '),1,200) AS [SQL_TEXT]
                                      -- , ROW_NUMBER() OVER (PARTITION BY A.INSTANCEID,  SESSION_ID, OBJECTNAME, TRAN_START_TIME ORDER BY A.COLLECTDATE DESC) AS RNUM
                                      , ROW_NUMBER() OVER (PARTITION BY A.INSTANCEID ORDER BY A.COLLECTDATE DESC) AS RNUM
                                  FROM [DBO].[TBL2_M_WHOISACTIVE] A WITH(NOLOCK) 
                                  INNER JOIN (SELECT INSTANCEID, COLLECTDATE, SESSION_ID, BLOCKING_SESSION_ID, TOTAL_ELAPSED_TIME
                                              FROM [DBO].[TBL2_M_WHOISACTIVE] A WITH(NOLOCK)
                                              WHERE 1=1
                                              -- AND A.INSTANCEID = 50
                                              AND A.COLLECTDATE >= '{}'
                                              AND BLOCKING_SESSION_ID <> 0
                                              ) B ON A.SESSION_ID = B.BLOCKING_SESSION_ID AND A.COLLECTDATE = B.COLLECTDATE AND A.TOTAL_ELAPSED_TIME < B.TOTAL_ELAPSED_TIME
                                              AND A.INSTANCEID = B.INSTANCEID
                                      WHERE 1=1
                                      -- AND A.INSTANCEID = 50
                                      AND A.COLLECTDATE >= '{}'
                                      AND B.TOTAL_ELAPSED_TIME > 60000
                                  ) AS X
                              ON Z.인스턴스ID = X.인스턴스ID
                              AND X.RNUM = 1
                      ORDER BY Z.[수집시간] DESC, Z.[시스템명], X.[시작시간]""".format(args,args,args,args)
                       
        # print(sqlTxt)
        data = conn.query(sqlTxt)

        if conn.rows() > 0:
            result = [dict((conn.description()[i][0], value) \
                            for i, value in enumerate(row)) for row in data]
            
            content=""
            for sms_txt in result :
                content = content + "일시 : " + sms_txt["LastRunDateTime"].strftime("%Y-%m-%d %H:%M:%S") + "\n"
                content = content + "서버 : " + sms_txt["ServerName"] + "\n"
                content = content + "내용 : \n```\n" + sms_txt["JobName"] + sms_txt["LastRunStatusMessage"] + "\n```"
                # print(content)
                # msgr.put_msgr_target(content, "DB0001")
                msgr.put_msgr_target(content, grp_cd="DB0003", send_title="**" + func_nm() + "**", msgr_color="RED")
                content="\n"

        # print(sqlTxt2)
        data2 = conn2.query(sqlTxt2)

        if conn2.rows() > 0:
            result2 = [dict((conn2.description()[i][0], value) \
                            for i, value in enumerate(row)) for row in data2]
            
            content=""
            for sms_txt2 in result2 :
                content = content + "일시 : " + sms_txt2["LOG_DATE"].strftime("%Y-%m-%d %H:%M:%S") + "\n"
                content = content + "서버 : " + sms_txt2["ServerName"] + "\n"
                content = content + "내용 : \n```\n" + sms_txt2["PROCESS_INFO"] + sms_txt2["ERRORLOG_TEXT"] + "\n```"
                # print(content)
                # msgr.put_msgr_target(content, "DB0001")
                msgr.put_msgr_target(content, grp_cd="DB0003", send_title="**" + func_nm() + "**", msgr_color="RED")
                content="\n"
                
        # print(sqlTxt3)
        data3 = conn3.query(sqlTxt3)

        if conn3.rows() > 0:
            result3 = [dict((conn3.description()[i][0], value) \
                            for i, value in enumerate(row)) for row in data3]
            
            content=""
            for sms_txt3 in result3 :
                content = content + "일시 : " + sms_txt3["수집시간"].strftime("%Y-%m-%d %H:%M:%S") + "\n"
                content = content + "서버 : " + sms_txt3["시스템명"].encode("ISO-8859-1").decode("euc-kr") + "(" +  str(sms_txt3["인스턴스ID"])+ ")" + "\n"
                content = content + "락지속시간(s) : " + str(sms_txt3["락지속시간(s)"]) + "\n"
                
                content = content + "타입 : " + str(sms_txt3["타입"]) + "\n"
                if sms_txt3["오브젝트명"]:
                    content = content + "오브젝트명 : " + str(sms_txt3["오브젝트명"]) + "\n"
                if sms_txt3["호스트명"]:
                    content = content + "호스트명 : " + str(sms_txt3["호스트명"]) + "\n"
                content = content + "대기정보 : " + str(sms_txt3["대기정보"]) + "\n\n"
                content = content + "SQL_TEXT : \n```\n" + str(sms_txt3["SQL_TEXT"]).replace("\x00","") + "\n```"
                # print(content)
                # msgr.put_msgr_target(content, "DB0001")
                
                # 20230629 보안 요청
                if sms_txt3["시스템명"].encode("ISO-8859-1").decode("euc-kr")== "[인프라] DRM":
                    if datetime.datetime.now().strftime("%H%M%S") >= "090000" and datetime.datetime.now().strftime("%H%M%S") <= "235959":
                        # msgr.put_msgr_target(content, "DB0001")
                        msgr.put_msgr_target(content, grp_cd="DB0003", send_title="**" + func_nm() + "**", msgr_color="RED")
                        msgr.put_msgr_target(content, grp_cd="NW0001",send_title="DRM Lock 모니터링", msgr_color="RED")
                else:
                    # msgr.put_msgr_target(content, "DB0001")
                    msgr.put_msgr_target(content, grp_cd="DB0003", send_title="**" + func_nm() + "**", msgr_color="RED")
                content="\n"

    except Exception as e:
        # print(func_nm() + ": " + str(e))
        msgr.put_msgr_target(func_tree() + ":\n" + str(e), grp_cd="DB9993", send_title="**" + func_nm() + "**", msgr_color="RED")
        
    finally:
        if conn:
            conn.close()
        if conn2:
            conn2.close()
        if conn3:
            conn3.close()


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------        
def list_meta_sec_check(args=YMDHH24MISS):
    print("MetaSecChk " + args)

    try:
        # DB 기본 접속 정보
        conn  = None
        conn  = metaDB()

        sqlTxt = ""

        # SQL 호출
        sqlTxt = """SELECT "항목구분", "신청구분", "시스템", "업무구분", "항목명" || '(' || "항목영문명" || ')' as "항목명", "도메인명/유형" as "도메인", "정의"
                         , "신청자", "수정일자" as "승인일시"
                      FROM ORADBA.META_SEC_MONITORING
                     WHERE "항목구분" = '용어'
                       AND "도메인명/유형" LIKE '%마스킹%'
                       AND "수정일자" >= :B1
                  """
        
        data = conn.query(sqlTxt, [args])
        
        if data:
            result = [dict((conn.description()[i][0], value) \
                            for i, value in enumerate(row)) for row in data]
            # print(result)
            
            for sms_txt in result :
                content=""

                content = content + "항목구분 : " + sms_txt["항목구분"]  + "\n"
                content = content + "신청구분 : " + sms_txt["신청구분"]  + "\n"
                content = content + "시스템 : "   + sms_txt["시스템"]    + "\n"
                content = content + "업무구분 : " + sms_txt["업무구분"]  + "\n"
                content = content + "항목명 : "   + sms_txt["항목명"]    + "\n"
                content = content + "도메인 : "   + sms_txt["도메인"]    + "\n"
                content = content + "정의 : "     + sms_txt["정의"]      + "\n"
                content = content + "신청자 : "   + sms_txt["신청자"]    + "\n"
                content = content + "승인일시 : " + sms_txt["승인일시"]  + "\n"# .strftime("%Y-%m-%d %H:%M:%S") + "\n"
                # print(content)
                
                msgr.put_msgr_target(content, "DB0005", send_title="**[마스킹 체크]**", msgr_color="GRAY") # 처리할게 없어서 GRAY
                msgr.put_msgr_target(content, grp_cd="SC0001", send_title="**[마스킹 체크]**", msgr_color="YELLOW")

    except Exception as e:
        # print(func_nm() + ": " + str(e))
        msgr.put_msgr_target(func_tree() + ":\n" + str(e), grp_cd="DB9993", send_title="**" + func_nm() + "**", msgr_color="RED")
        # pass
    
    finally:
        if conn:
            conn.close()


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------        
def list_ms_trace(args=YMDHH24MISS):
    print("MSTraceOnChk " + args)

    try:
        # DB 기본 접속 정보
        conn = None
        conn = monDB(func_nm())
        sqlTxt = ""

        # SQL 호출
        sqlTxt = """/* Trace(Profile) 사용 발생 시 모니터링 */
                      SELECT max(a.CollectDate) as time, b.ServerName, replace (a.wait_info, left(a.wait_info, PATINDEX('%)%',a.wait_info)),'') wait_info
                           ,max(a.total_elapsed_time) AS elapsed_time_ms, a.session_id, a.login_name, a.host_name
                           -- LTRIM, RTRIM만으로는 NULL 체크가 안됨 
                           -- ISNULL을 해놓고 ''로 만든다음에 비교해야됨 (이상함..)
                           , CASE WHEN ISNULL(LTRIM(RTRIM(a.ObjectName)),'') = '' THEN SUBSTRING(a.sql_text,1,30) ELSE a.ObjectName END AS SQL_TEXT
                       FROM TBL2_M_WhoIsActive a with (nolock), META2_M_InstanceInfo b with (nolock)
                       WHERE 1=1
                       AND a.CollectDate > = '{}'
                       AND a.InstanceID = b.InstanceID
                       AND a.wait_info like '%TRACE%'
                       AND a.host_name <> 'LPSQLMON'
                       AND b.UseYN = 'Y'
                       AND a.InstanceID IN (2, 4, 5, 6, 7, 8, 11, 12, 13, 15, 16, 21, 24, 27, 39, 48, 50, 51, 52, 53, 54, 55, 56, 57, 79)
                       --AND wait_info like '%TRACEWRITE%'
                       --AND InstanceID = 13
                       --AND b.ServerName IN ($ServerName)  
                      GROUP BY b.ServerName, replace (a.wait_info, left(a.wait_info, PATINDEX('%)%',a.wait_info)),''), a.session_id, a.login_name, a.host_name
                             , CASE WHEN ISNULL(LTRIM(RTRIM(a.ObjectName)),'') = '' THEN SUBSTRING(a.sql_text,1,30) ELSE a.ObjectName END
                 """.format(args)

        # print(sqlTxt)
        data = conn.query(sqlTxt)

        if conn.rows() > 0:
            result = [dict((conn.description()[i][0], value) \
                            for i, value in enumerate(row)) for row in data]

            content=""
            for sms_txt in result :
                content = content + "일시 : "     + sms_txt["time"].strftime("%Y-%m-%d %H:%M:%S") + "\n"
                content = content + "서버 : "     + sms_txt["ServerName"] + "\n"
                content = content + "내용 : "     + sms_txt["wait_info"]  + " 발생" + "\n"
                content = content + "세션 : "     + str(sms_txt["session_id"]) + "(" + sms_txt["login_name"] + ")" + "\n" 
                content = content + "사용자 : "   + sms_txt["host_name"]  + "\n" 
                content = content + "상세쿼리 : \n```\n" + sms_txt["SQL_TEXT"] + "\n```"
                # print(content)
                # msgr.put_msgr_target(content, "DB0001")
                msgr.put_msgr_target(content, grp_cd="DB0003", send_title="**" + func_nm() + "**", msgr_color="ORANGE")
                content="\n"

    except Exception as e:
        # print(func_nm() + ": " + str(e))
        msgr.put_msgr_target(func_tree() + ":\n" + str(e), grp_cd="DB9993", send_title="**" + func_nm() + "**", msgr_color="RED")
    
    finally:
        if conn:
            conn.close()


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------        
def check_bat_inst():
    print("BatInstChk")

    try:
        # DB 기본 접속 정보
        conn = None
        conn = batDB(func_nm())
        sqlTxt = ""

        # SQL 호출
        sqlTxt = """SELECT instance_name, status
                        --  , to_char(startup_time,'YYYY-MM-DD HH24:MI:SS') as startup_time 
                        , startup_time
                    FROM gv$instance
                    """ # 날짜 부분 변수로 들어 갈 수 있도록

        # print(sqlTxt)    
        data = conn.query(sqlTxt)

        # Oracle need to fetchall first for rowcount
        # cursor.fetchall()
        result = [dict((conn.description()[i][0], value) \
                        for i, value in enumerate(row)) for row in data]
        
        if conn.rows() != 2:
            content="\n"
            for sms_txt in result :
                content = content + "일시 : " + sms_txt["STARTUP_TIME"].strftime("%Y-%m-%d %H:%M:%S") + "\n"
                content = content + "대상 : " + sms_txt["INSTANCE_NAME"] + "\n"
                content = content + "내용 : " + sms_txt["STATUS"]
                # print(content)
                # msgr.put_msgr_target(content, "DB0001")
                msgr.put_msgr_target(content, grp_cd="DB0003", send_title="**" + func_nm() + "**", msgr_color="RED")
                content="\n"
                    
    except Exception as e:
        # print(func_nm() + ": " + str(e))
        msgr.put_msgr_target(func_tree() + ":\n" + str(e), grp_cd="DB9993", send_title="**" + func_nm() + "**", msgr_color="RED")
        pass
    
    finally:
        if conn:
            conn.close()


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------        
def list_meta_appr(args=YMDHH24MISS):
    print("MetaApprChk" + args)

    try:
        # DB 기본 접속 정보
        conn  = None
        conn2 = None
        conn  = metaDB()
        conn2 = metaDB()

        sqlTxt = ""
        sqlTxt2 = ""

        # SQL 호출
        sqlTxt = """SELECT "시스템"
                          ,"업무구분"
                          --,"논리명"
                          --,"요청구분"
                          --,"요청사유"
                          ,"결재 대기 라인"
                          ,COUNT(1) AS "건수"
                      FROM ORADBA.META_MODEL_MONITORING 
                     WHERE "수정일자" >= :B1
                     GROUP BY "시스템", "업무구분", "결재 대기 라인"
                  """

        sqlTxt2 = """SELECT "시스템",
                            "업무구분",
                            "항목구분",
                            -- "항목명",
                            -- "항목영문명",
                            -- "도메인명/유형",
                            -- "데이터타입",
                            -- "정의",
                            "결재 대기 라인"-- , "수정일자"
                            , COUNT(1) AS "건수"
                       FROM ORADBA.META_TERM_MONITORING 
                      WHERE "수정일자" >= :B1
                     GROUP BY "시스템", "업무구분", "항목구분", "결재 대기 라인"
                   """
        
        data = conn.query(sqlTxt, [args])
        
        if data:
            result = [dict((conn.description()[i][0], value) \
                            for i, value in enumerate(row)) for row in data]

            content="[모델표준화]\n"
            for sms_txt in result :
                content = content + "시스템 : "         + sms_txt["시스템"]         + "\n"
                content = content + "업무구분 : "       + sms_txt["업무구분"]       + "\n"
                content = content + "결재 대기 라인 : " + sms_txt["결재 대기 라인"] + "\n"
                content = content + "건수 : " + str(sms_txt["건수"]) #+ "\n"
                # print(content)
                # msgr.put_msgr_target(content, "DB0001")
                msgr.put_msgr_target(content, grp_cd="DB0005", send_title="**" + func_nm() + "**", msgr_color="YELLOW")
                content="[모델표준화]\n"                    
        
        data2 = conn2.query(sqlTxt2, [args])

        if data2:
            result2 = [dict((conn2.description()[i][0], value) \
                            for i, value in enumerate(row)) for row in data2]

            content="[데이터표준화]\n"
            for sms_txt2 in result2 :
                if sms_txt2["시스템"]:
                    content = content + "시스템 : "     + sms_txt2["시스템"]         + "\n"
                if sms_txt2["업무구분"]:
                    content = content + "업무구분 : "   + sms_txt2["업무구분"]       + "\n"
                if sms_txt2["항목구분"]:
                    content = content + "항목구분 : "   + sms_txt2["항목구분"]       + "\n"
                else:
                    content = content + "항목구분 : "   + "단어"       + "\n"

                content = content + "결재 대기 라인 : " + sms_txt2["결재 대기 라인"] + "\n"
                content = content + "건수 : " + str(sms_txt2["건수"]) #+ "\n"
                # print(content)
                # msgr.put_msgr_target(content, "DB0001")
                msgr.put_msgr_target(content, grp_cd="DB0005", send_title="**" + func_nm() + "**", msgr_color="YELLOW")
                content="[데이터표준화]\n"

    except Exception as e:
        # print(func_nm() + ": " + str(e))
        msgr.put_msgr_target(func_tree() + ":\n" + str(e), grp_cd="DB9993", send_title="**" + func_nm() + "**", msgr_color="RED")
        # pass
    
    finally:
        if conn:
            conn.close()
        if conn2:
            conn2.close()



def list_netbackup_err(args=YMDHH24MISS):
    print("netBackupChk " + args)

    try:
        # DB 기본 접속 정보
        conn = None
        conn = monPC(func_nm())
        sqlTxt = ""

        # SQL 호출
        sqlTxt = """/* 넷백업 오류 모니터링 */
                      SELECT JobID, Client, Schedule, Policy, format(Started,'yyyy-MM-dd HH:mm:ss') Started, format(Ended,'yyyy-MM-dd HH:mm:ss') Ended
                           -- , case  State when 'Done' then 0 when 'Active' then 1 else 2 end as State 
                           , Elapsed, Active_Elapsed, Status
                           , Dest_Media_Svr, Dest_StUnit, Attempt, Completion, Owner
                           , RGST_DTM, MDF_DTM
                        FROM [TB_Bak_Stat_Chk_L] with (nolock)
                        WHERE 1=1
                        AND collectDT between convert(varchar(8),getdate()-1,112) and convert(varchar(8),getdate(),112)
                        and MDF_DTM > = '{}'
                        and State = 'Done'
                        and Status > 1
                        -- 20240418 jyh 추가 (복원은 모니터링 대상 제외)
                        and type <> 'Restore'
                 """.format(args)

        # print(sqlTxt)
        data = conn.query(sqlTxt)

        if conn.rows() > 0:
            result = [dict((conn.description()[i][0], value) \
                            for i, value in enumerate(row)) for row in data]

            content="\n"
            for sms_txt in result :
                content = content + "일시 : "         + sms_txt["Ended"] + "\n"
                content = content + "잡아이디 : "     + str(sms_txt["JobID"]) + "\n"
                content = content + "클라이언트명 : " + sms_txt["Client"] + "\n"
                content = content + "스케줄명 : "     + sms_txt["Schedule"] + "\n"
                content = content + "정책명 : "       + sms_txt["Policy"] + "\n"
                content = content + "소요시간 : "     + str(sms_txt["Elapsed"]) + "\n"
                content = content + "상태값 : "       + sms_txt["Status"] + "\n"
                content = content + "미디어서버명 : " + sms_txt["Dest_Media_Svr"] + "(" + sms_txt["Dest_StUnit"] + ")" + "\n" 
                # print(content)
                msgr.put_msgr_target(content, grp_cd="DB0003",send_title="netBackupChk", msgr_color="RED")
                msgr.put_msgr_target(content, grp_cd="SE0001",send_title="netBackupChk", msgr_color="RED")
                content="\n"

    except Exception as e:
        # print(func_nm() + ": " + str(e))
        msgr.put_msgr_target(func_tree() + ":\n" + str(e), grp_cd="DB9993", send_title="**" + func_nm() + "**", msgr_color="RED")
    
    finally:
        if conn:
            conn.close()
        
        
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------        
def read_db_errors (args=YMDHH24MISS):
    print(args)
    try:
        list_ora_err(args)
        list_ms_err(args)
        check_bat_inst()
        list_meta_appr(args)
        list_meta_sec_check(args)
        list_ms_trace(args)
        list_netbackup_err(args)
        
    except Exception as e:
        # print(file_nm() + ": " + str(e))
        msgr.put_msgr_target(file_nm() + ":\n" + str(e), grp_cd="DB9993", send_title="**" + func_nm() + "**", msgr_color="RED")
        pass

        # it might have a gap 0 to 1 min
        # to avoid dup message, use args2, plus 1 min and put on the top of def
    finally:
        # args   = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # print(args)
        return # args


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------        
# read_db_errors()

# while True:
#     read_db_errors()
