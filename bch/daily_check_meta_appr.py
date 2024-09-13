# common & configuration
import cmn.common_msgr as msgr
from cmn.common import get_cur_func_nm as func_nm, get_cur_file_nm as file_nm, get_func_tree as func_tree
from cmn.common_db import metaDB
from cmn.common_datetime import check_weekday
from cmn.common_work import check_working_day


def list_meta_approval():
    conn = metaDB(func_nm())
    conn2 = metaDB(func_nm())

    # SQL 호출
    sqlTxt = """
            SELECT "시스템",
                    -- "업무구분",
                    -- "논리명",
                    -- "요청구분",
                    -- "요청사유",
                    NVL("결재 대기 라인",'검토중') as "결재 대기 라인"
                    , COUNT(1) AS "건수"
                FROM ORADBA.META_MODEL_MONITORING 
                GROUP BY "시스템", NVL("결재 대기 라인",'검토중')
                """

    sqlTxt2 = """
            SELECT "시스템",
                    -- "업무구분",
                    "항목구분",
                    -- "항목명",
                    -- "항목영문명",
                    -- "도메인명/유형",
                    -- "데이터타입",
                    -- "정의",
                    "결재 대기 라인"-- , "수정일자"
                    , COUNT(1) AS "건수"
                FROM ORADBA.META_TERM_MONITORING 
            GROUP BY "시스템", "항목구분", "결재 대기 라인"
                """

    try:   
        # print(sqlTxt)
        conn.execute(sqlTxt)
        fetchData = conn.fetchall()
        if fetchData:
            result = [dict((conn.description()[i][0], value) \
                            for i, value in enumerate(row)) for row in fetchData]
            result_txt = ""
            content="[모델표준화]\n"

            for sms_txt in result :
                if check_weekday() != 1 and  sms_txt['결재 대기 라인'] == 'DBA' : # 화요일만 DBA 결재 표시
                    continue
                else :
                    content = content + '시스템 : '         + sms_txt['시스템']         + '\n'
                    content = content + '결재 대기 라인 : ' + sms_txt['결재 대기 라인'] + '\n'
                    content = content + '건수 : ' + str(sms_txt['건수']) + '\n'
                    # print(content)
                    
                    result_txt = result_txt + content
                    content = ""
                    
            # msgr.put_msgr_target(result_txt, 'DB0001')
            msgr.put_msgr_target(result_txt.rstrip("\n"), "DB0005", send_title="**[모델표준화]**", msgr_color="WHITE")

        conn2.execute(sqlTxt2)
        fetchData2 = conn2.fetchall()

        if fetchData2:
            result2 = [dict((conn2.description()[i][0], value) \
                            for i, value in enumerate(row)) for row in fetchData2]
            result2_txt = ""
            content="[데이터표준화]\n"
            
            for sms_txt2 in result2 :
                if sms_txt2['시스템']:
                    content = content + '시스템 : '     + sms_txt2['시스템']         + '\n'
                if sms_txt2['항목구분']:
                    content = content + '항목구분 : '   + sms_txt2['항목구분']       + '\n'
                else:
                    content = content + '항목구분 : '   + '단어'       + '\n'

                content = content + '결재 대기 라인 : ' + sms_txt2['결재 대기 라인'] + '\n'
                content = content + '건수 : ' + str(sms_txt2['건수']) + '\n'
                # print(content)

                result2_txt =  result2_txt + content
                content = ""
            
            # msgr.put_msgr_target(result2_txt, 'DB0001')
            msgr.put_msgr_target(result2_txt.rstrip("\n"), "DB0005", send_title="**[데이터표준화]**", msgr_color="WHITE")

    except Exception as e:
        # print(func_nm() + ": " + str(e))
        msgr.put_msgr_target(func_tree() + ":\n" + str(e), grp_cd="DB9993", send_title="**" + func_nm() + "**", msgr_color="RED")
        # pass

    finally:
        if conn:
            conn.close()
        if conn2:
            conn2.close()


if __name__ == "__main__":
    try:
        if not check_working_day() :
            list_meta_approval()
    except Exception as e:
        # print(file_nm() + ": " + str(e))
        msgr.put_msgr_target(str(e), grp_cd="DB9993", send_title="**" + file_nm() + "**", msgr_color="RED")