import os
import time # for sleep
import re # for finding pattern
import requests
import datetime

# crawling
import pandas as pd # to merge id lists and write
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

# common & configuration 
from cfg.config_itsm import ITSM_REMAPPING, DWP_USER_ID, DWP_USER_PASSWORD, DELAY_TIME, GET_ITSM_URL, ITSM_OFFSET_SIZE, ITSM_MAX_CNT_SIZE, ITSM_OFFSET_SIZE, ITSM_MAX_CNT_SIZE, IGNORE_GRP, PART_SVC_MAPPING, DEFAULT_GROUP_CD,  ITSM_LOGIN_URL
import cmn.common_msgr as msgr
from cmn.common import get_cur_func_nm as func_nm, get_cur_file_nm as file_nm, get_func_tree as func_tree
from cmn.common_db import monPC
from cmn.common_itsm import get_itsm_payload # SEARCH_CL_CD : 01-정상, 02-반려
from cmn.common_datetime import YMDHMS

# 딜레이 (단위 : 초)
# implicitly_wait : 지정한 시간 이전에 브라우저 파싱이 완료되면, 이후의 시간은 기다리지 않고 바로 다음 코드를 실행
# sleep : 지정한 시간만큼 반드시 기다리고(쉬고) 다음 코드를 실행

# 시작일자는 고민 중 (현재 60일 전까지)
ITSM_REQ_DT        = (datetime.datetime.now() - datetime.timedelta(days=60)).strftime("%Y-%m-%d")
ITSM_SRCH_ST_DATE  = (datetime.datetime.now() - datetime.timedelta(days=60)).strftime("%Y%m%d")+"000000" 
ITSM_SRCH_END_DATE = YMDHMS
# os.environ["WDM_SSL_VERIFY"] = "0" # ChromeDriverManager().install() SSL 인증 오류 해소

def itsm_login():
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

    print("★ ★ ★ ★ ★  드라이브 생성 완료 ★ ★ ★ ★ ★ ★ ★ ")

    # ======================================================
    # ITSM 전산의뢰 
    # ======================================================
    driver.get(ITSM_LOGIN_URL)
    
    # ID, PW 입력
    # driver.find_element(By.ID, "user_id").send_keys(DWP_USER_ID)
    # driver.find_element(By.ID, "user_pwd").send_keys(DWP_USER_PASSWORD)

    # 계열사 선택
    # Select(driver.find_element(By.NAME, "search_type")).select_by_value("023400")
    
    # 로그인 버튼 클릭
    # driver.find_element(By.CLASS_NAME, "btn_login").click()

    # 완료 대기
    # driver.implicitly_wait(DELAY_TIME)
    # 필수 대기
    # ★ sleep 없이 implicitly_wait만 주면 데이터가 안나올때도 있음
    time.sleep(3)
    
    return driver
    
    
