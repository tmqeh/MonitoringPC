import os
import time  # for sleep
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd # to merge id lists and write

# common & configuration
from cfg.config_ems import EMS_USER_ID, EMS_USER_PASSWORD, DELAY_TIME, EMS_LOGIN_URL, EMS_SERVER_LIST_SUMMARY_URL_ID, EMS_SERVER_LIST_SUMMARY_URL, EMS_SERVER_RESOURE_URL_HEADER, EMS_SERVER_RESOURE_URL_TAIL, EMS_SERVER_FILESYSTEM_RESOURE_URL
import cmn.common_msgr as msgr
from cmn.common import get_cur_func_nm as func_nm, get_cur_file_nm as file_nm, get_func_tree as func_tree
from cmn.common_db import monPC
from cmn.common_sql import get_string, get_size_kb_bps

# EMS 세션 맺으면 기존 세션이 종료되는 이슈 있음
# 해결 방법은 사용자 여러개 쓰던지, 아예 사용하지 않는 계정 이용
# EMS 자체에 동시 접속 제한이 있는 것으로 판단됨

# 딜레이 (단위 : 초)
# implicitly_wait : 지정한 시간 이전에 브라우저 파싱이 완료되면, 이후의 시간은 기다리지 않고 바로 다음 코드를 실행
# sleep : 지정한 시간만큼 반드시 기다리고(쉬고) 다음 코드를 실행

"""
select 설명 : https://pythonblog.co.kr/coding/11/
※ find 보다 select 지향

함수설명
select_one() -> 1개만 조회
select() -> 전체 조회(리스트)

태그설명
.   -> classname
#   -> id
>   -> 태그 트리 (자식태그)
[]  -> 속성
X.Y -> 태그이름.클래스이름

※ class에 띄워쓰기가 있으면 전부 "." 처리하면됨
"""


