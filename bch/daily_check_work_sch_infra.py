# common & configuration
import cmn.common_msgr as msgr
from cmn.common import get_cur_func_nm as func_nm, get_cur_file_nm as file_nm, get_func_tree as func_tree
from cmn.common_db import workDB
from cmn.common_work import check_working_day, check_working_day_start


def get_infra_attendance_work_day():
    conn = workDB(func_nm())

    # SQL 호출
    sqlTxt = """
                WITH TODAY_DUTY as (
                        SELECT distinct D.TITLE as PART_NM, M.MEMBERNM as MEM_NM, M.MEMBERID
                            , MIN(CASE WHEN M.MEMBERID IN ('L05124','L06140','L02090','L04049') THEN NULL ELSE M.MEMBERID END) OVER() as WRITER
                            , W.TITLE 
                            , CASE WHEN W.ID IS NULL                        THEN '정상근무' 
                                    WHEN W.ID = 6                            THEN '정상근무'
                                    WHEN W.ID = 5 AND S.CONTENT = '재택근무' THEN '재택근무'
                                    WHEN W.ID = 2                            THEN '교육'
                                    WHEN W.ID IN (4,8)                       THEN '정상근무' -- 4:출장, 8:외근
                                    WHEN W.ID IN (3)                         THEN '휴가' -- 3:하계휴가, 1:휴가, 1+대체휴무(CONTENT):대체휴무
                                    WHEN W.ID IN (1) AND S.CONTENT     LIKE '%반차%' THEN '정상근무'
                                    WHEN W.ID IN (1) AND S.CONTENT NOT LIKE '%대체%' AND S.CONTENT NOT LIKE '%반차%' AND S.CONTENT NOT LIKE '%공가%' THEN '휴가'
                                    WHEN W.ID IN (1) AND S.CONTENT     LIKE '%대체%' THEN '대체휴무'
                                    ELSE '기타일정'
                                END as WORK_TYPE
                            , S.CONTENT + ' ' + S.CONTENT2 as Detail
                            , S.CONTENT
                            , W.ID
                        FROM MEMBER (NOLOCK) M
                    INNER JOIN DPT (NOLOCK) D
                            ON M.DPTNO = D.ID
                            AND D.TITLE in('인프라')
                    LEFT OUTER JOIN SCHEDULE (NOLOCK) S
                            ON M.ID = S.MEMBERID
                        AND GETDATE() BETWEEN S.STARTDATE AND S.ENDDATE
                    LEFT OUTER JOIN DUTY (NOLOCK) W
                            ON S.DUTYID = W.ID
                        WHERE M.USEYN = 1)
                SELECT  
                    MAX(CASE WHEN MEMBERID = WRITER THEN MEM_NM END) as [작성자]
                    , '[링크](http://ldps-sltn-alb-atlassian-01-1012132539.ap-northeast-2.elb.amazonaws.com:8090/pages/viewpage.action?pageId=153984500)' as [URL]
                    , MAX(PART_NM) as [파트]
                    , COUNT(PART_NM) as [총인원]
                    , SUM(CASE WHEN WORK_TYPE IN ('정상근무','외근', '재택근무') THEN 1 ELSE 0 END) as [근무인원]
                    , SUM(CASE WHEN WORK_TYPE IN ('휴가','대체휴무','교육','기타일정') THEN 1 ELSE 0 END) as [휴무/교육 인원] 
                    , ISNULL(STUFF((SELECT ',' + MEM_NM +'(' + CONTENT + ')' FROM TODAY_DUTY X WHERE X.WORK_TYPE IN     ('대체휴무') FOR XML PATH('')),1,1,''),'-') as [대휴]
                    , ISNULL(STUFF((SELECT ',' + MEM_NM +'(' + CONTENT + ')' FROM TODAY_DUTY X WHERE X.WORK_TYPE IN     ('휴가') FOR XML PATH('')),1,1,''),'-') as [년차/휴가]
                    , ISNULL(STUFF((SELECT ',' + MEM_NM +'(' + CONTENT + ')' FROM TODAY_DUTY X WHERE X.WORK_TYPE IN     ('교육') FOR XML PATH('')),1,1,''),'-') as [교육]
                    , ISNULL(STUFF((SELECT ',' + MEM_NM +'(' + CONTENT + ')' FROM TODAY_DUTY X WHERE X.WORK_TYPE NOT IN ('휴가','대체휴무','교육', '정상근무') FOR XML PATH('')),1,1,''),'-') as [공가/기타]
                FROM TODAY_DUTY with (nolock)
             """

    try:   
        # print(sqlTxt)
        conn.execute(sqlTxt)
        fetchData = conn.fetchall()

        if fetchData:
            result = [dict((conn.description()[i][0], value) \
                            for i, value in enumerate(row)) for row in fetchData]
            content=""

            for sms_txt in result :
                sms_txt['작성자']    =    sms_txt['작성자'].encode('ISO-8859-1').decode('euc-kr')# iso-8859-1
                # sms_txt['URL']       =       sms_txt['URL'].encode('ISO-8859-1').decode('euc-kr')
                sms_txt['파트']      =      sms_txt['파트'].encode('ISO-8859-1').decode('euc-kr')
                # sms_txt['대휴']      =      sms_txt['대휴'].encode('ISO-8859-1').decode('euc-kr')
                # sms_txt['년차/휴가'] = sms_txt['년차/휴가'].encode('ISO-8859-1').decode('euc-kr')
                # sms_txt['교육']      =      sms_txt['교육'].encode('ISO-8859-1').decode('euc-kr')
                # sms_txt['공가/기타'] = sms_txt['공가/기타'].encode('ISO-8859-1').decode('euc-kr')
                content = content + '# 작성자 : '         + sms_txt['작성자']              + '\n'
                # content = content + '# URL : '            + sms_txt['URL']                 + '\n'
                content = content + '# 파트 : '           + sms_txt['파트']                + '\n'
                content = content + '# 총인원 : '         + str(sms_txt['총인원'])         + '\n'
                content = content + '# 근무인원 : '       + str(sms_txt['근무인원'])       + '\n'
                content = content + '# 휴무/교육 인원 : ' + str(sms_txt['휴무/교육 인원'])  + '\n'
                content = content + '# 대휴 : '           + sms_txt['대휴']                + '\n'
                content = content + '# 년차/휴가 : '      + sms_txt['년차/휴가']            + '\n'
                content = content + '# 교육 : '           + sms_txt['교육']                + '\n'
                content = content + '# 공가/기타 : '      + sms_txt['공가/기타']            + '\n'
                # print(content)
                msgr.put_msgr_target(content, "DBWX99",send_title="인프라파트 근태현황",msgr_color="Accent", send_funcnm=func_nm())

    except Exception as e:
        # print(func_nm() + ": " + str(e))
        msgr.put_msgr_target(func_tree() + ":\n" + str(e), grp_cd="DBWX99", send_title="[Error] 인프라파트 근태현황", msgr_color="Attention", send_funcnm=func_nm())
        # pass
    
    finally:
        conn.close()


