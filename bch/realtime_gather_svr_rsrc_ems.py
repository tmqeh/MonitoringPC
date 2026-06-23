import os
import time  # for sleep
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
# import threading as th
# import concurrent.futures

# common & configuration
from cfg.config_ems import EMS_USER_ID, EMS_USER_PASSWORD, DELAY_TIME, EMS_LOGIN_URL, EMS_SVR_RSRC_CPU_MEM_URL, EMS_SVR_RSRC_FS_URL
from cfg.config_path import LOG_HOME
import cmn.common_msgr as msgr
from cmn.common import get_cur_func_nm as func_nm, get_cur_file_nm as file_nm, get_func_tree as func_tree
from cmn.common_db import monPC
from cmn.common_sql import get_string, get_size_mb


GATHER_FILESYSTEM_YN = 'N'
LOG_PATH = LOG_HOME + "ems/" 

# EMS 세션 맺으면 기존 세션이 종료되는 이슈 있음
# 해결 방법은 사용자 여러개 쓰던지, 아예 사용하지 않는 계정 이용
# EMS 자체에 동시 접속 제한이 있는 것으로 판단됨

# driver = webdriver.Chrome(service=service, options=options) 는 1개의 브라우저를 의미하기 때문에
# multi thread/process를 사용하면 안된다.
# 실제로 사용했더니 잘못된값 (다른 hostName의 value를 insert 하는것으로 추정)이 들어가서 제거함
# 사용하려면 멀티로그인이 안되기 때문에 여러개 계정을 준비하고, 각 thread별로 다른 driver를 이용해서 처리해야함


def list_ems_svr_id(args=None):
    conn = monPC(func_nm())

    sqlTxt = "select hostName, cpu_mem, FileSystem from TB_Svr_Rsrc_ID_EMS_M (nolock) order by newid()"

    try:
        # print(sqlTxt)
        data = conn.query(sqlTxt)
        result = []
        if conn.rows() > 0:
                result = [dict((conn.description()[i][0], value) \
                                for i, value in enumerate(row)) for row in data]
        # even MS-SQL need it (MUST)
        conn.commit()
        return result

    except Exception as e:
        # print(func_nm() + ": " + str(e))
        msgr.put_msgr_target(func_tree() + ":\n" + str(e), grp_cd="DBWX99", send_title="**" + func_nm() + "**", msgr_color="RED")

    finally:
        sqlTxt = ""
        conn.close()


def insert_svr_rsrc_ems_l(args):
    conn = monPC(func_nm())

    sqlTxt = "insert into dbo.TB_Svr_Rsrc_EMS_L (hostName, RSRC_NAME, USE_PCT, RGPR_ID, RGST_DTM, CollectDT, CollectHH, CollectMS) values " + "\n"

    # list to list
    for i, data_list in enumerate(args):  # for putting comma logic, enumerate is necessary
        # value transform to fit on insert syntax
        hostName = get_string(data_list[0], "l")
        rsrc_name = get_string(data_list[1], "l")
        use_pct = get_string(data_list[2].replace("-","0").replace("%", ""), "l")
        RGPR_ID = get_string("insert_svr_rsrc_ems_l", "l")
        RGST_DTM = "getdate()"
        CollectDT = "convert(varchar,getdate(),112)"
        CollectHH = "substring(convert(varchar,getdate(),108),1,2)"
        CollectMS = "substring(convert(varchar,getdate(),108),4,2) + substring(convert(varchar,getdate(),108),7,2)"

        # set bulk data query
        listToStr = "(" + \
                            hostName  + \
                      "," + rsrc_name + \
                      "," + use_pct   + \
                      "," + RGPR_ID   + \
                      "," + RGST_DTM  + \
                      "," + CollectDT + \
                      "," + CollectHH + \
                      "," + CollectMS + \
                    ")"

        # except last one, put comma and new line char
        if i < len(args) - 1:
            listToStr = listToStr + ",\n"
        sqlTxt = sqlTxt + listToStr

    try:
        # print(sqlTxt)
        conn.execute(sqlTxt)

        # even MS-SQL need it (MUST)
        conn.commit()

    except Exception as e:
        # print(func_nm() + ": " + str(e) + "\n" + str(args) + "\n" + sqlTxt)
        msgr.put_msgr_target(func_tree() + ":\n" + str(e) + "\n" + str(args) + "\n" + sqlTxt, grp_cd="DBWX99", send_title="**" + func_nm() + "**", msgr_color="RED", send_funcnm=func_nm())

    finally:
        sqlTxt = ""
        conn.close()


