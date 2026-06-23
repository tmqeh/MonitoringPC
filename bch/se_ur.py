import datetime
import json
import os

NOW = datetime.datetime.now()
YMD = NOW.strftime("%Y%m%d")

import requests

# Webex 액세스 토큰 (Bot OAuth 토큰)
access_token = 'MWQ1NDQ2ZjMtNmIzNS00NTRhLWE2YzctYzAwYWZiMzY0YWU4ZjIxZTMxYzQtOGE1_PF84_22cb7792-d880-4ec5-b6a6-649d9411bb5e'

# 메시지를 보낼 Webex 공간의 ID (Room ID)
room_id = 'Y2lzY29zcGFyazovL3VzL1JPT00vYjk3MTk3NjAtOWI0Ni0xMWVmLTg5YmItNjMxOWYwZDQ0Mzgy'

err_text=''
ok_count=0
nas_ok_count=0
err_host=[]
nas_err_host=[]
STORAGE_NAME=['culdb','gmsdb','enrdb','lpdlvdb','eadb','hrdb','lpgcsdb','lpscsdb','junjadb','leasedb','lpbatap','lpeaiex','lpeaiin','lpetlap','lpsisdb']
NAS_NAME=['nas_mkt','hnas','gnas','nas_drm','nas_md']
for STORAGE_NAMES in STORAGE_NAME:
    file_open=open(f'E:/se_daily_report/Storage_NAS_UR/{YMD}_{STORAGE_NAMES}.txt',"r")
    line=file_open.readline().strip() #읽은 값이 1이면 ok count 증가
    if line=='1':
        ok_count=ok_count+1
    else :
        err_host.append(STORAGE_NAMES) # 1이 아닌 값들은 err_host라는 배열에 저장
    file_open.close()
    os.remove(f'E:/se_daily_report/Storage_NAS_UR/{YMD}_{STORAGE_NAMES}.txt') #파일 읽고 특이사항이 없으면 지워지고 

if ok_count==15:
    storage_text='✅'
else :
    storage_text='❗' + (', '.join(err_host) if err_host else '') + '\t 확인 필요' '\n' 

for NAS_NAMES in NAS_NAME:
    file2_open=open(f'E:/se_daily_report/Storage_NAS_UR/{YMD}_{NAS_NAMES}.txt',"r")
    nas_line=file2_open.readline().strip()
    if nas_line=='1':
        nas_ok_count=nas_ok_count+1
    else :
        nas_err_host.append(NAS_NAMES)
    file2_open.close()
    os.remove(f'E:/se_daily_report/Storage_NAS_UR/{YMD}_{NAS_NAMES}.txt')

if nas_ok_count==5:
    nas_text='✅'
else :
    nas_text='❗ NAS: ' + (', '.join(nas_err_host) if nas_err_host else '') + '\n'
## 스토리지 / NAS 정상 파악
## 총 개수 카운트 후 15개 -> 특이사항 없으면 정상으로 판단
#err_host_text = ', '.join(err_host) if err_host else '✅' #err가 있으면 ,로 구분
# 보낼 메시지
message_text = f'## UR 점검 결과 \n - 스토리지 : {storage_text}\n - NAS : {nas_text} '

# Webex API 엔드포인트
url = 'https://webexapis.com/v1/messages'

# 헤더에 인증 토큰 추가
headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json',
}

# 메시지 데이터
data = {
    'roomId': room_id,  # 메시지를 보낼 방 ID
    'markdown': message_text  # 메시지 텍스트

}
# 메시지 전송 요청
response = requests.post(url, headers=headers, json=data)

# 응답 처리
if response.status_code == 200:
    print('메시지가 성공적으로 전송되었습니다.')
else:
    print(f'오류 발생: {response.status_code} - {response.text}')

