"""
JSON 응답 데이터 파싱 및 필터링
"""

import json
import csv
import cmn.common_msgr as msgr
from cmn.common_db import monPC
from cmn.common import get_cur_func_nm as func_nm, get_cur_file_nm as file_nm, get_func_tree as func_tree
from typing import List, Dict, Any


from cfg.config_itsm import IGNORE_GRP, PART_SVC_MAPPING, DEFAULT_GROUP_CD


def filter_csr_data(response_data: str | dict) -> List[Dict[str, Any]]:
    """
    JSON 응답에서 필요한 필드만 추출
    """
    # 필요한 필드 목록
    REQUIRED_FIELDS = [
        'reqTitle',           # 요청 제목
        'trgetSysNm',          # 대상시스템(보안, 데이터베이스)
        'reqTypeLclasNm',     # 요청 유형 대분류명
        'reqTypeSclasNm',     # 요청 유형 소분류명
        'reqDt',              # 요청 일자
        'endPlanDt',          # 종료 예정일
        'csrNo',              # CSR 번호
        'curProcsStep',       # 현재 처리 단계
        'reqDeptNm',          # 요청 부서명
        'reqUserId',          # 요청자 ID
        'reqUserNm',          # 요청자 이름
        'curWorkflowLseq',    # 현재 워크플로우 순서
        'maxWorkflowLseq',    # 최대 워크플로우 순서
        'rcpUserId',          # 접수자 ID
        'rcpUserNm',          # 접수자 이름
        'status'              # 상태
    ]
    
    # 문자열이면 JSON 파싱
    if isinstance(response_data, str):
        data = json.loads(response_data)
    else:
        data = response_data
    
    # csrManagementList 추출
    csr_list = data.get('csrManagementList', [])
    
    # 필요한 필드만 필터링
    filtered_list = []
    for item in csr_list:
        filtered_item = {
            field: item.get(field)
            for field in REQUIRED_FIELDS
        }
        filtered_list.append(filtered_item)

        # print(filtered_item.get('reqTitle', 'N/A'))
        # print("\n" + "="*80)
    
    return filtered_list


def print_filtered_data(filtered_data: List[Dict[str, Any]]):
    """
    필터링된 데이터를 보기 좋게 출력
    
    Args:
    - filtered_data: 필터링된 데이터 리스트
    """
    print("\n" + "="*80)
    print(f"📋 CSR 관리 목록 (총 {len(filtered_data)}개)")
    print("="*80)
    
    for idx, item in enumerate(filtered_data, 1):
        print(f"\n[{idx}] {item.get('csrNo', 'N/A')}")
        print(f"  제목: {item.get('reqTitle', 'N/A')}")
        print(f"  요청 유형: {item.get('reqTypeLclasNm', 'N/A')} > {item.get('reqTypeSclasNm', 'N/A')}")
        print(f"  요청 일자: {item.get('reqDt', 'N/A')}")
        print(f"  종료 예정일: {item.get('endPlanDt', 'N/A')}")
        print(f"  현재 단계: {item.get('curProcsStep', 'N/A')}")
        print(f"  워크플로우: {item.get('curWorkflowLseq', 'N/A')}/{item.get('maxWorkflowLseq', 'N/A')}")
        print(f"  요청 부서: {item.get('reqDeptNm', 'N/A')}")
        print(f"  요청자: {item.get('reqUserNm', 'N/A')} ({item.get('reqUserId', 'N/A')})")
        print(f"  작업자: {item.get('rcpUserNm', 'N/A')} ({item.get('rcpUserId', 'N/A')})")
        print(f"  상태: {item.get('status', 'N/A')}")
        print("\n")


