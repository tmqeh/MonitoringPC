# common & configuration
import cmn.common_msgr as msgr
from cmn.common import get_cur_func_nm as func_nm, get_cur_file_nm as file_nm, get_func_tree as func_tree
from cmn.common_db import monPC
from cmn.common_datetime import check_weekday
from cmn.common_work import check_working_day
from cmn.common_datetime import NETBACKUP_YMD as YMD


def list_itsm_approval():
    conn = monPC(func_nm())

    # SQL 호출
    sqlTxt = """
                SELECT '[' + STEP  + '] ' + DTL_REQ_TP_NM AS [카테고리]
                     , TIT AS [내용]
                     , REQPR_NM + ' (' + REQ_DPT_NM + ')' AS [요청자]
                     , REQ_DT AS [요청일자]
                     , CMPL_HOPE_DT AS [완료희망일자]
                     , CASE WHEN STEP like '%접수승인%' THEN SUBSTRING(WRKR_ID, 1,  CASE WHEN CHARINDEX(' 외', WRKR_ID) = 0 THEN LEN(WRKR_ID) ELSE CHARINDEX(' 외', WRKR_ID)-1 END) ELSE NULL END [작업자]
                  FROM [MonitoringDB].[dbo].[TB_ITSM_REQ_L] with (nolock)
                 WHERE STEP like '%접수%'
                   AND SVC_CATALOG LIKE '%데이터베이스%'
                   AND REQ_DT >= DATEADD(DAY, -30, GETDATE())
                 ORDER BY CMPL_HOPE_DT, REQ_NO
             """

    try:   
        # print(sqlTxt)
        conn.execute(sqlTxt)
        fetchData = conn.fetchall()
        if fetchData:
            result = [dict((conn.description()[i][0], value.encode("ISO-8859-1").decode("euc-kr") if value is not None else None) \
                            for i, value in enumerate(row)) for row in fetchData]
            # result_txt = ""
            content=""
            content_old=""

            for i, sms_txt in enumerate(result):
                    if YMD > sms_txt["완료희망일자"]:
                        content_old = content_old + "카테고리 : " + sms_txt["카테고리"] + "\n"
                        content_old = content_old + "내용 : " + sms_txt["내용"]    + "\n"
                        content_old = content_old + "요청자 : " + sms_txt["요청자"]   + "\n"
                        if sms_txt["작업자"] is not None:
                            content_old = content_old + "작업자 : " + sms_txt["작업자"] + "\n"
                        content_old = content_old + "완료희망일자 : " + sms_txt["완료희망일자"] + "\n"

                    else:
                        content = content + "카테고리 : " + sms_txt["카테고리"] + "\n"
                        content = content + "내용 : " + sms_txt["내용"]    + "\n"
                        content = content + "요청자 : " + sms_txt["요청자"]   + "\n"

                        if sms_txt["작업자"] is not None and YMD == sms_txt["완료희망일자"]:
                            content = content + "작업자 : " + "**" + sms_txt["작업자"] + "**" + "\n"
                        elif sms_txt["작업자"] is not None:
                            content = content + "작업자 : " + sms_txt["작업자"] + "\n"

                        if YMD == sms_txt["완료희망일자"]:
                            content = content + "완료희망일자 : " + "**" + sms_txt["완료희망일자"] + "**" + "\n\n"
                        else:
                            content = content + "완료희망일자 : " + sms_txt["완료희망일자"] + "\n\n"
                    
                    # result_txt = result_txt + content
            content_old = content_old.rstrip()
            content = content.rstrip()

            if content_old:
                msgr.put_msgr_target(content_old, "DB0004", send_title="**ITSM 요청리스트 (일정 확인 필요)**", msgr_color="RED")
            if content:
                msgr.put_msgr_target(content, "DB0004", send_title="**ITSM 요청리스트**", msgr_color="WHITE")
            # msgr.put_msgr_target(content, "DB0001")

    except Exception as e:
        # print(func_nm() + ": " + str(e))
        msgr.put_msgr_target(func_tree() + ":\n" + str(e), grp_cd="DB9993", send_title="**" + func_nm() + "**", msgr_color="RED")
        # pass

    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    try:
        if not check_working_day() :
            list_itsm_approval()

    except Exception as e:
        # print(file_nm() + ": " + str(e))
        msgr.put_msgr_target(str(e), grp_cd="DB9993", send_title="**" + file_nm() + "**", msgr_color="RED")