def list_itsm_xml(driver, SEARCH_CL_CD="01"):

    cookies = driver.get_cookies()
    cookies_dict = {cookie["name"]: cookie["value"] for cookie in cookies}

    try:
        payload = get_itsm_payload(ITSM_OFFSET_SIZE, ITSM_MAX_CNT_SIZE, ITSM_SRCH_ST_DATE, ITSM_SRCH_END_DATE, SEARCH_CL_CD)

        # 헤더 없어도 됨
        # 쿠키 있어야됨
        response = requests.post(GET_ITSM_URL, data=payload, cookies=cookies_dict) # headers=ITSM_HEADERS
        result = BeautifulSoup(response.text, features="xml")

        data_set = []
        df_xml = []
        
        column_list = list(ITSM_REMAPPING.values())  # 컬럼 리스트 생성

        for row in result.findAll('Row'):
            row_set = {}  # 각 행에 대한 데이터를 담을 딕셔너리를 생성
            for col in row.findAll('Col'):
                col_id = ITSM_REMAPPING.get(col["id"], col["id"])  # col['id']에 해당하는 한글로 매핑된 값을 가져옴
                if col_id not in column_list:  # 만약 컬럼 리스트에 해당하지 않으면 skip
                    continue
                if any(item in col_id for item in ["offset", "max_cnt", "rmn_cnt", "tot_cnt"]):
                    continue
                if any(item in col["id"] for item in ["time"]):
                    row_set[col_id] = datetime.datetime.strptime(col.text[0:14], "%Y%m%d%H%M%S").strftime("%Y-%m-%d") # 과거 시간데이터에 timestamp가 있어 3자리 절삭
                else:
                    row_set[col_id] = col.text
            if '순번' in row_set:  # '순번' 값이 있는 경우에만 추가
                data_set.append(row_set)

        df_xml = pd.DataFrame(data_set, columns=column_list) # column_list 없으면 데이터 없을 때 열이 통째로 누락 발생함
        return df_xml

        # msgr.put_msgr_target("download finished", "DBWX99", send_title="itsm 요청리스트", msgr_color="GREEN")
    except Exception as e:
        # print(func_nm() + ": " + str(e))
        msgr.put_msgr_target(func_tree() + ":\n" + str(e), grp_cd="DBWX99", send_title="**" + func_nm() + "**", msgr_color="RED", send_funcnm=func_nm())
        pass


