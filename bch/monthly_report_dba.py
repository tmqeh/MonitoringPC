# common & configuration
from cfg.config_path import IMG_MONTHLY_DIR as IMG_DIR, IMG_EXT
from cfg.config_grafana import GRAFANA_URL
import cmn.common_msgr as msgr
from cmn.common import get_cur_func_nm as func_nm, get_cur_file_nm as file_nm, get_func_tree as func_tree
from cmn.common_datetime import YMDHH24MISS, TIME_YM
from cmn.common_file import check_image, check_dir
from cmn.common_grafana import get_image, write_log


# 1000:500인가? 너무 좁은데
# 월간레포트 전용 상수 (조정 가능)
WIDTH_SIZE        = "&width=1200"
HEIGHT_SIZE       = "&height=400"
TIME_ZONE         = "&tz=Asia%2FSeoul"
TIME_FROM         = "&from=now-30d"
TIME_TO           = "&to=now"
TIME_FROM_STORAGE = "&from=now-1y" # 스토리지 time range 변경
USER_ORG          = "&orgId=1"

# 월간레포트 기타 상수 (MS-SQL에 한정)
TIME_GROUP_SIZE = "&var-TimeRangeGroup=720" # 안 넣었는데도 DEFAULT(자동 조정)라서 동작함
PART_NAME       = "&var-PartName=" # 예시 : 상품권
SERVER_NAME     = "&var-ServerName=All"

# LOGGING
RESULT_LOG = []
RESULT_LOG.append(YMDHH24MISS)
RESULT_LOG_PATH = IMG_DIR + TIME_YM + "/" + TIME_YM + "_monthly_report" + ".txt"

target_info = [  {"title":"월간보고_MS-SQL"         , "resource_type":"CPU"    ,"url":"/BrMGijwVk/" + "monthly-check-mssql-resource-new?panelId=10"}
               , {"title":"월간보고_MS-SQL"         , "resource_type":"Memory" ,"url":"/BrMGijwVk/" + "monthly-check-mssql-resource-new?panelId=12"}
               , {"title":"월간보고_MS-SQL"         , "resource_type":"Storage","url":"/tNtMijwVk/" + "monthly-check-mssql-storage-new?panelId=10"}
               , {"title":"월간보고_Oracle_영업통합", "resource_type":"CPU"    ,"url":"/JR-WmjwVk/" + "monthly-check-oracle-resource-new?panelId=4"}
               , {"title":"월간보고_Oracle_영업통합", "resource_type":"Memory" ,"url":"/JR-WmjwVk/" + "monthly-check-oracle-resource-new?panelId=7"}
               , {"title":"월간보고_Oracle_영업통합", "resource_type":"Storage","url":"/n4uZmCwVz/" + "monthly-check-oracle-tablespace-new?panelId=5"}
               , {"title":"월간보고_Oracle_인사"    , "resource_type":"CPU"    ,"url":"/JR-WmjwVk/" + "monthly-check-oracle-resource-new?panelId=17"}
               , {"title":"월간보고_Oracle_인사"    , "resource_type":"Memory" ,"url":"/JR-WmjwVk/" + "monthly-check-oracle-resource-new?panelId=18"}
               , {"title":"월간보고_Oracle_인사"    , "resource_type":"Storage","url":"/n4uZmCwVz/" + "monthly-check-oracle-tablespace-new?panelId=7"}
               , {"title":"월간보고_Oracle_배치"    , "resource_type":"CPU"    ,"url":"/JR-WmjwVk/" + "monthly-check-oracle-resource-new?panelId=10"}
               , {"title":"월간보고_Oracle_배치"    , "resource_type":"Memory" ,"url":"/JR-WmjwVk/" + "monthly-check-oracle-resource-new?panelId=19"}
               , {"title":"월간보고_Oracle_배치"    , "resource_type":"Storage","url":"/n4uZmCwVz/" + "monthly-check-oracle-tablespace-new?panelId=8"}
               , {"title":"월간보고_Oracle_배송"    , "resource_type":"CPU"    ,"url":"/JR-WmjwVk/" + "monthly-check-oracle-resource-new?panelId=20"}
               , {"title":"월간보고_Oracle_배송"    , "resource_type":"Memory" ,"url":"/JR-WmjwVk/" + "monthly-check-oracle-resource-new?panelId=21"}
               , {"title":"월간보고_Oracle_배송"    , "resource_type":"Storage","url":"/n4uZmCwVz/" + "monthly-check-oracle-tablespace-new?panelId=11"}
            ]

part_list = ["경영지원","마케팅","상품권","인프라","재무","POS","MD"]
# 예시 : http://10.12.111.1:3000/render/d-solo/BrMGijwVk/monthly-check-mssql-resource-new?panelId=10 &orgId=1&tz=Asia%2FSeoul&from=now-30d&to=now&width=1200&height=400 &var-PartName=재무&var-ServerName=All


def get_url(target, option_param=None):
    try:
        file_full_path = IMG_DIR + TIME_YM + "/" + TIME_YM + "_" + target["title"] 
        
        # MS-SQL
        if option_param != None:
            file_full_path = file_full_path + "_" + option_param + "_" + target["resource_type"] + IMG_EXT

        # Oracle
        else:
            file_full_path = file_full_path + "_" + target["resource_type"] + IMG_EXT
        
        # Default
        if target["resource_type"] == "Storage": # 스토리지 time range 변경
            url = GRAFANA_URL + target["url"] + USER_ORG + TIME_ZONE + TIME_FROM_STORAGE + TIME_TO + WIDTH_SIZE + HEIGHT_SIZE
        else:
            url = GRAFANA_URL + target["url"] + USER_ORG + TIME_ZONE + TIME_FROM + TIME_TO + WIDTH_SIZE + HEIGHT_SIZE
        
        # MS-SQL
        if option_param != None:
            url = url + PART_NAME + option_param + SERVER_NAME + TIME_GROUP_SIZE

        # URL debugging
        return url, file_full_path

    except Exception as e:
        # print(func_nm() + ": " + str(e))
        msgr.put_msgr_target(func_tree() + ":\n" + str(e), grp_cd="DBWX99", send_title="**" + func_nm() + "**", msgr_color="RED", send_funcnm=func_nm())


if __name__ == "__main__":
    try:
        check_dir(IMG_DIR + TIME_YM)

        for target in target_info:
            if "MS-SQL" in target["title"]:
                for target_part in part_list:
                    url, file_full_path = get_url(target, target_part)
                    get_image(url, file_full_path)

                    write_log(RESULT_LOG_PATH, file_full_path + " : " + url)
                    # timeout retry용
                    while check_image(file_full_path) != "Y": 
                        get_image(url, file_full_path)
            else:
                url, file_full_path = get_url(target)
                get_image(url, file_full_path)

                write_log(RESULT_LOG_PATH, file_full_path + " : " + url)
                # timeout retry용
                while check_image(file_full_path) != "Y": 
                    get_image(url, file_full_path)
            
        # msgr.put_msgr_target("월간보고 이미지 다운로드 완료", "DB0001")
        msgr.put_msgr_target("월간보고 이미지 다운로드 완료".rstrip("\n"), "DBWX03", send_title="**월간보고 배치**", msgr_color="GREEN", send_funcnm=func_nm())

    except Exception as e:
        # print(file_nm() + ": " + str(e))
        msgr.put_msgr_target(str(e), grp_cd="DBWX99", send_title="**" + file_nm() + "**", msgr_color="RED", send_funcnm=func_nm())