def insert_ems_svr_list(args):
    conn = monPC(func_nm())
    sqlTxt = ""

    # list to list
    for row_dataset in args:
        group_path      = ""
        hostName        = ""
        ipAddress       = ""
        vendor          = ""
        osType          = ""
        server_type     = ""
        cpu_use_pct     = ""
        mem_use_pct     = ""
        max_IO_rate_pct = ""
        fs_use_pct      = ""
        net_rcv_bps_kb  = ""
        net_tsm_bps_kb  = ""
        nst_stat_cnt    = ""
        priority        = ""
        
        for data_list in row_dataset:  # for putting comma logic, enumerate is necessary
            # value transform to fit on insert syntax
            if data_list[0] == "groupPath":
                group_path = get_string(data_list[1].lstrip().rstrip().replace("\n", ""), "l")
            elif data_list[0] == "name":
                hostName = get_string(data_list[1].lstrip().rstrip(), "l")
            elif data_list[0] == "ipAddress":
                ipAddress = get_string(data_list[1], "l")
            elif data_list[0] == "vendor":
                vendor = get_string(data_list[1], "l")
            elif data_list[0] == "osType":
                osType = get_string(data_list[1].lstrip().rstrip(), "l")
            elif data_list[0] == "type":
                server_type = get_string(data_list[1].lstrip().rstrip(), "l")
            elif data_list[0] == "cpuUtilization":
                cpu_use_pct = get_string(data_list[1].replace("%", "").replace("-", ""), "l")
            elif data_list[0] == "memoryUtilization":
                mem_use_pct = get_string(data_list[1].replace("%", "").replace("-", ""), "l")
            elif data_list[0] == "maxIORate":
                max_IO_rate_pct = get_string(data_list[1].replace("%", "").replace("-", ""), "l")
            elif data_list[0] == "fileSystemUtilization":
                fs_use_pct = get_string(data_list[1].replace("%", "").replace("-", ""), "l")
            elif data_list[0] == "networkInterfacesRxTraffic":
                net_rcv_bps_kb = get_size_kb_bps(data_list[1])
            elif data_list[0] == "networkInterfacesTxTraffic":
                net_tsm_bps_kb = get_size_kb_bps(data_list[1])
            elif data_list[0] == "netstatCount":
                nst_stat_cnt = get_string(data_list[1].lstrip().rstrip().replace("-", ""), "l")
            elif data_list[0] == "priority":
                priority = get_string(data_list[1], "l")

            RGPR_ID = "insert_ems_svr_list"
            RGST_DTM = "getdate()"
            CollectDT = "convert(varchar,getdate(),112)"
            CollectHH = "substring(convert(varchar,getdate(),108),1,2)"
            CollectMS = "substring(convert(varchar,getdate(),108),4,2)"

        # set bulk data query
        sqlTxt = sqlTxt + "MERGE [MonitoringDB].[dbo].[TB_Svr_List_EMS_M] AS T \n"
        sqlTxt = sqlTxt + "USING (SELECT " + hostName + " AS hostName          \n"
        sqlTxt = sqlTxt + "      ) AS S                                        \n"
        sqlTxt = sqlTxt + "   ON T.hostName = S.hostName                       \n"
        sqlTxt = sqlTxt + " WHEN MATCHED THEN UPDATE                           \n"
        sqlTxt = sqlTxt + " SET                                                \n"
        sqlTxt = sqlTxt + "   -- hostName     =   " + hostName              + "\n"
        sqlTxt = sqlTxt + "     group_path      = " + group_path            + "\n"
        sqlTxt = sqlTxt + "   , ipAddress       = " + ipAddress             + "\n"
        sqlTxt = sqlTxt + "   , vendor          = " + vendor                + "\n"
        sqlTxt = sqlTxt + "   , osType          = " + osType                + "\n"
        sqlTxt = sqlTxt + "   , server_type     = " + server_type           + "\n"
        sqlTxt = sqlTxt + "   , cpu_use_pct     = " + cpu_use_pct           + "\n"
        sqlTxt = sqlTxt + "   , mem_use_pct     = " + mem_use_pct           + "\n"
        sqlTxt = sqlTxt + "   , max_IO_rate_pct = " + max_IO_rate_pct       + "\n"
        sqlTxt = sqlTxt + "   , fs_use_pct      = " + fs_use_pct            + "\n"
        sqlTxt = sqlTxt + "   , net_rcv_bps_kb  = " + net_rcv_bps_kb        + "\n"
        sqlTxt = sqlTxt + "   , net_tsm_bps_kb  = " + net_tsm_bps_kb        + "\n"
        sqlTxt = sqlTxt + "   , nst_stat_cnt    = " + nst_stat_cnt          + "\n"
        sqlTxt = sqlTxt + "   , priority        = " + priority              + "\n"
        sqlTxt = sqlTxt + "   , MDFPR_ID        = 'insert_ems_svr_list'        \n"
        sqlTxt = sqlTxt + "   , MDF_DTM         = getdate()                    \n"
        sqlTxt = sqlTxt + " WHEN NOT MATCHED THEN INSERT                       \n"
        sqlTxt = sqlTxt + " (   group_path ,                                   \n"
        sqlTxt = sqlTxt + "     hostName ,                                     \n"
        sqlTxt = sqlTxt + "     ipAddress ,                                    \n"
        sqlTxt = sqlTxt + "     vendor ,                                       \n"
        sqlTxt = sqlTxt + "     osType ,                                       \n"
        sqlTxt = sqlTxt + "     server_type ,                                  \n"
        sqlTxt = sqlTxt + "     cpu_use_pct ,                                  \n"
        sqlTxt = sqlTxt + "     mem_use_pct ,                                  \n"
        sqlTxt = sqlTxt + "     max_IO_rate_pct ,                              \n"
        sqlTxt = sqlTxt + "     fs_use_pct ,                                   \n"
        sqlTxt = sqlTxt + "     net_rcv_bps_kb ,                               \n"
        sqlTxt = sqlTxt + "     net_tsm_bps_kb ,                               \n"
        sqlTxt = sqlTxt + "     nst_stat_cnt ,                                 \n"
        sqlTxt = sqlTxt + "     priority ,                                     \n"
        sqlTxt = sqlTxt + "     RGPR_ID ,                                      \n"
        sqlTxt = sqlTxt + "     RGST_DTM                                       \n"
        sqlTxt = sqlTxt + " ) VALUES                                           \n"
        sqlTxt = sqlTxt + " (   " + group_path + " ,                           \n"
        sqlTxt = sqlTxt + "     " + hostName + " ,                             \n"
        sqlTxt = sqlTxt + "     " + ipAddress + " ,                            \n"
        sqlTxt = sqlTxt + "     " + vendor + " ,                               \n"
        sqlTxt = sqlTxt + "     " + osType + " ,                               \n"
        sqlTxt = sqlTxt + "     " + server_type + " ,                          \n"
        sqlTxt = sqlTxt + "     " + cpu_use_pct + " ,                          \n"
        sqlTxt = sqlTxt + "     " + mem_use_pct + " ,                          \n"
        sqlTxt = sqlTxt + "     " + max_IO_rate_pct + " ,                      \n"
        sqlTxt = sqlTxt + "     " + fs_use_pct + " ,                           \n"
        sqlTxt = sqlTxt + "     " + net_rcv_bps_kb + " ,                       \n"
        sqlTxt = sqlTxt + "     " + net_tsm_bps_kb + " ,                       \n"
        sqlTxt = sqlTxt + "     " + nst_stat_cnt + " ,                         \n"
        sqlTxt = sqlTxt + "     " + priority + " ,                             \n"
        sqlTxt = sqlTxt + "     'insert_ems_svr_list'  ,                       \n"
        sqlTxt = sqlTxt + "     getdate()                                      \n"
        sqlTxt = sqlTxt + " );                                                 \n"

        try:
            # print(sqlTxt)
            conn.execute(sqlTxt)

        except Exception as e:
            # print(func_nm() + ": " + str(e))
            msgr.put_msgr_target(func_tree() + ":\n" + str(e), grp_cd="DBWX99", send_title="**" + func_nm() + "**", msgr_color="RED", send_funcnm=func_nm())
            # print(row_dataset)
            # print(sqlTxt)
            # return 0
            pass

        finally:
            sqlTxt = ""
            group_path = ""
            hostName = ""
            ipAddress = ""
            vendor = ""
            osType = ""
            server_type = ""
            cpu_use_pct = ""
            mem_use_pct = ""
            max_IO_rate_pct = ""
            fs_use_pct = ""
            net_rcv_bps_kb = ""
            net_tsm_bps_kb = ""
            nst_stat_cnt = ""
            priority = ""

        # except last one, put comma and new line char
        # if i < len(args)-1 :
        #     listToStr = listToStr + ',\n'
        # sqlTxt = sqlTxt  + listToStr

    # even MS-SQL need it (MUST)
    # 루프 마지막에 위치시켜서 commit을 한번만 실행하게 작성
    conn.commit()
    # return 1 # when it call this function return is needed to check
    conn.close()


