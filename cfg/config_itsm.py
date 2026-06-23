
# ITSM_PATH = "C:/csr"
# CHROME_DEBUG_COOKIE_PATH = "C:/csr/debug_cookie"
# CHROME_DEBUG_EXEC_PATH = "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"
# CHROME_DEBUG_PORT = "9222"

DELAY_TIME = 5
DWP_LOGIN_URL = "https://dwp.lotte.net/Group/LoginPage.bzr" 
DWP_USER_ID = "L21065"
DWP_USER_PASSWORD = "gvvRTU,Fug"

MOIN_URL = "https://dwp.lotte.net/Group/Portal/Enterprise/DefaultPage.bzr"
# ITSM_LOGIN_URL = "https://nitsm.lotte.net/index.jsp"
ITSM_LOGIN_URL = "https://itsm.lotte.net/ko/slo/sloLogin?v=koI4BBYnj1Bi4um5RS-2oqUIwmvslEH-3qSPIpJ5MCvZ9aFf6WZ5oxkeV1ZA8h1ynC8zRTVhDfc9FEgQknVuDLgtOateGbigKb3BqWrZ_a-RL0rVsw40raEhMvO9p7QhwO7PNKL9WMBLp6kVXcA20agMn3LKCU6wOg17dtwQTAE%3D"
# GET_ITSM_URL = 'https://nitsm.lotte.net/.lxp?target=csr&method=getDivCsrRequestList'
GET_ITSM_URL = "https://itsm.lotte.net/api/proxy?path=https%3A%2F%2Fitsm.lotte.net%2Fapi%2Fv1%2Fcsr%2Fmanagement%2Fprogress&pageCategory=dept&pageStep=all&searchCompCd=&searchReqTypeLclas=&searchReqTypeSclas=&searchTrgetSysCd=SYS2024120400043&searchDeptCd=&searchStatus=&reqDtType=reqDt&reqStrtDt=2025-12-05&reqEndDt=2026-01-05&searchType=title&searchTxt=&isCsrSeprChecked=false&isRejectChecked=false&isDelayChecked=false&isUrgentChecked=false&isClosingChecked=false&isReqRejectChecked=false&isMngr=true&compCd=COM071800&deptCd=COM07180002156&userId=L21065%40lotte.net&roleId=A000B003&managedGroupId=COM071800202103233"
DOWNLOAD_FILE_NAME = "전체요청목록"
EXCEL_EXT = ".xlsx"


ITSM_OFFSET_SIZE = 0
ITSM_MAX_CNT_SIZE = 2000

ITSM_HEADERS = {"Accept":"application/xml, text/xml, */*"
               ,"Accept-Encoding":"gzip, deflate, br"
               ,"Accept-Language":"ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7"
               ,"Cache-Control":"no-cache, no-store"
               ,"Connection":"keep-alive"
               ,"Content-Length":"11598"
               ,"Content-Type":"text/xml"
               }

ITSM_REMAPPING = {
            "csr_type_name": "요청유형",
            "sub_csr_type_name": "상세요청유형",
            "request_title": "제목",
            "service_catalog_name": "서비스카탈로그",
            "request_user_name": "요청자",
            "request_user_id": "요청자사번",
            "request_user_dept_name": "요청부서",
            "trt_user_name": "작업자",
            "reg_time": "요청일",
            "fin_begin_time": "시작예정일",
            "request_solve_time": "완료희망일",
            "fin_exp_time": "완료예정일",
            "start_time": "처리시작일",
            "end_time": "처리완료일",
            "process_status_name": "단계",
            "next_process_status_name": "다음상태",
            # "next_process_div_name": "다음상태",
            "assignee_user_name": "담당자",
            "progress_rate": "진척율(%)",
            "work_day_cnt": "작업일수",
            "trt_mh": "처리시간",
            "delay_day_cnt": "지연일수",
            "satisfy_score": "만족도",
            "receive_time": "접수완료일",
            "satisfy_reg_time": "만족도평가일",
            "closed_time": "최종완료일",
            "all_worker": "전체작업자",
            "request_id": "요청번호",
            "parent_request_id": "관리CSR번호",
            "is_code_name": "IS팀",
            "release_start_time": "배포시작일",
            "release_end_time": "배포완료일",
            "review_user_name": "검토자",
            "review_time": "검토완료일",
            "row_index" : "순번"
        }