def insert_svr_fs_ems_l(args):
    conn = monPC(func_nm())

    sqlTxt = "insert into dbo.TB_Svr_Fs_EMS_L (hostName, path_name, drive_name , disk_type, total_size_mb, use_size_mb, free_size_mb, USE_PCT, RGPR_ID, RGST_DTM, CollectDT, collectHH, collectMS) values " + "\n"

    # list to list
    for i, row_dataset in enumerate(args):
        for data_list in row_dataset:  # for putting comma logic, enumerate is necessary
            # value transform to fit on insert syntax
            hostName = get_string(data_list[0], "l")
            if data_list[1] == "name":
                path_name = get_string(data_list[2].lstrip().rstrip(), "l")
            elif data_list[1] == "DiskName":
                drive_name = get_string(data_list[2], "l")
            elif data_list[1] == "Type":
                disk_type = get_string(data_list[2], "l")
            elif data_list[1] == "TotalSize":
                total_size_mb = get_size_mb(data_list[2])
            elif data_list[1] == "UsedSize":
                use_size_mb = get_size_mb(data_list[2])
            elif data_list[1] == "FreeSize":
                free_size_mb = get_size_mb(data_list[2])
            elif data_list[1] == "Utilization":
                use_pct = get_string(data_list[2].replace("-","0").replace("%", ""), "l")

            RGPR_ID = get_string("insert_svr_fs_ems_l", "l")
            RGST_DTM = "getdate()"
            CollectDT = "convert(varchar,getdate(),112)"  # data_list[1][0:8]
            CollectHH = "substring(convert(varchar,getdate(),108),1,2)"  # data_list[1][8:10]
            CollectMS = "substring(convert(varchar,getdate(),108),4,2) + substring(convert(varchar,getdate(),108),7,2)"  # data_list[1][10:14]

        # set bulk data query
        listToStr = "(" + \
                          hostName      + \
                    "," + path_name     + \
                    "," + drive_name    + \
                    "," + disk_type     + \
                    "," + total_size_mb + \
                    "," + use_size_mb   + \
                    "," + free_size_mb  + \
                    "," + use_pct       + \
                    "," + RGPR_ID       + \
                    "," + RGST_DTM      + \
                    "," + CollectDT     + \
                    "," + CollectHH     + \
                    "," + CollectMS     + \
                    ")"

        hostName      = ""
        path_name     = ""
        drive_name    = ""
        disk_type     = ""
        total_size_mb = ""
        use_size_mb   = ""
        free_size_mb  = ""
        use_pct       = ""

        # except last one, put comma and new line char
        if i < len(args) - 1:
            listToStr = listToStr + ",\n"
        sqlTxt = sqlTxt + listToStr

    try:
        # print(sqlTxt)
        conn.execute(sqlTxt)

        # even MS-SQL need it (MUST)
        conn.commit()

    except Exception as e:
        # print(func_nm() + ": " + str(e) + "\n" + str(args) + "\n" + sqlTxt)
        msgr.put_msgr_target(func_tree() + ":\n" + str(e) + "\n" + str(args) + "\n" + sqlTxt, grp_cd="DBWX99", send_title="**" + func_nm() + "**", msgr_color="RED", send_funcnm=func_nm())

    finally:
        sqlTxt = ""
        conn.close()


