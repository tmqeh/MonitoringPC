# common & configuration
from cfg.config_path import IMG_DAILY_DIR as IMG_DIR, IMG_EXT
from cfg.config_grafana import DASHBOARD_LIST
import cmn.common_msgr as msgr
from cmn.common import get_cur_func_nm as func_nm, get_cur_file_nm as file_nm, get_func_tree as func_tree
from cmn.common_datetime import YMD
from cmn.common_file import check_image
from cmn.common_grafana import get_image


target_list = [
               'daily_check_mssql'
             , 'daily_check_oracle'
             , 'daily_check_etc_oracle'
             , 'daily_check_etc_dr'
              ]


if __name__ == "__main__":
    try:
        for target in target_list:
            for data in DASHBOARD_LIST:
                if data['title'] == target:
                    file_name = YMD + "_" + data['title'].replace(' ','-') + "_Grafana_Daily" + IMG_EXT
                    file_full_path = IMG_DIR + file_name
                    url = data['url'] + '&width=' + data['width'] + '&height=' + data['height'] 
                    get_image(url, file_full_path)

                    # timeout retry용
                    while check_image(file_full_path) != 'Y': 
                        get_image(url, file_full_path)
                    
                    # Send image
                    msgr.put_msgr_target(data['title'], grp_cd='DB0001', img_file_path=file_full_path)
    except Exception as e:
        # print(file_nm() + ": " + str(e))
        msgr.put_msgr_target(str(e), grp_cd="DB9993", send_title="**" + file_nm() + "**", msgr_color="RED")