def insert_itsm_request_log(filtered_data: List[Dict[str, Any]]):
    conn = monPC(func_nm())
    # content = "" # 단일 전송에서 담당별 전송으로 변경
    
    sqlTxt = """
    MERGE dbo.TB_NEWITSM_REQ_L AS A
    USING (SELECT %s as REQ_NO
                , %s as STEP_CD
                , %s as CMPL_DT
                , %s as RCPTPR_ID
            ) AS B
        ON (A.REQ_NO = B.REQ_NO
            )
    WHEN NOT MATCHED THEN
        INSERT (  REQ_NO
                 ,STAT_CD
                 ,REQ_TIT_NM
                 ,OBJ_SYS_NM
                 ,REQ_LRCLS_NM
                 ,REQ_SMCLS_NM
                 ,REQ_DT
                 ,CMPL_DT
                 ,REQ_DPT_NM
                 ,REQPR_ID
                 ,REQPR_NM
                 ,STEP_CD
                 ,NOW_STEP_CD
                 ,MAX_STEP_CD
                 ,RCPTPR_ID
                 ,RCPTPR_NM
                 ,RGPR_ID
                 ,RGST_DTM
                ) VALUES
                ( %s
                , %s
                , %s
                , %s
                , %s
                , %s
                , %s
                , %s
                , %s
                , %s
                , %s
                , %s
                , %s
                , %s
                , %s
                , %s
                ,'insert_itsm_request_log'
                , getdate()
                )
    WHEN MATCHED AND (A.STEP_CD <> B.STEP_CD 
                   OR A.RCPTPR_ID <> B.RCPTPR_ID
                   OR A.CMPL_DT <> B.CMPL_DT)THEN
        UPDATE SET    A.REQ_NO        = %s
                    , A.STAT_CD       = %s
                    , A.REQ_TIT_NM    = %s
                    , A.OBJ_SYS_NM    = %s
                    , A.REQ_LRCLS_NM  = %s
                    , A.REQ_SMCLS_NM  = %s
                    , A.REQ_DT        = %s
                    , A.CMPL_DT       = %s
                    , A.REQ_DPT_NM    = %s
                    , A.REQPR_ID      = %s
                    , A.REQPR_NM      = %s
                    , A.STEP_CD       = %s
                    , A.NOW_STEP_CD   = %s
                    , A.MAX_STEP_CD   = %s
                    , A.RCPTPR_ID     = %s
                    , A.RCPTPR_NM     = %s
                    , A.MDFPR_ID      = 'update_itsm_request_log'
                    , A.MDF_DTM       = getdate()
    ;
    """

    try:
        for idx, item in enumerate(filtered_data, 1): # each row
            # print("======================================")
            # print(idx)
            # 숫자는 %d, 문자는 %s를 사용

            msg_title      = ""
            csrNo           = item.get('csrNo') or "N/A"
            status          = item.get('status') or "N/A"
            reqTitle        = item.get('reqTitle') or "N/A"
            trgetSysNm      = item.get('trgetSysNm') or "N/A"
            reqTypeLclasNm  = item.get('reqTypeLclasNm') or "N/A"
            reqTypeSclasNm  = item.get('reqTypeSclasNm') or "N/A"
            reqDt           = item.get('reqDt') or "N/A"
            endPlanDt       = item.get('endPlanDt') or "N/A"
            reqDeptNm       = item.get('reqDeptNm') or "N/A"
            reqUserId       = item.get('reqUserId') or "N/A"
            reqUserNm       = item.get('reqUserNm') or "N/A"
            curProcsStep    = item.get('curProcsStep') or "N/A"
            curWorkflowLseq = item.get('curWorkflowLseq') or "N/A"
            maxWorkflowLseq = item.get('maxWorkflowLseq') or "N/A"
            rcpUserId       = item.get('rcpUserId') or "N/A"
            rcpUserNm       = item.get('rcpUserNm') or "N/A"

            # 진행 단계 확인
            chkStep = chk_itsm_change(conn, csrNo, curProcsStep, rcpUserId, endPlanDt)


            # 변경이 있는 경우만 알림
            if chkStep is None : 
                print("변경없음\n")
                # print("="*80 +"\n")
                continue

            # 접수, 결재, 결재 완료 상태에 대해서만 알림
            if curProcsStep in ("03","11") :
                # 기본 양식
                content = "**" + reqTypeSclasNm + "**" + "\n"      
                content = content + "# CSR : " + csrNo + "\n"
                content = content + "# 내용 : " + reqTitle + "\n"
                content = content + "# 요청 : " + reqUserNm + " (" + reqDeptNm + ")" + "\n"              

                # CSR 접수 대기
                if rcpUserId == "N/A" and endPlanDt == "N/A":
                    content = content + "\n"
                    content = content + "매니저님 CSR 접수 부탁드립니다.\n"
                    content = content + "-" + csrNo + "\n"
                    msg_title = "ITSM 접수(대기)"

                # CSR 결재 대기
                elif rcpUserId != "N/A" and endPlanDt == "N/A":
                    content = content + "# 작업 : " + rcpUserNm + "\n"
                    content = content + "# 일자 : " + endPlanDt + "\n"
                    content = content + "\n"
                    content = content + "매니저님 CSR 결재 부탁드립니다.\n"
                    content = content + "-" + csrNo + "\n"
                    msg_title = "ITSM 접수(결재)"

                # CSR 처리 대기
                elif rcpUserId != "N/A" and endPlanDt != "N/A":                    
                    content = content + "# 작업 : " + rcpUserNm + "\n"
                    content = content + "# 일자 : " + endPlanDt + "\n"
                    content = content + "\n"
                    content = content + "※CSR 결재 완료\n"
                    msg_title = "ITSM 처리(대기)"

                if trgetSysNm == "데이터베이스" and content:
                    msgr.put_msgr_target(content.rstrip("\n"), "DBWX04", send_title=msg_title, msgr_color="Good", send_funcnm=func_nm())                    
                
                elif trgetSysNm == "보안" and content:
                    msgr.put_msgr_target(content.rstrip("\n"), "SCWX04", send_title=msg_title, msgr_color="Good", send_funcnm=func_nm())                    

            # print(req_no)
            conn.execute(sqlTxt
                            ######## for select
                            ,(csrNo
                            , curProcsStep
                            , reqDt
                            , rcpUserId
                            ########### for insert
                            , csrNo
                            , status
                            , reqTitle
                            , trgetSysNm
                            , reqTypeLclasNm
                            , reqTypeSclasNm
                            , reqDt
                            , endPlanDt
                            , reqDeptNm
                            , reqUserId
                            , reqUserNm
                            , curProcsStep
                            , curWorkflowLseq
                            , maxWorkflowLseq
                            , rcpUserId
                            , rcpUserNm                           
                            ######### for update
                            , csrNo
                            , status
                            , reqTitle
                            , trgetSysNm
                            , reqTypeLclasNm
                            , reqTypeSclasNm
                            , reqDt
                            , endPlanDt
                            , reqDeptNm
                            , reqUserId
                            , reqUserNm
                            , curProcsStep
                            , curWorkflowLseq
                            , maxWorkflowLseq
                            , rcpUserId
                            , rcpUserNm)
                        )
        
            # even MS-SQL need it (MUST)
            conn.commit()

    except Exception as e:
        print(func_nm() + ": " + str(e))
        msgr.put_msgr_target(func_tree() + ":\n" + str(e), grp_cd="DBWX99", send_title="**" + func_nm() + "**", msgr_color="RED", send_funcnm=func_nm())
        # pass

    finally:
        if conn:
            conn.close()

