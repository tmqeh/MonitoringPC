# common & configuration
import cmn.common_msgr as msgr
from cmn.common import get_cur_func_nm as func_nm, get_cur_file_nm as file_nm, get_func_tree as func_tree
from cmn.common_db import workDB
from cmn.common_datetime import YMD


def get_weekend_work_sch(args=YMD):
    # DB 기본 접속 정보
    conn = workDB(func_nm())

    # SQL 호출
    sqlTxt = """SELECT MAX(CONTENT) DUTYNM, B.MEMBERNM, CONTENT
                    FROM SCHEDULE A WITH(NOLOCK), 
                MEMBER B WITH(NOLOCK)
                    WHERE B.GRADE = 2 
                    AND B.ID = A.MEMBERID
                    AND dateadd(DAY,0,GETDATE()) BETWEEN STARTDATE AND ENDDATE
                    AND CONTENT = '책임당직'
                GROUP BY B.MEMBERNM,  STARTDATE, ENDDATE, CONTENT
                UNION ALL
                SELECT DISTINCT C.TITLE, B.MEMBERNM + '(' + A.CONTENT + ')', CONTENT
                    FROM SCHEDULE A WITH(NOLOCK), 
                        MEMBER B WITH(NOLOCK),
                        DPT C WITH(NOLOCK)
                    WHERE B.ID = A.MEMBERID
                    AND dateadd(DAY,0,GETDATE()) BETWEEN A.STARTDATE AND A.ENDDATE
                    AND A.CONTENT IN ('주말근무','점검')
                    AND B.DPTNO = C.ID
                    AND EXISTS(SELECT 1 FROM SCHEDULE Z WITH(NOLOCK) WHERE dateadd(DAY,0,GETDATE()) BETWEEN Z.STARTDATE AND Z.ENDDATE AND Z.CONTENT = '주말근무')
            ORDER BY CONTENT DESC
                """ # 날짜 부분 변수로 들어 갈 수 있도록

    try:   
        # print(sqlTxt)    
        data = conn.query(sqlTxt)
        result = []
        if conn.rows() > 0: # .encode('ISO-8859-1').decode('euc-kr') 한글깨짐 방지로 추가
            result = [dict((conn.description()[i][0], value.encode('ISO-8859-1').decode('euc-kr')) \
                            for i, value in enumerate(row)) for row in data]

        contents = "" 
        if result:
            for sms_txt in result :
                contents = contents + '# ' + sms_txt['DUTYNM']  + ' : ' + sms_txt['MEMBERNM'] + '\n'
            # print(contents)
        
            # msgr.send_slack_message(contents, '#dba')
            # msgr.put_msgr_target(contents, grp_cd='DB0001')
            msgr.put_msgr_target(contents.rstrip("\n"), "DBWX99", send_title="휴일 근무자 리스트", msgr_color="GREEN", send_funcnm=func_nm())

    except Exception as e:
        # print(func_nm() + ": " + str(e))
        msgr.put_msgr_target(func_tree() + ":\n" + str(e), grp_cd="DBWX99", send_title="[Error] 휴일 근무자 리스트", msgr_color="RED", send_funcnm=func_nm())
        # pass

    finally:
        conn.close()


if __name__ == "__main__":
    try:
        get_weekend_work_sch()
    except Exception as e:
        # print(file_nm() + ": " + str(e))
        msgr.put_msgr_target(str(e), grp_cd="DBWX99", send_title="[Error] 휴일 근무자 리스트", msgr_color="RED", send_funcnm=func_nm())