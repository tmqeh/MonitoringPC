# for File Prefix
import datetime

# for sending requests body(data)
import json
import requests

# 모듈설치 : pip --trusted-host pypi.org --trusted-host files.pythonhosted.org install pymssql
#import pymssql as mci
import os
NOW         = datetime.datetime.now()
YMD         = NOW.strftime("%Y%m%d")


jandi_url = 'https://wh.jandi.com/connect-api/webhook/25972562/'
storage_url = '0434ba48023343c27bb1241a55fab1ae'


def JANDI_SEND (type, data, part, color) :
    URL = jandi_url + part
    body_color = color

    header ={"Accept": "application/vnd.tosslab.jandi-v2+json",\
    "Content-Type": "application/json"
    }
    tran={"body": type, "connectColor":body_color,"connectInfo":data} #GREEN / YELLOW / RED
    response = requests.post(url=URL, data=json.dumps(tran), headers=header)


#sapsolman01 서버 UR 점검 진행 후 파일을 전달한다.
#경로 :  /root/daily_check/UR_Check 

storage_UR=[]
nas_UR=[]
ok_count=0
nas_ok_count=0
file_culdb = open(f'E:\se_daily_report\Storage_NAS_UR\{YMD}_culdb.txt', "r")
file_gmsdb = open(f'E:\se_daily_report\Storage_NAS_UR\{YMD}_gmsdb.txt', "r")
file_enrdb = open(f'E:\se_daily_report\Storage_NAS_UR\{YMD}_enrdb.txt', "r")
file_lpdlvdb = open(f'E:\se_daily_report\Storage_NAS_UR\{YMD}_lpdlvdb.txt', "r")
file_eadb = open(f'E:\se_daily_report\Storage_NAS_UR\{YMD}_eadb.txt', "r")
file_hrdb = open(f'E:\se_daily_report\Storage_NAS_UR\{YMD}_hrdb.txt', "r")
file_lpgcsdb = open(f'E:\se_daily_report\Storage_NAS_UR\{YMD}_lpgcsdb.txt', "r")
file_lpscsdb = open(f'E:\se_daily_report\Storage_NAS_UR\{YMD}_lpscsdb.txt', "r")
file_junjadb = open(f'E:\se_daily_report\Storage_NAS_UR\{YMD}_junjadb.txt', "r")
file_leasedb = open(f'E:\se_daily_report\Storage_NAS_UR\{YMD}_leasedb.txt', "r")
file_lpbatap = open(f'E:\se_daily_report\Storage_NAS_UR\{YMD}_lpbatap.txt', "r")
file_lpeaiex = open(f'E:\se_daily_report\Storage_NAS_UR\{YMD}_lpeaiex.txt', "r")
file_lpeaiin = open(f'E:\se_daily_report\Storage_NAS_UR\{YMD}_lpeaiin.txt', "r")
file_lpetlap = open(f'E:\se_daily_report\Storage_NAS_UR\{YMD}_lpetlap.txt', "r")
file_lpsisdb = open(f'E:\se_daily_report\Storage_NAS_UR\{YMD}_lpsisdb.txt', "r")
file_nas_mkt = open(f'E:\se_daily_report\Storage_NAS_UR\{YMD}_nas_mkt.txt', "r")
file_hnas = open(f'E:\se_daily_report\Storage_NAS_UR\{YMD}_hnas.txt', "r")
file_gnas = open(f'E:\se_daily_report\Storage_NAS_UR\{YMD}_gnas.txt', "r")
file_nas_drm = open(f'E:\se_daily_report\Storage_NAS_UR\{YMD}_nas_drm.txt', "r")
file_nas_md = open(f'E:\se_daily_report\Storage_NAS_UR\{YMD}_nas_md.txt', "r")

line_culdb = file_culdb.readline().strip()
line_gmsdb = file_gmsdb.readline().strip()
line_enrdb = file_enrdb.readline().strip()
line_lpdlvdb = file_lpdlvdb.readline().strip()
line_eadb = file_eadb.readline().strip()
line_hrdb = file_hrdb.readline().strip()
line_lpgcsdb = file_lpgcsdb.readline().strip()
line_lpscsdb = file_lpscsdb.readline().strip()
line_junjadb = file_junjadb.readline().strip()
line_leasedb = file_leasedb.readline().strip()
line_lpbatap = file_lpbatap.readline().strip()
line_lpeaiex = file_lpeaiex.readline().strip()
line_lpeaiin = file_lpeaiin.readline().strip()
line_lpetlap = file_lpetlap.readline().strip()
line_lpsisdb = file_lpsisdb.readline().strip()
line_nas_mkt = file_nas_mkt.readline().strip()
line_hnas = file_hnas.readline().strip()
line_gnas = file_gnas.readline().strip()
line_nas_md = file_nas_md.readline().strip()
line_nas_drm = file_nas_drm.readline().strip()


#스토리지, NAS 볼륨 별 점검
if line_culdb == "1" :
    ok_count = ok_count + 1
else :
    storage_UR.append({"title":"문화센터  : 확인필요", "description":""})

if line_gmsdb == "1" :
    ok_count = ok_count + 1
else :
    storage_UR.append({"title":"사은  : 확인필요", "description":""})

if line_enrdb == "1" :
    ok_count = ok_count + 1
else :
    storage_UR.append({"title":"에누리  : 확인필요 ", "description":""})

if line_lpdlvdb == "1" :
    ok_count = ok_count + 1
else :
    storage_UR.append({"title":"배송  : 확인필요", "description":""})

if line_eadb == "1" :
    ok_count = ok_count + 1
else :
    storage_UR.append({"title":"전자결재  : 확인필요", "description":""})

if line_hrdb == "1" :
    ok_count = ok_count + 1