def insert_ems_svr_id(args):
    conn = monPC(func_nm())
    sqlTxt = ""

    # list to list
    for row_dataset in args:
        hostName   = get_string(row_dataset["hostname"],'l')
        cpu_mem    = get_string(row_dataset["cpu_mem"],'l')
        FileSystem = get_string(row_dataset["filesystem"],'l')

        # set bulk data query
        sqlTxt = sqlTxt + "MERGE [MonitoringDB].[dbo].[TB_Svr_Rsrc_ID_EMS_M] AS T \n"
        sqlTxt = sqlTxt + "USING (SELECT " + hostName + " AS hostName          \n"
        sqlTxt = sqlTxt + "      ) AS S                                        \n"
        sqlTxt = sqlTxt + "   ON T.hostName = S.hostName                       \n"
        sqlTxt = sqlTxt + " WHEN MATCHED THEN UPDATE                           \n"
        sqlTxt = sqlTxt + " SET                                                \n"
        sqlTxt = sqlTxt + "   -- hostName     = " + hostName                + "\n"
        sqlTxt = sqlTxt + "     cpu_mem       = " + cpu_mem                 + "\n"
        sqlTxt = sqlTxt + "   , FileSystem    = " + FileSystem              + "\n"
        sqlTxt = sqlTxt + "   , MDFPR_ID      = 'insert_ems_svr_id'            \n"
        sqlTxt = sqlTxt + "   , MDF_DTM       = getdate()                      \n"
        sqlTxt = sqlTxt + " WHEN NOT MATCHED THEN INSERT                       \n"
        sqlTxt = sqlTxt + " (   hostName ,                                     \n"
        sqlTxt = sqlTxt + "     cpu_mem ,                                      \n"
        sqlTxt = sqlTxt + "     FileSystem ,                                   \n"
        sqlTxt = sqlTxt + "     RGPR_ID ,                                      \n"
        sqlTxt = sqlTxt + "     RGST_DTM                                       \n"
        sqlTxt = sqlTxt + " ) VALUES                                           \n"
        sqlTxt = sqlTxt + " (   " + hostName + " ,                             \n"
        sqlTxt = sqlTxt + "     " + cpu_mem + " ,                              \n"
        sqlTxt = sqlTxt + "     " + FileSystem + " ,                           \n"
        sqlTxt = sqlTxt + "     'insert_ems_svr_id'  ,                         \n"
        sqlTxt = sqlTxt + "     getdate()                                      \n"
        sqlTxt = sqlTxt + " );                                                 \n"

        try:
            # print(sqlTxt)
            conn.execute(sqlTxt)

        except Exception as e:
            # print(func_nm() + ": " + str(e))
            msgr.put_msgr_target(func_tree() + ":\n" + str(e), grp_cd="DBWX99", send_title="**" + func_nm() + "**", msgr_color="RED", send_funcnm=func_nm())
            # print(row_dataset)
            # print(sqlTxt)
            # return 0

        finally:
            sqlTxt = ""
            hostName = ""
            cpu_mem = ""
            FileSystem = ""

        # except last one, put comma and new line char
        # if i < len(args)-1 :
        #     listToStr = listToStr + ',\n'
        # sqlTxt = sqlTxt  + listToStr

    # even MS-SQL need it (MUST)
    # 루프 마지막에 위치시켜서 commit을 한번만 실행하게 작성
    conn.commit()
    # return 1 # when it call this function return is needed to check
    conn.close()