def insert_itsm_request_log(args):
    conn = monPC(func_nm())
    # content = "" # 단일 전송에서 담당별 전송으로 변경
    # 문자 전송 그룹
    GROUP_CONTENT = {key : "" for key in PART_SVC_MAPPING}
    
    sqlTxt = """
    MERGE dbo.TB_ITSM_REQ_L AS A
    USING (SELECT %s as REQ_NO, %s as STEP
            ) AS B
        ON (A.REQ_NO = B.REQ_NO
            )
    WHEN NOT MATCHED THEN
        INSERT (  REQ_NO, 
                  REQ_TP_NM, DTL_REQ_TP_NM, TIT, SVC_CATALOG, 
                  REQPR_NM, REQPR_ID, REQ_DPT_NM, WRKR_ID,
                  REQ_DT, ST_SCHE_DT, CMPL_HOPE_DT, CMPL_SCHE_DT, PRCS_ST_DT, PRCS_CMPL_DT,
                  STEP, NEXT_STAT, CHRGPR_ID, PRGRS_RT_PCT, WRK_DYS, PRCS_TM, DLAY_DYS, STFDG,
                  RCEPT_CMPL_DT, STFDG_EVL_DT, FNL_CMPL_DT, ALL_WRKR_ID, MGM_CSR_NO, TEAM_NM,
                  PUB_HOPE_DT, PUB_ST_DT, PUB_CMPL_DT,
                  EXMNR_ID, EXMN_CMPL_DT, EXMN_TM,
                  RGPR_ID, RGST_DTM
                ) VALUES
                ( %s
                , %s, %s, %s, %s
                , %s, %s, %s, %s
                , %s, %s, %s, %s, %s, %s
                , %s, %s, %s, %s, %s, %s, %s, %s
                , %s, %s, %s, %s, %s, %s
                , %s, %s, %s
                , %s, %s, %s
                , 'insert_itsm_request_log', getdate()
                )
    WHEN MATCHED AND A.STEP <> B.STEP THEN
        UPDATE SET    A.REQ_TP_NM     = %s
                    , A.DTL_REQ_TP_NM = %s
                    , A.TIT           = %s
                    , A.SVC_CATALOG   = %s
                    , A.REQPR_NM      = %s
                    , A.REQPR_ID      = %s
                    , A.REQ_DPT_NM    = %s
                    , A.WRKR_ID       = %s
                    , A.REQ_DT        = %s
                    , A.ST_SCHE_DT    = %s
                    , A.CMPL_HOPE_DT  = %s
                    , A.CMPL_SCHE_DT  = %s
                    , A.PRCS_ST_DT    = %s
                    , A.PRCS_CMPL_DT  = %s
                    , A.STEP          = %s
                    , A.NEXT_STAT     = %s
                    , A.CHRGPR_ID     = %s
                    , A.PRGRS_RT_PCT  = %s
                    , A.WRK_DYS       = %s
                    , A.PRCS_TM       = %s
                    , A.DLAY_DYS      = %s
                    , A.STFDG         = %s
                    , A.RCEPT_CMPL_DT = %s
                    , A.STFDG_EVL_DT  = %s
                    , A.FNL_CMPL_DT   = %s
                    , A.ALL_WRKR_ID   = %s
                    , A.MGM_CSR_NO    = %s
                    , A.TEAM_NM       = %s
                    , A.PUB_HOPE_DT   = %s
                    , A.PUB_ST_DT     = %s
                    , A.PUB_CMPL_DT   = %s
                    , A.EXMNR_ID      = %s
                    , A.EXMN_CMPL_DT  = %s
                    , A.EXMN_TM       = %s
                    , A.MDFPR_ID      = 'update_itsm_request_log'
                    , A.MDF_DTM       = getdate()
    ;
    """
    
    try:
        for index, row in args.iterrows(): # each row
            # print("======================================")
            # print(index)
            # print(row)
            # 숫자는 %d, 문자는 %s를 사용
            # CollectDt       = "convert(varchar,getdate(),112)"
            req_no         = row["요청번호"]

            req_tp_nm      = row["요청유형"]
            dtl_req_tp_nm  = row["상세요청유형"]
            tit            = row["제목"]
            svc_catalog    = row["서비스카탈로그"]
            reqpr_nm       = row["요청자"]
            reqpr_id       = row["요청자사번"]
            req_dpt_nm     = row["요청부서"]
            wrkr_id        = row["작업자"]
            req_dt         = row["요청일"]
            st_sche_dt     = row["시작예정일"]
            cmpl_hope_dt   = row["완료희망일"]
            cmpl_sche_dt   = row["완료예정일"]
            prcs_st_dt     = row["처리시작일"]
            prcs_cmpl_dt   = row["처리완료일"]
            step           = row["단계"]
            next_stat      = row["다음상태"]
            chrgpr_id      = row["담당자"]
            prgrs_rt_pct   = row["진척율(%)"]
            wrk_dys        = row["작업일수"]
            prcs_tm        = row["처리시간"]
            dlay_dys       = row["지연일수"]
            stfdg          = row["만족도"]
            rcept_cmpl_dt  = row["접수완료일"]
            stfdg_evl_dt   = row["만족도평가일"]
            fnl_cmpl_dt    = row["최종완료일"]
            all_wrkr_id    = row["전체작업자"]
            mgm_csr_no     = row["관리CSR번호"]
            team_nm        = row["IS팀"]
            pub_hope_dt    = '' # row["배포희망일"]
            pub_st_dt      = row["배포시작일"]
            pub_cmpl_dt    = row["배포완료일"]
            exmnr_id       = row["검토자"]
            exmn_cmpl_dt   = row["검토완료일"]
            exmn_tm        = '' # row["검토시간"]
            # rgpr_id           = "insert_itsm_request_log"
            # rgst_dtm          = "getdate()"
            # mdfpr_id          = "update_itsm_request_log"
            # mdf_dtm           = "getdate()"

            # 접수단계만 알림이 오도록 하였으나 조절 가능 
            # => 담당자가 접수해야 알람이 가서, 요청자의 요청승인 또는 현업의 검토승인이 완료될때 문자가도록 변경 
            # (단, get_itsm_request_status_and_send_alert 도 같이 수정 필요)
            # "검토승인" 추가 (next_step이 "접수"인 case)
            # "요청승인" 추가 (next_step이 "접수"인 case)
            # print("=======================================================")
            # print(step)
            # print(next_stat)
            
            
            if (any(item in step for item in ["요청승인", "검토승인"]) and "요청접수" in next_stat) or ("접수승인" in step and any(item in step for item in ["처리결과", "작업계획"])): 
            # if ("승인" in step and "접수" in next_stat) or ("접수승인" in step and "처리" in next_stat):
            # if any(item in step for item in ["요청승인", "검토승인", "접수"]):

                # 무시할 항목인지 확인
                if any(ignored_part in svc_catalog for ignored_part in IGNORE_GRP):
                    # print("ignore target : " + svc_catalog)
                    continue # 정상동작 확인 완료

                part_nm = svc_catalog.split(">")[0].replace("IT_","").replace(" Part","")
                # 파트에 해당하는 그룹 코드 찾기
                grp_cd = None
                for group_cd, parts in PART_SVC_MAPPING.items():

                    if svc_catalog in parts:
                        grp_cd = group_cd
                        break
                    else:
                        grp_cd = DEFAULT_GROUP_CD # 신규 카테고리 발생으로 인한 누락 체크
                
                prev_step = get_itsm_request_status_and_send_alert(conn, req_no, step)

                if prev_step is not None and grp_cd is not None:
                    if any(item in step for item in ["요청승인", "검토승인"]) and "요청접수" in next_stat:
                        content = "**" + req_tp_nm + "(" + dtl_req_tp_nm + ")" + "**\n"
                    if "접수승인" in step and "처리결과" in next_stat:
                        content = "[ITSM 작업]() " + req_tp_nm + "(" + dtl_req_tp_nm + ")" + "\n"
                    
                    content = content + "# 내용 : " + tit + "\n"
                    content = content + "# 요청 : " + reqpr_nm + " (" + req_dpt_nm + ")" + "\n"

                    if "접수승인" in step and any(item in step for item in ["처리결과", "작업계획"]) in next_stat:
                        content = content + "# 작업 : " + wrkr_id + "\n"
                        
                    content += "# 일자 : " + cmpl_hope_dt + "\n"
                    content = content + "\n" # 여러개 발생 시, 개행 시켜서 보기 편하게

                    GROUP_CONTENT[grp_cd] += str(content)
            # print(req_no)
            conn.execute(sqlTxt
                            ######## for select
                        ,(req_no, step
                            ########### for insert
                        , req_no,
                            req_tp_nm, dtl_req_tp_nm, tit, svc_catalog, 
                            reqpr_nm, reqpr_id, req_dpt_nm, wrkr_id,
                            req_dt, st_sche_dt, cmpl_hope_dt, cmpl_sche_dt, prcs_st_dt, prcs_cmpl_dt,
                            step, next_stat, chrgpr_id, prgrs_rt_pct, wrk_dys, prcs_tm, dlay_dys, stfdg,
                            rcept_cmpl_dt, stfdg_evl_dt, fnl_cmpl_dt, all_wrkr_id, mgm_csr_no, team_nm,
                            pub_hope_dt, pub_st_dt, pub_cmpl_dt,
                            exmnr_id, exmn_cmpl_dt, exmn_tm
                            ######### for update
                        , req_tp_nm, dtl_req_tp_nm, tit, svc_catalog, 
                            reqpr_nm, reqpr_id, req_dpt_nm, wrkr_id,
                            req_dt, st_sche_dt, cmpl_hope_dt, cmpl_sche_dt, prcs_st_dt, prcs_cmpl_dt,
                            step, next_stat, chrgpr_id, prgrs_rt_pct, wrk_dys, prcs_tm, dlay_dys, stfdg,
                            rcept_cmpl_dt, stfdg_evl_dt, fnl_cmpl_dt, all_wrkr_id, mgm_csr_no, team_nm,
                            pub_hope_dt, pub_st_dt, pub_cmpl_dt,
                            exmnr_id, exmn_cmpl_dt, exmn_tm))

        # if content: # 단일 전송에서 담당별 전송으로 변경
        #     msgr.put_msgr_target(content.rstrip("\n"), grp_cd="DBWX99", send_title="**ITSM 신규요청**", msgr_color="YELLOW")
        
        # 각 그룹별로 메시지 전송
        # 임시 중지 
        # ★ 운영 전환 시, 이부분 주석 해제 필요 
        # DBA만 받기 위해서는 grp_cd 또는 PART_SVC_MAPPING 에서 "데이터베이스" 만 조건 처리하여 전송
        for grp_cd, content in GROUP_CONTENT.items():
            if content:
                if grp_cd == "DBWX04": # DBA꺼만 시범 운영
                    # msgr.put_msgr_target(content.rstrip("\n"), grp_cd)
                    msgr.put_msgr_target(content.rstrip("\n"), "DBWX04", send_title="ITSM 요청", msgr_color="Good", send_funcnm=func_nm())
                # else : # for debugging
                    # msgr.put_msgr_target(content.rstrip("\n"), "DBWX99", send_title="**전산의뢰**", msgr_color="YELLOW")
                # msgr.put_msgr_target(content.rstrip("\n"), grp_cd=grp_cd, send_title="**ITSM 신규요청**", msgr_color="YELLOW")
        
        # even MS-SQL need it (MUST)
        conn.commit()

    except Exception as e:
        # print(func_nm() + ": " + str(e))
        msgr.put_msgr_target(func_tree() + ":\n" + str(e), grp_cd="DBWX99", send_title="**" + func_nm() + "**", msgr_color="RED", send_funcnm=func_nm())
        # pass

    finally:
        if conn:
            conn.close()


