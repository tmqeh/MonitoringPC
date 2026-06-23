from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
from cfg.config_itsm2 import filter_csr_data, insert_itsm_request_log 
from bs4 import BeautifulSoup
import time
import json
import os


def login(url1):
    """
    URL1에 접속하여 Chrome driver 객체를 생성하고 리턴
    
    Args:
        url1 (str): 로그인 페이지 URL (토큰이 GET 파라미터에 포함됨)
    
    Returns:
        webdriver.Chrome: 로그인된 Chrome driver 객체
    """
    # Chrome 옵션 설정
    chrome_options = Options()

    # Headless 모드 활성화
    chrome_options.add_argument('--headless=new')
    
    # 기본 보안 및 안정성
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    
    # Headless 최적화
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-software-rasterizer')
    chrome_options.add_argument('--disable-notifications')

    # GPU 가상화 오류 해결을 위한 추가 옵션
    chrome_options.add_argument('--disable-features=VizDisplayCompositor,VizHitTestSurfaceLayer')
    chrome_options.add_argument('--disable-features=IsolateOrigins,site-per-process')
    chrome_options.add_argument('--disable-features=BlockInsecurePrivateNetworkRequests')
    chrome_options.add_argument('--use-angle=swiftshader')  # 소프트웨어 렌더링 강제
    chrome_options.add_argument('--disable-webgl')  # WebGL 비활성화
    chrome_options.add_argument('--disable-webgl2')  # WebGL2 비활성화
    chrome_options.add_argument('--disable-3d-apis')  # 3D API 비활성화
    chrome_options.add_argument('--disable-accelerated-2d-canvas')  # 2D 캔버스 가속 비활성화
    chrome_options.add_argument('--disable-accelerated-video-decode')  # 비디오 디코딩 가속 비활성화    

    # 성능 최적화
    chrome_options.add_argument('--disable-background-timer-throttling')
    chrome_options.add_argument('--disable-backgrounding-occluded-windows')
    chrome_options.add_argument('--disable-renderer-backgrounding')
    
    # Chrome driver 생성
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # URL1에 접속 (토큰이 GET 파라미터에 있어서 자동 로그인됨)
        driver.get(url1)
        
        # 페이지 로딩 완료 대기 (document.readyState == 'complete')
        WebDriverWait(driver, 10).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )
        print("✅ 페이지 로딩 완료")
        
        # 중요한 쿠키(accessToken)가 설정될 때까지 대기
        max_wait = 10  # 최대 10초 대기
        wait_count = 0
        access_token_found = False
        
        while wait_count < max_wait:
            cookies = driver.get_cookies()
            cookies_cnt = len(cookies)
            
            # accessToken 또는 JSESSIONID 확인
            if cookies_cnt == 6:
                access_token_found = True
                break
            
            print(f"⏳ 인증 쿠키 대기 중... ({wait_count + 1}/{max_wait}초)")
            time.sleep(1)
            wait_count += 1
        
        # 쿠키 확인 (디버깅용)
        cookies = driver.get_cookies()   
            
        if not access_token_found:
            print("⚠️ 경고: 인증 쿠키를 찾을 수 없습니다!")
        
        print("✅ 로그인 완료")
        return driver
        
    except Exception as e:
        print(f"❌ 로그인 중 오류 발생: {e}")
        driver.quit()
        raise


def get_list(driver, url2):

    try:  
        # 동일한 driver로 URL2에 접속 (세션 유지됨)
        driver.get(url2)
        
        # 페이지 로딩 완료 대기
        WebDriverWait(driver, 10).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )
        
        # 추가 대기
        time.sleep(2)    
            
        # response 값 (HTML 소스) 저장
        response = driver.page_source
        
        # 401 에러 체크
        if "401" in response or "Unauthorized" in response:
            print("❌ 401 Unauthorized 에러 감지!")
            print("   세션이 유지되지 않았습니다.")
            print(f"   응답 내용 (처음 500자): {response[:500]}")
        else:
            print("✅ 데이터 수집 완료")        

       # JSON 데이터 추출 및 필터링 (응답이 JSON인 경우)
        try:
            # response가 문자열인지 확인
            if not isinstance(response, str):
                print(" 응답이 문자열이 아닙니다. HTML만 저장됩니다.")
            else:
                # HTML에서 JSON 데이터 추출 시도
                # 만약 response가 순수 JSON이라면 바로 파싱
                response_stripped = response.strip()
                json_text = None

                soup = BeautifulSoup(response_stripped, 'html.parser')
                
                # <pre> 태그에서 JSON 추출
                pre_tag = soup.find('pre')
                json_text = pre_tag.get_text()                
                json_text = json_text.strip()

            # JSON 파싱 시도
            if json_text and (json_text.startswith('{') or json_text.startswith('[')):
                json_data = json.loads(json_text)
                
                # 필요한 필드만 필터링
                filtered_data = filter_csr_data(json_data)

                # 필터링된 데이터 이력 저장 및 메세지전송
                insert_itsm_request_log(filtered_data)
                
            else:
                print("\n⚠️  응답이 JSON 형식이 아닙니다. HTML만 저장됩니다.")                
                
        except json.JSONDecodeError as e:
            print(f"\n⚠️  JSON 파싱 실패: {e}")
            print("   HTML 파일만 저장되었습니다.")
        except Exception as e:
            print(f"\n⚠️  데이터 필터링 중 오류: {e}")    
        
        return response
        
    except Exception as e:
        print(f"❌ 데이터 수집 중 오류  발생: {e}")
        print(f"   현재 URL: {driver.current_url}")
        raise