# JSON 타입은 키의 VALUE 수정이 용이해서 config로 사용
ITSM_COOKIES = {
"_ga" : "GA1.1.1538730031.1679819216"
,"moin_test02" : "xlra+YTeallQERPpyEzp2YMliouzdgv+PsHjVlD8qJd4lno6fjlGwG2JDyT5s6BKTf0wNMT3heHlK7YEbajkO6Zd7kMM5/AXY5gtfmOZmgA/lNcK+ILFyWyjMZJMsuLAxc1Hom4AYZ3UeOmdg6A52sc7LJphy4s97kCuk6C6aoEFPbyhLunb1UuFIoyvF6vudth5wTPzx2FeNxV4MJ6ciUFehD0ZbtqANq6XY9H9lJNI374r8N6Chw3SgsJq99AneJIAgQmgA+LBSLURMXRmvDM0QFQKgxhBn+WpwfFMg2FKxry4NIgJFzpubl4vPHXI7yI26RtR3c2lL1Bga5u1/MOZXSqX9oos6V5cVs5M2PjexQ0meXfAUkHb8XHwL+oc30Y5APoGguee5PHPNg1l+tokaeWKvkk7gymHwx1MyihkLRH8Iwy/dAXiQSmgLRLiFtivCNjy406vsRPPVr6q8JxmblrNUSgfvqqH8hB6K1YwSqiEAta0RHSruvieUVANyB6EHJPEPvFjT/TKxIIVowwDv7g5mw3bN1DUjrfnEgCLRm7C+Lb2QN5+ZwjiM6SsYAy4H6/xPSo6QhoWnr9Hunk37XYo+J1emTAh19VLBr20W7Q+yeA9sIC0z3hEV0DhCpI9KO3ztloMmzwtQ4Por0134pZfIUO8XasJU6tjSkL8HScyFg8KHvMyEtQYxLUDnSCsv+Di/RtLh2vfndEhCQ=="
,"moin_test03":"1hj2FUDdYc2faKknEIEFCOODTmryt7QXMm/GygMOJViS/2ThC4h6DWglVPh4HlQQVdS0tFVCliFdfKSFA8bOSkV1VAdkEJfOz36mCnF61CZC15BgFFZZsdrphBpYxXV/B/frJ8IS1qhC87KIV2+6k9FgEFU1/3MfRYIg54l+KJ7HWWSI7FxCtg6BOlFX03Iwz2Q+5mGhzNE5FXyW1LeOw8I+mqidUpFnG00zrs4p2TpROazwYCDNCde8z2pq25cjSYW4RDO3IQkHU/hTe+V/Kz5eZy/Eh5x4Z2yiPpDU0wbi2eypka3mSFIgkDHBxRkjxtlcJ+BRSvhuybVPArMDyISW9KZSo/hfAdTEbMxJ9qBhc7ykCoE9QlcEJp52lJgdE0389cmNTfPWqSm6qMcILcWCdOv0TEcv/jfa229KZKZSME7TuxcWBiZ4BYuapPaCr6e7ordH8eM="
,"moin_practice02":DWP_USER_ID
,"moin_practice03":"COMPANY"
,"moin_practice04":"1042"
,"moin_idsavecheck":DWP_USER_ID
,"moin_test01":"xlra+YTeallQERPpyEzp2YujynbyOynhWP/yuMuI3HDoYDlS+Y1Pui7l5LwQnRqq8LS/Ao7+IXtL8KuIjI+80LYMWQHd4ndRp5Wc/XGpA+hSOW2SJV0TLuY1XV1GllrC24ncSGFCTBkQNdjTCa0padiKMphjPyRYjdENXBq55UD1Vfurk4VuCi/jLCf6Py8WeWZYEk9O9rDja4D4KlSl6zBFiVZK7yFc+pMIdbJAOvrVBfyBkGcUYuRuRQ5euc7xwk6wIixy7tgulkJet2WUNW9t4emnmkF4UTEYWzCt68cbaBX3e/jhYHjhbbBZTQ3YuA0llD6FZNkmt0EqIM8Fp4ots4uPAHa+ffbVL5mhJsu85Ie7nyXGGlFTYIarJIhbA7TlsH9CuaR/PtlAsad2vj5dxLSe0Djn72/nh91MBCRcsR9BlxBalHHkpOLVUqtIizfiBlXWvhoxkGGTO4NVAA=="
,"moin.token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1laWQiOiIxNjI3OTE4IiwiZ3JvdXBzaWQiOiIwNzE4MDAiLCJMb2NhbGl0eSI6IktvcmVhIFN0YW5kYXJkIFRpbWUiLCJWZXJzaW9uIjoiMjAyMy0wNy0wNCDsmKTsoIQgMToyNzo0MSIsIm5iZiI6MTY4ODQzNDA2MSwiZXhwIjoxNjg5NzMwMDYxLCJpYXQiOjE2ODg0MzQwNjEsImlzcyI6Imh0dHBzOi8vbG9naW4ubG90dGUubmV0LyIsImF1ZCI6Imh0dHBzOi8vd3d3LmxvdHRlLm5ldCJ9.NbkJ8IIFGps4sDKa_Ii3r7PScfxy7XCnkE_G2Vcm-EM"
,"cookieSaveYn":"N"
,"user_id":""
,"div_id":""
,"userid":"test"
,"sso2020Prod":"462"
,"_ga_6MRNLRP1CL":"GS1.1.1707095948.225.1.1707095961.0.0.0"
,"JSESSIONID": None # 핵심 파라미터
}

