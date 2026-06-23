# common & configuration
import cmn.common_msgr as msgr
from cmn.common import get_cur_func_nm as func_nm, get_cur_file_nm as file_nm, get_func_tree as func_tree
from cmn.common_db import monPC
from cmn.common_work import check_working_day
from cmn.common_datetime import NETBACKUP_YMD as YMD


def list_itsm_approval(trgetSysNm):
    conn = monPC(func_nm())

    # SQL 호출
    sqlTxt = """
                SELECT STEP_CD AS [진행단계]
				     , REQ_NO as [CSR]
                     , OBJ_SYS_NM [담당부서]
                     , REQ_SMCLS_NM AS [카테고리]
                     , REQ_TIT_NM AS [내용]
                     , REQPR_NM + ' (' + REQ_DPT_NM + ')' AS [요청]
                     , REQ_DT AS [요청일자]
                     , CMPL_DT AS [일자]
                     , RCPTPR_NM [작업]
                  FROM [MonitoringDB].[dbo].[TB_NEWITSM_REQ_L] with (nolock)
                 WHERE STEP_CD IN ('11')
                   AND OBJ_SYS_NM = %s
                   AND REQ_DT >= DATEADD(DAY, -30, GETDATE())
                 ORDER BY OBJ_SYS_NM, CMPL_DT, REQ_NO
             """

    try:   
        # print(sqlTxt)
        conn.execute(sqlTxt, trgetSysNm)
        fetchData = conn.fetchall()
        if fetchData:
            result = [dict((conn.description()[i][0], value.encode("ISO-8859-1").decode("euc-kr") if value is not None else None) \
                            for i, value in enumerate(row)) for row in fetchData]
            # result_txt = ""
            content=""
            content_old=""
            content_today=""

            for i, sms_txt in enumerate(result):
                    if YMD > sms_txt["일자"]:
                        content_old = content_old + "**" + sms_txt["카테고리"] + "**\n"
                        content_old = content_old + "# CSR : " + sms_txt["CSR"] + "\n"
                        content_old = content_old + "# 내용 : " + sms_txt["내용"] + "\n"
                        content_old = content_old + "# 요청 : " + sms_txt["요청"] + "\n"
                        content_old = content_old + "# 작업 : " + sms_txt["작업"] + "\n"
                        content_old = content_old + "# 일자 : " + sms_txt["일자"] + "\n"
                        content_old = content_old + "\n"

                    elif YMD == sms_txt["일자"]:
                        content_today = content_today + "**" + sms_txt["카테고리"] + "**\n"
                        content_today = content_today + "# CSR : " + sms_txt["CSR"] + "\n"
                        content_today = content_today + "# 내용 : " + sms_txt["내용"] + "\n"
                        content_today = content_today + "# 요청 : " + sms_txt["요청"] + "\n"
                        content_today = content_today + "# 작업 : " + sms_txt["작업"] + "\n"
                        content_today = content_today + "# 일자 : " + sms_txt["일자"] + "\n"
                        content_today = content_today + "\n"

                    else:
                        content = content + "**" + sms_txt["카테고리"] + "**\n"
                        content = content + "# CSR : " + sms_txt["CSR"] + "\n"
                        content = content + "# 내용 : " + sms_txt["내용"] + "\n"
                        content = content + "# 요청 : " + sms_txt["요청"] + "\n"
                        content = content + "# 작업 : " + sms_txt["작업"] + "\n"
                        content = content + "# 일자 : " + sms_txt["일자"] + "\n"
                        content = content + "\n"
                    
            content_old = content_old.rstrip()
            content_today = content_today.rstrip()
            content = content.rstrip()

            if trgetSysNm == "데이터베이스" :
                if content_old:
                    msgr.put_msgr_target(content_old, "DBWX04", send_title="ITSM 지연", msgr_color="Attention", send_funcnm=func_nm())
                if content_today:
                    msgr.put_msgr_target(content_today, "DBWX04", send_title="ITSM 금일 작업", msgr_color="Accent", send_funcnm=func_nm())                
                if content:
                    msgr.put_msgr_target(content, "DBWX04", send_title="ITSM 예정", msgr_color="Good", send_funcnm=func_nm())

            if trgetSysNm == "보안" : 
                if content_old:
                    msgr.put_msgr_target(content_old, "SCWX04", send_title="ITSM 지연", msgr_color="Attention", send_funcnm=func_nm())
                if content_today:
                    msgr.put_msgr_target(content_today, "SCWX04", send_title="ITSM 금일 작업", msgr_color="Accent", send_funcnm=func_nm())                
                if content:
                    msgr.put_msgr_target(content, "SCWX04", send_title="ITSM 예정", msgr_color="Good", send_funcnm=func_nm())                
            

    except Exception as e:
        # print(func_nm() + ": " + str(e))
        msgr.put_msgr_target(func_tree() + ":\n" + str(e), grp_cd="DBWX99", send_title="[Error] ITSM 요청리스트", msgr_color="Attention", send_funcnm=func_nm())
        # pass

    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    try:
        if not check_working_day() :
            list_itsm_approval(trgetSysNm="데이터베이스")
            list_itsm_approval(trgetSysNm="보안")

    except Exception as e:
        # print(file_nm() + ": " + str(e))
        msgr.put_msgr_target(str(e), grp_cd="DBWX99", send_title="[Error] ITSM 요청리스트", msgr_color="Attention", send_funcnm=func_nm())