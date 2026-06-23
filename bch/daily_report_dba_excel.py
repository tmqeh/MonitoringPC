import win32com.client # for excel handling
import shutil # for file copy
from pathlib import Path # for finding windows "downloads" folder

# common & configuration
import cmn.common_msgr as msgr
from cmn.common import get_cur_func_nm as func_nm, get_cur_file_nm as file_nm, get_func_tree as func_tree
from cmn.common_datetime import YMD, YESTERDAY_YMD
from cmn.common_file import check_file

# COM 설명 참고사이트 : 
# https://pbpython.com/windows-com.html

# Dcom 설정 참고 사이트 : 
# https://superuser.com/questions/579900/why-cant-excel-open-a-file-when-run-from-task-scheduler

# 잡스케줄러 등록 방법
# 기본은 시작하는 사용자 인듯 --> 대화형 사용자로 저장 후 등록


# Start an instance of Excel
xlapp = win32com.client.DispatchEx("Excel.Application")

# Open the workbook in said instance of Excel
FILE_HOME = str(Path.home() / "Downloads") + '/'
FILE_NAME = "_DBA_일일점검보고서.xlsx"

SOURCE_DT = YESTERDAY_YMD
TARGET_DT = YMD


def export_daily_report():
    try:
        shutil.copy(FILE_HOME + SOURCE_DT + FILE_NAME, FILE_HOME + TARGET_DT + FILE_NAME)
        wb = xlapp.workbooks.open(FILE_HOME + TARGET_DT + FILE_NAME)
        # Optional, e.g. if you want to debug
        # xlapp.Visible = True

        # Refresh all data connections.
        wb.RefreshAll()
        # to refresh all the data
        xlapp.CalculateUntilAsyncQueriesDone()

        wb.Save()
        # Save는 이미 완료 했고
        # 종료할때 다시 저장을 물어보는데 해당 팝업이 안뜨도록 옵션 지정 후 호출
        wb.Close(SaveChanges=False)
        # Quit
        xlapp.Quit()
    except Exception as e:
        # print(func_nm() + ": " + str(e))
        msgr.put_msgr_target(func_tree() + ":\n" + str(e), grp_cd="DBWX99", send_title="**" + func_nm() + "**", msgr_color="RED", send_funcnm=func_nm())


if __name__ == "__main__":
    try:
        export_daily_report()
        while check_file(FILE_HOME + TARGET_DT + FILE_NAME) == 'N':
            msgr.put_msgr_target("DBA 일일점검보고 " + "재시도", grp_cd="DBWX99", send_title="**" + func_nm() + "**", msgr_color="WHITE", send_funcnm=func_nm())
                
        msgr.put_msgr_target(FILE_HOME + TARGET_DT + FILE_NAME + " is created", grp_cd="DBWX99", send_title="**" + func_nm() + "**", msgr_color="WHITE", send_funcnm=func_nm())
    except Exception as e:
        # print(file_nm() + ": " + str(e))
        msgr.put_msgr_target(str(e), grp_cd="DBWX99", send_title="**" + file_nm() + "**", msgr_color="RED", send_funcnm=func_nm())