def delete_itsm_reject_log(args):
    conn = monPC(func_nm())

    sqlTxt = """
             DELETE dbo.TB_ITSM_REQ_L
              WHERE REQ_NO = %s
             """          
    try:
        for index, row in args.iterrows(): # each row
                # 숫자는 %d, 문자는 %s를 사용
                req_no         = row["요청번호"]
                conn.execute(sqlTxt
                             ######## for delete
                            ,(req_no))
        conn.commit()

    except Exception as e:
        # print(func_nm() + ": " + str(e))
        msgr.put_msgr_target(func_tree() + ":\n" + str(e), grp_cd="DBWX99", send_title="**" + func_nm() + "**", msgr_color="RED", send_funcnm=func_nm())
        # print(req_no)
        # pass

    finally:
        if conn:
            conn.close()


def list_itsm_db_data():
    conn = monPC(func_nm())

    # 삭제 전에 들어온 데이터가 있을 수 있으나 정상건 범위 조회
    dataSet = None
    sqlTxt  = """
              SELECT REQ_NO, STEP
                FROM dbo.TB_ITSM_REQ_L
               WHERE REQ_DT >= %s
              """
    result = []
    try:
        conn.execute(sqlTxt,(ITSM_REQ_DT))
        fetchData = conn.fetchall()

        if fetchData:
            result = [((value.encode('ISO-8859-1').decode('euc-kr') if value is not None else None) \
                            for i, value in enumerate(row)) for row in fetchData]
            dataSet = pd.DataFrame(result, columns=["요청번호", "단계"])
            
            return dataSet

    except Exception as e:
        # print(func_nm() + ": " + str(e))
        msgr.put_msgr_target(func_tree() + ":\n" + str(e), grp_cd="DBWX99", send_title="[Error] ITSM Alert", msgr_color="Attention", send_funcnm=func_nm())
        # print(req_no)
        # pass

    finally:
        if conn:
            conn.close()