def chk_itsm_change(conn, req_no, curProcsStep, rcpUserId, endPlanDt): # row["요청번호"], row["단계"]

    sqlTxt = """
    SELECT STEP_CD, RCPTPR_ID, CMPL_DT
      FROM TB_NEWITSM_REQ_L (nolock) 
     WHERE REQ_NO = %s
            """
    
    errCheck = ""

    try:
        result = conn.query(sqlTxt, req_no)

        # CSR 신규
        if not result :      
            return "new"

        cnt = 0 
        v_curProcsStep, v_rcpUserId, v_endPlanDt = result[0]

        print("v_curProcsStep : " + v_curProcsStep)
        print("curProcsStep : " + curProcsStep)

        if v_curProcsStep != curProcsStep : 
            cnt = cnt + 1
        if v_rcpUserId != rcpUserId : 
            cnt = cnt + 1
        if v_endPlanDt  != endPlanDt :
            cnt = cnt + 1
        
        # CSR 진행상태 변경
        if cnt != 0 :
            return "mod"
        else :
            return None
    
    except Exception as e:
        print(func_nm() + ": " + str(e))
        msgr.put_msgr_target(func_tree() + ":\n" + str(e) + "\n" + errCheck, grp_cd="DBWX99", send_title="[Error] ITSM Alert", msgr_color="Attention", send_funcnm=func_nm())
        pass 