def ems_login():
    # 크롬 드라이버 위치 지정
    # CHROME_DRIVER_PATH = "C:\\chromedriver_win32\\chromedriver.exe"
    # 크롬 버전 올라 갈 때 마다 버전오류 발생하여 시작할때 설치 강제 실행
    # 경로 불필요
    os.system("taskkill /F /IM chromedriver.exe") # ChromeDriverManager().install() 로 생성되는 프로세스 강제 종료
    os.system("taskkill /F /IM chrome.exe") # ChromeDriverManager().install() 로 생성되는 프로세스 강제 종료
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("--disable-gpu")
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


def get_ems_svr_fs_id(summary_id, driver):
    dataset_contents = []
    for each_svr_id in summary_id:
        dataset_row = []
        driver.get(EMS_SERVER_FILESYSTEM_RESOURE_URL + each_svr_id[1])

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        for row in soup:
            # print(row.select("#serverFileSystemZone > a"))
            svr_fs_id = row.select("#serverFileSystemZone > a[href]")[0]["href"].split("/")[3]
            dataset_row.append(each_svr_id[0])
            dataset_row.append(svr_fs_id)
        dataset_contents.append(dataset_row)
    return dataset_contents


def get_ems_svr_list_and_id(target_resource_id, driver):
    driver.get(EMS_SERVER_LIST_SUMMARY_URL + target_resource_id)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    page_count = 1  # len(row.select("#tabsZone_0 > div > div > ul > li"))
    for row in soup:
        page_count = len(row.select("#tabsZone_0 > div > div > ul > li"))

    header_contents = [] # for DEBUG
    summary_contents = []
    resource_id_contents = []

    for i in range(page_count):
        driver.get(EMS_SERVER_RESOURE_URL_HEADER + str(i + 1) + EMS_SERVER_RESOURE_URL_TAIL)

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        for row in soup:
            # if page_count > 0 then loop # for DEBUG
            # break

            # 타입 : <class 'bs4.element.ResultSet'>
            summary = row.select("#tabsZone_0 > div > div > table")

            for content in summary:
                # # 리소스 명만 가져올때
                # # thead > tr > th .get_text()
                headers = content.select("thead > tr > th > a")

                for header in headers: # for DEBUG
                    header_contents.append(header.get_text())

                # 값만 가져올때
                # tbody > tr > td .get_text()
                # dataset = content.select("tbody > tr > td") # 너무 세분화됨
                dataset = content.select("tbody > tr")

                for small_dataset in dataset:
                    summary_row = []
                    resource_id_row = []
                    for row in small_dataset:
                        if row.select("td > a"):
                            if row["data-grid-property"] == "name": # cpu_mem id 가져오는 로직 병합
                                # print(row.select("a")[0].get_text(), row.select("a[href]")[0]["href"].split("/")[3])
                                resource_id_row.append(row.select("a")[0].get_text().strip())
                                resource_id_row.append(row.select("a[href]")[0]["href"].split("/")[3])
                            # print(row['data-grid-property'])
                            # print(row.select("a")[0].get_text())
                            summary_row.append([row["data-grid-property"], row.select("a")[0].get_text()])
                        elif row.select(".progress"):
                            # print(row['data-grid-property'])
                            # print(row.select(".progress")[0]['data-percent'])
                            summary_row.append([row["data-grid-property"], row.select(".progress")[0]["data-percent"],])
                        else:
                            # print(row['data-grid-property'])
                            # print(row.get_text())
                            summary_row.append([row["data-grid-property"], row.get_text()])
                        # print(summary_row)
                            
                    summary_contents.append(summary_row)
                    resource_id_contents.append(resource_id_row)

            # DEBUG
            # print(header_contents)
            # # print("================================================")
            # # print(len(summary_contents))
            # for i, value in enumerate(summary_contents):
            #     print(value)
            # # for i, value in enumerate(summary_contents):
            # #     if (i+1)/25 == 1.0:
            # #         print(value)
            # print(summary_contents)

    # print("summary_contents=========================================")
    # for data in summary_contents:
    #     print(data[1][1].strip())

    # print("resource_id_contents=========================================")
    # for data in resource_id_contents:
    #     print(data)

    return summary_contents, resource_id_contents