def ems_login():
    # 크롬 드라이버 위치 지정
    # CHROME_DRIVER_PATH = "C:\\chromedriver_win32\\chromedriver.exe"
    # 크롬 버전 올라 갈 때 마다 버전오류 발생하여 시작할때 설치 강제 실행
    # 경로 불필요
    # os.system("taskkill /F /IM chromedriver.exe") # ChromeDriverManager().install() 로 생성되는 프로세스 강제 종료
    # os.system("taskkill /F /IM chrome.exe") # ChromeDriverManager().install() 로 생성되는 프로세스 강제 종료
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    # 화면 미표시 옵션
    options.add_argument("--headless") # 화면 없이 동작 (--headless=new 하면 오류남, 기능은 더 최신이라고 했는데..)
    options.add_argument("--disable-gpu") # headless면 GPU 사용 안함
    options.add_argument("--window-size=1920x1080") # headless일때는 maximized가 아니라 1920x1080으로 해야 element 읽을 수 있음
    # 화면 표시 옵션
    # options.add_argument("--start-maximized") # 화면크기
    # 20221117 added
    # INFO:CONSOLE 이 계속나와서 FETAL만 표시하도록 변경
    options.add_argument("log-level=1")
    driver = webdriver.Chrome(service=service, options=options)

    # 완료 대기
    driver.implicitly_wait(DELAY_TIME)

    # URL 접근
    driver.get(EMS_LOGIN_URL)

    # ID, PW 입력
    driver.find_element(By.NAME, "userId").send_keys(EMS_USER_ID)
    driver.find_element(By.NAME, "password").send_keys(EMS_USER_PASSWORD)

    # 로그인 버튼 클릭
    driver.find_element(By.CLASS_NAME, "loginBtn").click()

    # 완료 대기
    driver.implicitly_wait(DELAY_TIME)
    # 필수 대기
    # ★ sleep 없이 implicitly_wait만 주면 데이터가 안나올때도 있음
    time.sleep(3)

    return driver


def get_ems_cpu_mem(target_resource_id, hostname, driver):
    try:
        driver.get(EMS_SVR_RSRC_CPU_MEM_URL + target_resource_id)

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        for row in soup:
            # 타입 : <class 'bs4.element.ResultSet'>
            dataset = row.select(".col-md-6 > .scheduler-border.panel-title.height50")
            results = []

            # 리소스 이름 확인 및 배열화
            for result in dataset:
                if result.select("small")[0].get_text() == "CPU 사용률":
                    results.append([hostname, result.select("small")[0].get_text(), result.select(".progress")[0]["data-percent"],])
                elif result.select("small")[0].get_text() == "메모리 사용률":
                    results.append([hostname, result.select("small")[0].get_text(), result.select(".progress")[0]["data-percent"],])

            if results: # 간헐적 데이터 미수집 발생
                insert_svr_rsrc_ems_l(results)
    except Exception as e:
        print(func_nm() + ": " + str(e))
        msgr.put_msgr_target(func_tree() + ":\n" + str(e), grp_cd="DBWX99", send_title="**" + func_nm() + "**", msgr_color="RED", send_funcnm=func_nm())
        pass


def get_ems_filesystem(target_resource_id, hostname, driver):
    try:
        driver.get(EMS_SVR_RSRC_FS_URL + target_resource_id)

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        for row in soup:
            # 기능 추가할지 말지 고민중 (영업통합"만" 총26개/페이지당25개 -> 2페이지)
            # page_count = len(row.select("#tabsZone_0 > ul.pagination"))
            # if page_count > 0 then loop
            # print(len(row.select("#tabsZone_0 > ul.pagination")))

            # 타입 : <class 'bs4.element.ResultSet'>
            summary = row.select(".table.table-hover")
            header_contents = []
            dataset_contents = []

            for content in summary:
                # # 리소스 명만 가져올때
                # # thead > tr > th .get_text()
                header = content.select("thead > tr > th > a")
                header_contents.append("호스트명")
                for x in header:
                    header_contents.append(x.get_text())

                # 값만 가져올때
                # tbody > tr > td .get_text()
                # dataset = content.select("tbody > tr > td") # 너무 세분화됨
                dataset = content.select("tbody > tr")

                for small_dataset in dataset:
                    dataset_row = []
                    for y in small_dataset:
                        if y.select("td > a"):
                            # print(y['data-grid-property'])
                            # print(y.select("a")[0].get_text())
                            dataset_row.append([hostname, y["data-grid-property"], y.select("a")[0].get_text(),])
                        elif y.select(".progress"):
                            # print(y['data-grid-property'])
                            # print(y.select(".progress")[0]['data-percent'])
                            dataset_row.append([hostname, y["data-grid-property"], y.select(".progress")[0]["data-percent"],])
                        else:
                            # print(y['data-grid-property'])
                            # print(y.get_text())
                            dataset_row.append([hostname, y["data-grid-property"], y.get_text()])
                        # print(dataset_row)
                    dataset_contents.append(dataset_row)

            # print(header_contents)
            # print("================================================")
            # # print(len(dataset_contents))
            # print(dataset_contents)
            # # for i, value in enumerate(dataset_contents):
            # #     print(value)
                    
            if dataset_contents: # 간헐적 데이터 미수집 발생
                insert_svr_fs_ems_l(dataset_contents)
    except Exception as e:
        print(func_nm() + ": " + str(e))
        # msgr.put_msgr_target(func_tree() + ":\n" + str(e), grp_cd="DBWX99", send_title="**" + func_nm() + "**", msgr_color="RED")
        pass
        