def get_itsm_request_status_and_send_alert(conn, req_no, step): # row["요청번호"], row["단계"]

    sqlTxt = """
    SELECT STEP
      FROM TB_ITSM_REQ_L (nolock) 
     WHERE REQ_NO = %s
            """
    
    errCheck = ""

    try:
        result = str("".join(conn.query(sqlTxt, req_no)[0])).encode("ISO-8859-1").decode("euc-kr")
        # step에 "검토승인" 추가 (next_step이 "접수"인 case)
        # 기존 데이터가 "%요청%", "%검토%", "%접수%" 인 상태에서 새로 수집한 데이터가 "요청승인", "검토승인", "%접수%" 일 경우 
        errCheck = "step0"

        if result is not None and result != step:
        # if any(item in result for item in ["요청", "검토", "접수"]) and any(item in step for item in ["요청승인", "검토승인", "접수"]) and result != step:
            errCheck = "step1"
            return result
            # msgr.put_msgr_target(req_no + " is ready to progress.", grp_cd="DBWX99", send_title="**ITSM 신규요청**", msgr_color="YELLOW")
        
        # 기존 데이터가 없고 새로 수집한 데이터가 "요청승인", "검토승인", "%접수%" 일 경우 
        elif result is None : # and result != step:
            errCheck = "step2"
            return "신규"
        
        return None
    
    except Exception as e:
        # print(func_nm() + ": " + str(e))
        msgr.put_msgr_target(func_tree() + ":\n" + str(e) + "\n" + errCheck, grp_cd="DBWX99", send_title="[Error] ITSM Alert", msgr_color="Attention", send_funcnm=func_nm())
        pass