def merge_resource_id(cpu_mem_id, filesystem_id):
    df_to_list = []
    df_cpu_mem = pd.DataFrame(cpu_mem_id, columns=["hostname", "cpu_mem"]).set_index("hostname")
    df_filesystem = pd.DataFrame(filesystem_id, columns=["hostname", "filesystem"]).set_index("hostname")
    df_merge = pd.merge(left=df_cpu_mem, right=df_filesystem, how="inner", on="hostname")

    for row in df_merge.itertuples():
        row_data = {"hostname": row.Index, "cpu_mem": row.cpu_mem, "filesystem": row.filesystem}
        df_to_list.append(row_data)
    
    return df_to_list


if __name__ == "__main__":
    try:
        driver = ems_login()

        # ####################################################################
        # 함수 호출로 분리
        """
        get_ems_svr_list_and_id 에서 server_summary 내용 가져오고, cpu_mem_id 가져와서
            insert_ems_svr_list (server_summary) 작업 돌리고 # 이걸 마지막에 하면 거의 동시에 insert 작업 진행 됨
            get_ems_svr_fs_id 에서 cpu_mem_id를 이용해서 filesystem_id 가져와서
                cpu_mem_id & filesystem_id merge 작업 해주고
                    insert_ems_svr_id   (resource_id)   
        """
        # 서버 리요약 정보 수집 + CPU_MEM ID 수집 후, INSERT
        server_summary, cpu_mem_id = get_ems_svr_list_and_id(EMS_SERVER_LIST_SUMMARY_URL_ID, driver)
        insert_ems_svr_list(server_summary)

        # 파일시스템 ID 수집
        filesystem_id = get_ems_svr_fs_id(cpu_mem_id, driver)

        # CPU_MEM ID & 파일시스템 ID MERGE 후, INSERT
        resource_id = merge_resource_id(cpu_mem_id, filesystem_id)
        insert_ems_svr_id(resource_id)
        # ####################################################################

    except Exception as e:
        # print(file_nm() + ": " + str(e))
        msgr.put_msgr_target(str(e), grp_cd="DBWX99", send_title="**" + file_nm() + "**", msgr_color="RED", send_funcnm=func_nm())

    finally:
        driver.quit()