ITSM_HEADERS = {
            "Accept": "application/xml, text/xml, */*",
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
            "Cache-Control": "no-cache, no-store",
            "Connection": "keep-alive",
            "Content-Type": "text/xml",
            "If-Modified-Since": "Sat, 1 Jan 2000 00:00:00 GMT",
            "Pragma": "no-cache",
            "Sec-Fetch-Dest": "empty",
            "X-Requested-With": "XMLHttpRequest",
        }

DEFAULT_GROUP_CD = "DBWX99"

# 파트의 서비스별로 메시지 전송 그룹 지정
# 개발 단계, 관리자에게만 문자 (분할 전송)
PART_SVC_MAPPING = {
    "DBWX99": ["IT_경영지원 Part > 그룹웨어",
               "IT_경영지원 Part > 기업문화",
               "IT_경영지원 Part > 동료사원",
               "IT_경영지원 Part > 메일/메신저",
               "IT_경영지원 Part > 전산의뢰",
               "IT_경영지원 Part > 전자결재",
               "IT_경영지원 Part > 형상관리",],
    "DBWX99": ["IT_경영지원 Part > 인사",
               "IT_경영지원 Part > HQ인사",],
    "DBWX99": ["IT_마케팅 Part > 근거리배송시스템",
               "IT_마케팅 Part > 배송시스템",],
    "DBWX99": ["IT_마케팅 Part > 문화센터시스템",],
    "DBWX99": ["IT_마케팅 Part > 법인영업시스템",
               "IT_마케팅 Part > 비즈마일리지",
               "IT_마케팅 Part > 사은시스템",
               "IT_마케팅 Part > 에누리시스템",
               "IT_마케팅 Part > 통합AS시스템",],
    "DBWX99": ["IT_상품권 Part > 상품권시스템",],
    "DBWX04": ["IT_인프라 Part > 데이터베이스",],  # 이거 때문에 세부 카테고리까지 봄
    "DBWX99": ["IT_인프라 Part > 보안",],  # 이거 때문에 세부 카테고리까지 봄
    "DBWX99": ["IT_재무 Part > 구매",
               "IT_재무 Part > 웹전표",],
    "DBWX99": ["IT_재무 Part > ERP(SAP) - 손익",
               "IT_재무 Part > ERP(SAP) - 자금",
               "IT_재무 Part > ERP(SAP) - 해외",
               "IT_재무 Part > ERP(SAP) - 회계",
               "IT_재무 Part > ERP(SAP) - G/L계정생성",],
    "DBWX99": ["IT_재무 Part > SAP HANA 시스템",],
    "DBWX99": ["IT_MD Part > 거래선SCM",
               "IT_MD Part > 파트너포탈",
               "IT_MD Part > 파트너포탈-모바일",],
    "DBWX99": ["IT_POS Part > POS시스템-개발",
               "IT_POS Part > POS시스템-매출",],
    "DBWX99": ["IT_MD Part > 영업분석시스템",],
    "DBWX99": ["IT_MD Part > 영업통합시스템-기준정보",],
    "DBWX99": ["IT_MD Part > 영업통합시스템-매입정산",],
    "DBWX99": ["IT_MD Part > 영업통합시스템-영업매출",],
    "DBWX99": ["IT_MD Part > 영업통합시스템-온라인",],
}
# # 파트의 서비스별로 메시지 전송 그룹 지정
# PART_SVC_MAPPING = {
#     "HR9993": ["IT_경영지원 Part > 그룹웨어",
#                "IT_경영지원 Part > 기업문화",
#                "IT_경영지원 Part > 동료사원",
#                "IT_경영지원 Part > 메일/메신저",
#                "IT_경영지원 Part > 전산의뢰",
#                "IT_경영지원 Part > 전자결재",
#                "IT_경영지원 Part > 형상관리",],
#     "HR9994": ["IT_경영지원 Part > 인사",
#                "IT_경영지원 Part > HQ인사",],
#     "MK9991": ["IT_마케팅 Part > 근거리배송시스템",
#                "IT_마케팅 Part > 배송시스템",],
#     "MK9992": ["IT_마케팅 Part > 문화센터시스템",],
#     "MK9993": ["IT_마케팅 Part > 법인영업시스템",
#                "IT_마케팅 Part > 비즈마일리지",
#                "IT_마케팅 Part > 사은시스템",
#                "IT_마케팅 Part > 에누리시스템",
#                "IT_마케팅 Part > 통합AS시스템",],
#     "GC9993": ["IT_상품권 Part > 상품권시스템",],
#     "DBWX99": ["IT_인프라 Part > 데이터베이스",],  # 이거 때문에 세부 카테고리까지 봄
#     "SC9991": ["IT_인프라 Part > 보안",],  # 이거 때문에 세부 카테고리까지 봄
#     "IF9991": ["IT_재무 Part > 구매",
#                "IT_재무 Part > 웹전표",],
#     "IF9992": ["IT_재무 Part > ERP(SAP) - 손익",
#                "IT_재무 Part > ERP(SAP) - 자금",
#                "IT_재무 Part > ERP(SAP) - 해외",
#                "IT_재무 Part > ERP(SAP) - 회계",
#                "IT_재무 Part > ERP(SAP) - G/L계정생성",],
#     "IF9993": ["IT_재무 Part > SAP HANA 시스템",],
#     "MD9991": ["IT_MD Part > 거래선SCM",
#                "IT_MD Part > 파트너포탈",
#                "IT_MD Part > 파트너포탈-모바일",],
#     "PS9991": ["IT_POS Part > POS시스템-개발",
#                "IT_POS Part > POS시스템-매출",],
#     "MD9990": ["IT_MD Part > 영업분석시스템",],
#     "MD9995": ["IT_MD Part > 영업통합시스템-기준정보",],
#     "MD9994": ["IT_MD Part > 영업통합시스템-매입정산",],
#     "MD9993": ["IT_MD Part > 영업통합시스템-영업매출",],
#     "MD9992": ["IT_MD Part > 영업통합시스템-온라인",],
# }

# 무시할 파트 키워드
IGNORE_GRP = [
    "데이터플랫폼",
    "디지털 채널",
    "웨딩시스템"
]