else :
    storage_UR.append({"title":"인사  : 확인필요", "description":""})

if line_lpgcsdb == "1" :
    ok_count = ok_count + 1
else :
    storage_UR.append({"title":"상품권  : 확인필요", "description":""})

if line_lpscsdb == "1" :
    ok_count = ok_count + 1
else :
    storage_UR.append({"title":"매출DB  : 확인필요", "description":""})

if line_junjadb == "1" :
    ok_count = ok_count + 1
else :
    storage_UR.append({"title":"전자증빙  : 확인필요", "description":""})

if line_leasedb == "1" :
    ok_count = ok_count + 1
else :
    storage_UR.append({"title":"내부회계  : 확인필요", "description":""})

if line_lpbatap == "1" :
    ok_count = ok_count + 1
else :
    storage_UR.append({"title":"배치  : 확인필요", "description":""})

if line_lpeaiex == "1" :
    ok_count = ok_count + 1
else :
    storage_UR.append({"title":"외부EAI  : 확인필요", "description":""})

if line_lpeaiin == "1" :
    ok_count = ok_count + 1
else :
    storage_UR.append({"title":"내부EAI  : 확인필요", "description":""})

if line_lpetlap == "1" :
    ok_count = ok_count + 1
else :
    storage_UR.append({"title":"ETL  : 확인필요", "description":""})

if line_lpsisdb == "1" :
    ok_count = ok_count + 1
else :
    storage_UR.append({"title":"영업통합  : 확인필요", "description":""})

if line_nas_mkt == "1" :
    nas_ok_count = nas_ok_count + 1
else :
    nas_UR.append({"title":"마케팅 NAS  : 확인필요", "description":""})

if line_hnas == "1" :
    nas_ok_count = nas_ok_count + 1
else :
    nas_UR.append({"title":"인사 NAS  : 확인필요", "description":""})

if line_gnas == "1" :
    nas_ok_count = nas_ok_count + 1
else :
    nas_UR.append({"title":"재무 NAS  : 확인필요", "description":""})

if line_nas_md == "1" :
    nas_ok_count = nas_ok_count + 1
else :
    nas_UR.append({"title":"MD NAS  : 확인필요", "description":""})

if line_nas_drm == "1" :
    nas_ok_count = nas_ok_count + 1
else :
    nas_UR.append({"title":"DRM NAS (소산) : 확인필요", "description":""})


# 잔디 전달
if ok_count == 15 :
    storage_UR.append({"title":"스토리지 UR 복제 상태 :  정상", "description":""})
    JANDI_SEND ("스토리지 UR 복제 상태", storage_UR, storage_url, "GREEN")
else :
    JANDI_SEND ("스토리지 UR 복제 상태", storage_UR, storage_url, "RED")

if nas_ok_count == 5 :
    nas_UR.append({"title":"NAS UR 복제 상태 : 정상", "description": ""})
    JANDI_SEND ("NAS UR 복제 상태", nas_UR, storage_url, "GREEN")
else :
    JANDI_SEND ("NAS UR 복제 상태", nas_UR, storage_url, "RED")


file_culdb.close()
file_gmsdb.close()
file_enrdb.close()
file_lpdlvdb.close()
file_eadb.close()
file_hrdb.close()
file_lpgcsdb.close()
file_lpscsdb.close()
file_junjadb.close()
file_leasedb.close()
file_lpbatap.close()
file_lpeaiex.close()
file_lpeaiin.close()
file_lpetlap.close()
file_lpsisdb.close()
file_nas_mkt.close()
file_hnas.close()
file_gnas.close()
file_nas_drm.close()
file_nas_md.close()


os.remove(f'E:\se_daily_report\Storage_NAS_UR\{YMD}_culdb.txt')
os.remove(f'E:\se_daily_report\Storage_NAS_UR\{YMD}_gmsdb.txt')
os.remove(f'E:\se_daily_report\Storage_NAS_UR\{YMD}_enrdb.txt')
os.remove(f'E:\se_daily_report\Storage_NAS_UR\{YMD}_lpdlvdb.txt')
os.remove(f'E:\se_daily_report\Storage_NAS_UR\{YMD}_eadb.txt')
os.remove(f'E:\se_daily_report\Storage_NAS_UR\{YMD}_hrdb.txt')
os.remove(f'E:\se_daily_report\Storage_NAS_UR\{YMD}_lpgcsdb.txt')
os.remove(f'E:\se_daily_report\Storage_NAS_UR\{YMD}_lpscsdb.txt')
os.remove(f'E:\se_daily_report\Storage_NAS_UR\{YMD}_junjadb.txt')
os.remove(f'E:\se_daily_report\Storage_NAS_UR\{YMD}_leasedb.txt')
os.remove(f'E:\se_daily_report\Storage_NAS_UR\{YMD}_lpbatap.txt')
os.remove(f'E:\se_daily_report\Storage_NAS_UR\{YMD}_lpeaiex.txt')
os.remove(f'E:\se_daily_report\Storage_NAS_UR\{YMD}_lpeaiin.txt')
os.remove(f'E:\se_daily_report\Storage_NAS_UR\{YMD}_lpetlap.txt')
os.remove(f'E:\se_daily_report\Storage_NAS_UR\{YMD}_lpsisdb.txt')
os.remove(f'E:\se_daily_report\Storage_NAS_UR\{YMD}_nas_mkt.txt')
os.remove(f'E:\se_daily_report\Storage_NAS_UR\{YMD}_hnas.txt')
os.remove(f'E:\se_daily_report\Storage_NAS_UR\{YMD}_gnas.txt')
os.remove(f'E:\se_daily_report\Storage_NAS_UR\{YMD}_nas_drm.txt')
os.remove(f'E:\se_daily_report\Storage_NAS_UR\{YMD}_nas_md.txt')