if __name__ == "__main__":
    import math # temp
    start = time.time()
    df_db_data = list_itsm_db_data()
    
    try:
        pass
        """
        ##2025.02.24 ITSM 2.0 전환에 따른 기능 중지
        driver = itsm_login()        
        #######################
        # 반려, 취소건 삭제
        #######################
        df_xml_reject = list_itsm_xml(driver, '02')
        df_xml_reject.set_index('순번', inplace=True)
        df_xml_reject.fillna("", inplace=True)

        # db가 기준이라서 left에 두려다가 insertable과 일관성있게 xml을 left로 둠
        # suffixes : 동일 컬럼명일 경우, 접미어 지정 (default : ("_x","_y"))
        df_deletable = pd.merge(left = df_xml_reject, right = df_db_data, how = "inner", on = "요청번호", suffixes=("_xml","_db")) 
        
        # inner join으로 삭제 대상만 전달
        if not df_deletable.empty:
            delete_itsm_reject_log(df_deletable)
        
        #######################
        # 정상건 조회 및 UPSERT
        #######################
        # xml이 기준
        df_xml_request = list_itsm_xml(driver, '01')
        # while df_xml_request.empty:
        #     df_xml_request = list_itsm_xml(driver, '01')
        df_xml_request.set_index('순번', inplace=True)
        df_xml_request.fillna("", inplace=True)

        df_insertable = pd.merge(left = df_xml_request , right = df_db_data, how = "left", on = "요청번호", suffixes=("_xml","_db"))
        # NaN을 포함하여 신규 데이터 또는 상태가 변경된 데이터만 전달
        # 단계 컬럼 정리까지 한꺼번에 진행 (inplace는 제외)
        if not df_insertable.loc[df_insertable["단계_xml"] != df_insertable["단계_db"]].empty:
            insert_itsm_request_log(df_insertable.loc[df_insertable["단계_xml"] != df_insertable["단계_db"]].rename(columns={"단계_xml":"단계"}).drop("단계_db", axis=1))
        
        driver.quit() # webdriver 종료
        end = time.time()
        print(f"{end - start:.5f} sec")
        # msgr.put_msgr_target(f"{end - start:.5f} sec", grp_cd="DBWX99", send_title="**ITSM**", msgr_color="GREEN")
        """
    except Exception as e:
        # print(file_nm() + ": " + str(e))
        msgr.put_msgr_target(str(e), grp_cd="DBWX99", send_title="**" + file_nm() + "**", msgr_color="RED", send_funcnm=func_nm())
        pass