def get_infra_attendance_week_start():
    conn = workDB(func_nm())

    # SQL 호출
    sqlTxt = """
                 WITH dummy_DT as (
                        -- 근태 공백 제거를 위한 날짜 더미 테이블 (재귀 사용)
                        SELECT GETDATE()-0 as DT_DATE, CONVERT(VARCHAR, GETDATE()-0, 112) as DT, DATEPART(WEEK, getdate()-0) WK
                        UNION ALL
                        SELECT DATEADD(DAY, 1, DT_DATE) as DT_DATE, CONVERT(VARCHAR, DATEADD(DAY, 1, DT_DATE), 112) as DT, DATEPART(WEEK, DATEADD(DAY, 1, DT_DATE))
                         FROM dummy_DT with (nolock)
                        WHERE DT_DATE < GETDATE()-0+7-1
                        ),
                      holyday_CHK as (
                      -- 책임당직 유무를 통해 휴일인지 확인 (명절 당일에는 책임당직이 없으므로 체크 로직 추가 필요)
                       SELECT Z.DT
                         FROM SCHEDULE A with (nolock), MEMBER B with (nolock), dummy_DT Z with (nolock)
                        WHERE B.GRADE = 2 
                          AND B.ID = A.MEMBERID
                          AND DATEADD(DAY, +0, z.DT_DATE) BETWEEN STARTDATE AND ENDDATE
                          AND CONTENT = '책임당직'
                        ),
                      TODAY_DUTY as (
                        -- 기존 근태는 GETDATE를 사용했지만
                        -- 한주치를 보기 위해서 dummy_DT와 조인
                        -- WRITER를 체크하는 로직이 좀 부실함 (방안 고민중)
                        -- ※ WRITER : 근태일일보고 작성자 추출 (영업일 1째날에만 작성하면되는데 그때의 작성자 찾는게 잘안됨)
                        -- ※ 영업일 1째날에만 해당쿼리 돌게 따로 체크로직 쿼리 만 들꺼임
                        SELECT Z.DT, Z.DT_DATE, Z.WK, D.TITLE as PART_NM, M.MEMBERNM as MEM_NM, M.MEMBERID
                            , MIN(CASE WHEN M.MEMBERID IN ('L05124','L06140','L02090','L04049') THEN NULL 
                                       WHEN W.ID IS NULL                                        THEN M.MEMBERID
                                       WHEN W.ID = 6                                            THEN M.MEMBERID
                                       WHEN W.ID = 5 AND S.CONTENT = '재택근무'                 THEN M.MEMBERID
                                       WHEN W.ID = 2                                            THEN NULL 
                                       WHEN W.ID IN (4,8)                                       THEN M.MEMBERID -- 4:출장, 8:외근
                                       WHEN W.ID IN (3)                                         THEN NULL  -- 3:하계휴가, 1:휴가, 1+대체휴무(CONTENT):대체휴무
                                       WHEN W.ID IN (1) AND S.CONTENT     LIKE '%반차%'         THEN M.MEMBERID
                                       WHEN W.ID IN (1) AND S.CONTENT NOT LIKE '%대체%' AND S.CONTENT NOT LIKE '%반차%' AND S.CONTENT NOT LIKE '%공가%' THEN NULL 
                                       WHEN W.ID IN (1) AND S.CONTENT     LIKE '%대체%'         THEN NULL 
                                       ELSE M.MEMBERID END) OVER(PARTITION BY Z.DT) as WRITER
                            , W.TITLE 
                            , CASE WHEN W.ID IS NULL                                 THEN '정상근무' 
                                    WHEN W.ID = 6                                    THEN '정상근무'
                                    WHEN W.ID = 5 AND S.CONTENT = '재택근무'         THEN '재택근무'
                                    WHEN W.ID = 2                                    THEN '교육'
                                    WHEN W.ID IN (4,8)                               THEN '정상근무' -- 4:출장, 8:외근
                                    WHEN W.ID IN (3)                                 THEN '휴가' -- 3:하계휴가, 1:휴가, 1+대체휴무(CONTENT):대체휴무
                                    WHEN W.ID IN (1) AND S.CONTENT     LIKE '%반차%' THEN '정상근무'
                                    WHEN W.ID IN (1) AND S.CONTENT NOT LIKE '%대체%' AND S.CONTENT NOT LIKE '%반차%' AND S.CONTENT NOT LIKE '%공가%' THEN '휴가'
                                    WHEN W.ID IN (1) AND S.CONTENT     LIKE '%대체%' THEN '대체휴무'
                                    ELSE '기타일정'
                                END as WORK_TYPE
                            , S.CONTENT + ' ' + S.CONTENT2 as Detail
                            , S.CONTENT
                            , W.ID
                        FROM MEMBER (NOLOCK) M CROSS APPLY dummy_DT Z
                    INNER JOIN DPT (NOLOCK) D
                            ON M.DPTNO = D.ID
                            AND D.TITLE in('인프라')
                    LEFT OUTER JOIN SCHEDULE (NOLOCK) S
                            ON M.ID = S.MEMBERID
                        AND Z.DT_DATE BETWEEN S.STARTDATE AND S.ENDDATE
                    LEFT OUTER JOIN DUTY (NOLOCK) W
                            ON S.DUTYID = W.ID
                        WHERE M.USEYN = 1)
                        SELECT *
                        FROM (
                            SELECT DT, REPLACE(SUBSTRING(CONVERT(VARCHAR, DT_DATE, 101),1,5),'/','.') as DT_DATE
                                 , REPLACE(SUBSTRING(CONVERT(VARCHAR, DT_DATE, 101),1,5),'/','.') + ' ' + 
                                 + ISNULL(STUFF((SELECT ',' + MEM_NM +'(' + CASE WHEN WORK_TYPE = '교육' THEN WORK_TYPE ELSE CONTENT END + ')' 
                                                   FROM TODAY_DUTY X  with (nolock)
                                                  WHERE X.WORK_TYPE IN ('휴가','대체휴무','교육','기타일정') 
                                                    AND A.DT = X.DT 
                                                  ORDER BY CASE WORK_TYPE WHEN '대체휴무' THEN 1 WHEN '휴가' THEN 2 WHEN '교육' THEN 3 ELSE 9 END, MEMBERID FOR XML PATH('')),1,1,''),'') as [근태 계획]
                                 , MAX(CASE WHEN MEMBERID = WRITER THEN MEM_NM END) as [작성자]
                                 , MAX(PART_NM) as [파트]
                              FROM TODAY_DUTY A with (nolock)
                             WHERE NOT EXISTS(SELECT 1 FROM holyday_CHK X with (nolock) WHERE A.DT = X.DT)
                           GROUP BY DT, DT_DATE
                       ) W 
                       -- 근태계획 비어있는거 제외시키면 작성자가 누락됨
                       -- 그냥 python 에서 2개가 같으면 pass 시키는쪽으로 방향을 잡아야겠다.
                       /*
                       작성자 = result[0]
                       if dt_date == [근태 계획]:
                            continue
                       else:
                       근태계획 = [근태 계획].append
                       */
                       -- WHERE DT_DATE != [ 근태 계획]
                       ORDER BY 1
             """

    try:   
        # print(sqlTxt)
        conn.execute(sqlTxt)
        fetchData = conn.fetchall()
        
        if fetchData:
            result = [dict((conn.description()[i][0], value) \
                            for i, value in enumerate(row)) for row in fetchData]
            content=""
            writer=""
            for i, sms_txt in enumerate(result) :
                
                # \MetaApprChk weekStartReportWriter Error except : 'latin-1' codec can't encode characters in position 6-8: ordinal not in range(256)
                sms_txt['근태 계획']    =    sms_txt['근태 계획']# .encode('ISO-8859-1').decode('euc-kr')# iso-8859-1 # 희안하네
                sms_txt['작성자']    =    sms_txt['작성자'].encode('ISO-8859-1').decode('euc-kr')# iso-8859-1
                sms_txt['파트']      =      sms_txt['파트'].encode('ISO-8859-1').decode('euc-kr')
                if i == 0:
                    writer=sms_txt['작성자']
                    content='# 작성자 : ' + writer + '\n'
                if sms_txt['DT_DATE'] == sms_txt['근태 계획'].strip():
                    continue
                else:
                    content = content + sms_txt['근태 계획'] + "\n"
                    
            msgr.put_msgr_target(content, "DBWX99",send_title="근태 계획",msgr_color="Accent", send_funcnm=func_nm())

    except Exception as e:
        # print(func_nm() + ": " + str(e))
        msgr.put_msgr_target(func_tree() + ":\n" + str(e), grp_cd="DBWX99", send_title="[Error] 인프라파트 근태현황", msgr_color="Attention", send_funcnm=func_nm())
        # pass
    
    finally:
        conn.close()


if __name__ == "__main__":
    try:
        if not check_working_day() :
            get_infra_attendance_work_day()
        if check_working_day_start(): # 필요 (영업일 시작하는 날짜 (정휴나 명절 제낄수 있는 로직))
            get_infra_attendance_week_start()

    except Exception as e:
        # print(file_nm() + ": " + str(e))
        msgr.put_msgr_target(str(e), grp_cd="DBWX99", send_title="[Error] 인프라파트 근태현황", msgr_color="Attention", send_funcnm=func_nm())
