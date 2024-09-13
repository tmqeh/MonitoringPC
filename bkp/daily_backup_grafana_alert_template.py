import requests
import json
import yaml

# common & configuration
import cfg.config_grafana as cnf
from cfg.config_path import BACKUP_DIR
from cfg.config_grafana import GRAFANA_HOST as HOST, TEMPLATE_API, ALERTRULE_API, CONTACTPOINT_API, POLICY_API
import cmn.common_msgr as msgr
from cmn.common import get_cur_func_nm as func_nm, get_cur_file_nm as file_nm, get_func_tree as func_tree
from cmn.common_datetime import GRAFANA_TIME as TIME
from cmn.common_file import check_dir

DETAIL_DIR = "grafana_json/grafana_alert/"
FULL_DIR = BACKUP_DIR + DETAIL_DIR


def export_json_data(file_path, data):
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f)
    except EnvironmentError:
        return '{} ERROR: fail to export {}'.format(TIME, file_path)


def get_json_data(key, host, api):
    url = host + api
    headers = {'Authorization' : 'Bearer ' + key}
    r = requests.get(url=url, headers=headers)
    detail_dir = api.split('/')[4] # /api/v1/provisioning/ 뒤에 매개변수를 폴더 명으로
    check_dir(FULL_DIR + detail_dir)
    
    try:
        if r.status_code == 200:
            data_list = r.json()
            
            # 이게 맞나 싶은데.. policies는 필요한 데이터가 2 level에 있어서 예외처리함
            if detail_dir == 'policies':
                data_list = data_list['routes']
            
            for data in data_list:

                if 'settings' in data:
                    data['settings']['token'] = "" # contact-points 토큰 null 처리
                
                if 'receiver' in data: # policies : depth 2 레벨 데이터 get (위에서 예외처리로 바로 핸들링)
                    file_name = data['receiver']
                # if 'routes' in data: # policies 불필요 데이터 skip 처리 및 depth 2 레벨 데이터 get
                #     print(data)
                #     if 'receiver' in data['routes']:
                #         file_name = data['routes']['receiver']
                #         print(file_name)
                
                if 'title' in data:
                    file_name = data['title']
                if 'name' in data:
                    file_name = data['name']
                
                file_path = FULL_DIR + detail_dir + '/' + file_name + '.json'
                export_json_data(file_path, data)

    except Exception as e:
        msgr.put_msgr_target("daily_backup_grafana_alert_template get_json_data except : ", grp_cd="DB9993", send_title="**" + func_nm() + "**", msgr_color="RED")


if __name__ == "__main__":
    # https://github.com/AndrewOcamps/grafana-dashboard-backup
    try:
        # template, alertrule, contactpoint, policy
        get_json_data(cnf.GRAFANA_API, HOST,  TEMPLATE_API    )
        get_json_data(cnf.GRAFANA_API, HOST,  ALERTRULE_API   )
        get_json_data(cnf.GRAFANA_API, HOST,  CONTACTPOINT_API)
        get_json_data(cnf.GRAFANA_API, HOST,  POLICY_API      )

    except yaml.YAMLError as e:
        msgr.put_msgr_target("daily_backup_grafana_alert_template yaml except : " + str(e), grp_cd="DB9993", send_title="**" + file_nm() + "**", msgr_color="RED")
    except Exception as e:
        msgr.put_msgr_target("daily_backup_grafana_alert_template except : " + str(e), grp_cd="DB9993", send_title="**" + file_nm() + "**", msgr_color="RED")