def main():
    # 메인 실행 함수

    # 검색 종료일 (현재일자)
    END_DT = datetime.now().strftime('%Y-%m-%d')

    # 검색 시작일 (30일 이전일자)
    STA_DT = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    

    # URL 설정 (실제 URL로 변경 필요)
    # LOGIN URL
    URL1 = "https://itsm.lotte.net/ko/slo/sloLogin?v=koI4BBYnj1Bi4um5RS-2oqUIwmvslEH-3qSPIpJ5MCvZ9aFf6WZ5oxkeV1ZA8h1ynC8zRTVhDfc9FEgQknVuDLgtOateGbigKb3BqWrZ_a-RL0rVsw40raEhMvO9p7QhwO7PNKL9WMBLp6kVXcA20agMn3LKCU6wOg17dtwQTAE%3D"  # 로그인 페이지

    # DATA URL
    URL2 = "https://itsm.lotte.net/api/proxy?"
    URL2 = URL2 + "path=https%3A%2F%2Fitsm.lotte.net%2Fapi%2Fv1%2Fcsr%2Fmanagement%2Fprogress"
    URL2 = URL2 + "&pageCategory=dept"
    URL2 = URL2 + "&pageStep=all"
    URL2 = URL2 + "&searchCompCd="
    URL2 = URL2 + "&searchReqTypeLclas="
    URL2 = URL2 + "&searchReqTypeSclas="
    URL2 = URL2 + "&searchTrgetSysCd="
    URL2 = URL2 + "&searchDeptCd=COM071800202103233" # 담당부서 : 인프라/시스템담당
    URL2 = URL2 + "&searchStatus="
    URL2 = URL2 + "&reqDtType=reqDt"
    URL2 = URL2 + "&searchType=title"
    URL2 = URL2 + "&searchTxt="
    URL2 = URL2 + "&isCsrSeprChecked=false"
    URL2 = URL2 + "&isRejectChecked=false"
    URL2 = URL2 + "&isDelayChecked=false"
    URL2 = URL2 + "&isUrgentChecked=false"
    URL2 = URL2 + "&isClosingChecked=false"
    URL2 = URL2 + "&isReqRejectChecked=false"
    URL2 = URL2 + "&isMngr=true"
    URL2 = URL2 + "&compCd=COM071800"
    URL2 = URL2 + "&deptCd=COM07180002156"
    URL2 = URL2 + "&userId=L21065%40lotte.net"
    URL2 = URL2 + "&roleId=A000B003"
    URL2 = URL2 + "&managedGroupId=COM071800202103233"
    # 날짜 조건 설정
    URL2 = URL2 + "&reqStrtDt=" + STA_DT
    URL2 = URL2 + "&reqEndDt=" + END_DT
    
    driver = None
   
    try:
        # 1. 로그인
        driver = login(URL1)
        
        # 2. 데이터 수집
        response = get_list(driver, URL2)

        # print(f"✅ Response가 저장되었습니다:")
        
        # 4. 추가 처리 (예: BeautifulSoup으로 파싱)
        # from bs4 import BeautifulSoup
        # soup = BeautifulSoup(response, 'html.parser')
        # # 원하는 데이터 추출
        
    except Exception as e:
        print(f"실행 중 오류 발생: {e}")
        
    finally:
        # driver 종료
        if driver:
            driver.quit()
            print("Driver 종료 완료")

if __name__ == "__main__":
    main()