def get_status(driver):
    try:
        if driver.title:
            return 1
        else:
            return 0
    except Exception as e: # (socket.error, httplib2.CannotSendRequest):
        # print(func_nm() + ": " + str(e))
        # msgr.put_msgr_target(func_tree() + ":\n" + str(e), grp_cd="DBWX99", send_title="**" + func_nm() + "**", msgr_color="RED")
        return 0 # "Dead"


if __name__ == "__main__":
    try:
        driver = ems_login()
        while get_status(driver) == 0:
            driver = ems_login()

        while True: # 무한루프 
            server_list = list_ems_svr_id()

            # ####################################################################
            # 함수 호출로 분리
            # 한꺼번에 처리하면 수집 시간과 insert 시간이 상이하기 때문에 get_% 함수에서 즉시 insert로 함쳐둠
            # summary 조회하면 cpu, mem은 나오기 때문에 filesystem을 먼저 실행
            # 파일시스템은 1일 1회 수집하도록 로직 구현 (스케줄러 재실행 시, 구분자 초기화)

            if GATHER_FILESYSTEM_YN == "N": # 하루에 한번만 수집 (스케줄러에서 매일 재실행)
                GATHER_FILESYSTEM_YN = "Y"
                for target_server in server_list:
                    while get_status(driver) == 0: # 세션 튕기면 다시 접속
                        driver = ems_login()
                    # filesystem 정보 수집
                    get_ems_filesystem(target_server["FileSystem"], target_server["hostName"], driver)
                   # driver.quit()
            
            # msgr.put_msgr_target("get_ems_cpu_mem START")
            for target_server in server_list:
                while get_status(driver) == 0: # 세션 튕기면 다시 접속
                    driver = ems_login()
                # cpu랑 filesystem 동시에 실행하니까 자꾸 오류나는데 쪼개야되나..?
                get_ems_cpu_mem(target_server["cpu_mem"], target_server["hostName"], driver)
                # driver.quit()

            # 멀티스레드 처리시도 하였으나, 잘못된 데이터 insert로 제거 (최상단에 설명 참고)
            # with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor: # 프로그램이 설치된 호스트의 논리프로세서 개수와 맞춤
            #     futures = []

            #     for i, server in enumerate(server_list):
            #         if get_status(driver) == 0:
            #             driver = ems_login()

            #         future = executor.submit(get_ems_cpu_mem, f"p{i+1}", server["cpu_mem"], server["hostName"], driver)
            #         futures.append(future)

            #     # Wait for all threads to complete
            #     concurrent.futures.wait(futures)
            # ####################################################################
    
    except Exception as e:
        # print(file_nm() + ": " + str(e))
        msgr.put_msgr_target(str(e), grp_cd="DBWX99", send_title="**" + file_nm() + "**", msgr_color="RED", send_funcnm=func_nm())
        pass

    finally:
        driver.quit()