def main():
    """테스트용 메인 함수"""
    # 샘플 데이터
    sample_data = {
      "csrManagementList": [
        {
            "compCd": "COM071800",
            "compNm": "롯데백화점",
            "reqTitle": "[문화센터] 강좌구분별접수현황(우) 집계 대상 등급 순서 변경 외 1건",
            "reqCont": None,
            "reqType": None,
            "reqTypeLclas": "REQB004",
            "reqTypeSclas": "REQB004S0003",
            "reqTypeLclasNm": "시스템변경/개발",
            "reqTypeSclasNm": "DB 변경 요청(정규)",
            "reqTypeLclasMetaCode": None,
            "reqTypeSclasMetaCode": None,
            "reqDt": "2026-03-23",
            "trgetSysCd": "SYS2024120400043",
            "trgetSysNm": "데이터베이스",
            "curApprStatus": "00",
            "csrId": "0718002603235305",
            "csrSubId": "0718002603235306",
            "csrNo": "CSR0718002603235305",
            "workflowId": "WF00000000000303",
            "progressRate": None,
            "myWork": None,
            "curProcsStep": "13",
            "endPlanDt": "2026-03-31",
            "reqDeptCd": None,
            "reqDeptNm": "IT_마케팅 Part",
            "reqUserId": "L22257@lotte.net",
            "reqUserNm": "안소현",
            "rcpDeptCd": "COM071800202103233",
            "rcpDeptNm": "인프라/시스템담당",
            "rcpUserId": "L29011@lotte.net",
            "rcpUserNm": "김진현",
            "startPlanDt": "2026-03-31",
            "apprSeqNo": 0,
            "apprUserId": None,
            "apprUserNm": None,
            "apprDt": None,
            "hierarchyPath": "CSR0718002603235305",
            "parentCsrId": None,
            "parentCsrNo": None,
            "childCsrIds": None,
            "tmprSaveYn": None,
            "chckDeptCd": None,
            "chckDeptNm": None,
            "chckUserId": None,
            "chckUserNm": None,
            "ipcr": None,
            "curWorkflowLseq": 3,
            "maxWorkflowLseq": 3,
            "finEndDt": None,
            "wdtbEndDt": None,
            "totalMh": None,
            "processEndDt": None,
            "wdtbLastApprDt": None,
            "standardEndDate": "처리 완료일",
            "standardFinEndDt": None,
            "delayDays": 0,
            "status": "",
            "allRcpUsers": "김진현",
            "stsfdgGrade": None,
            "bizDivCd": None,
            "bizDivNm": None,
            "bizDivMetaCode": None
        }
  ]
    }
    
    # 필터링
    filtered = filter_csr_data(sample_data)
    
    # 출력
    print_filtered_data(filtered)

    # Insert Data
    insert_itsm_request_log(filtered)

if __name__ == "__main__":
    main()
