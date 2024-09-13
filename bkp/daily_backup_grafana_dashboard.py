import os
import requests
import json
import yaml
from datetime import datetime

# common & configuration
import cfg.config_grafana as cnf
import cmn.common_msgr as msgr
from cmn.common import get_cur_func_nm as func_nm, get_cur_file_nm as file_nm, get_func_tree as func_tree
from cfg.config_path import BACKUP_DIR
from cfg.config_grafana import GRAFANA_HOST as HOST

DETAIL_DIR = "grafana_json/MonitoringPC"
FULL_DIR = BACKUP_DIR + DETAIL_DIR
from cmn.common_file import check_dir


def get_dashboard_list(key, host):
    now = datetime.now()
    time = now.strftime("%d/%m/%Y %H:%M:%S")
    url = host + '/api/search/'
    headers = {'Authorization' : 'Bearer ' + key}

    try:
        r = requests.get(url=url, headers=headers)

        if r.status_code == 200:
            dashboard_list = r.json()
            result_list = []
            for dashboard in dashboard_list:
                result_list.append(dashboard)
            return result_list
        else:
            return '{} ERROR: HTTP {} {}'.format(time, r.status_code, url)
    except Exception as e:
        msgr.put_msgr_target("daily_backup_grafana_dashboard get_dashboard_list except : " + str(e), grp_cd="DB9993", send_title="**" + func_nm() + "**", msgr_color="RED")


def get_folder_list(key, host):
    now = datetime.now()
    time = now.strftime("%d/%m/%Y %H:%M:%S")
    url = host + '/api/folders/'
    headers = {'Authorization' : 'Bearer ' + key}

    try:
        r = requests.get(url=url, headers=headers)
        if r.status_code == 200:
            folder_list = r.json()
            result_list = []
            for folder_name in folder_list:
                result_list.append(folder_name)
            return result_list
        else:
            return '{} ERROR: HTTP {} {}'.format(time, r.status_code, url)
    except Exception as e:
        msgr.put_msgr_target("daily_backup_grafana_dashboard get_folder_list except : " + str(e), grp_cd="DB9993", send_title="**" + func_nm() + "**", msgr_color="RED")


def backup_dashboard(uid, key, host, path):
    now = datetime.now()
    time = now.strftime("%d/%m/%Y %H:%M:%S")
    backup_dir = path
    url = host + '/api/dashboards/uid/' + uid
    headers = {'Authorization' : 'Bearer ' + key}

    try:
        r = requests.get(url=url, headers=headers)

        if r.status_code == 200:
            dashboard_json = r.json()

            meta = dashboard_json['meta']
            #version = meta['version']
            #url = meta['url']
            #created = meta['created']
            #createdBy = meta['createdBy']
            #updated = meta['updated']
            #updatedBy = meta['updatedBy']
            slug = meta['slug']

            dashboard = dashboard_json['dashboard']
            dashboard_path = backup_dir + '/' + slug + '.json'
            try:
                with open(dashboard_path, 'w') as f:
                    json.dump(dashboard, f)
            except EnvironmentError:
                return '{} ERROR: fail to export {}'.format(time, slug)
            
            return '{} SUCCESS: {}'.format(time, slug)
        else:
            return '{} ERROR: HTTP {} {}'.format(time, r.status_code, url)
    except Exception as e:
        msgr.put_msgr_target("daily_backup_grafana_dashboard backup_dashboard except : " + str(e), grp_cd="DB9993", send_title="**" + func_nm() + "**", msgr_color="RED")


if __name__ == "__main__":
    # https://github.com/AndrewOcamps/grafana-dashboard-backup
    try:
        folder_list = get_folder_list(cnf.GRAFANA_API, HOST)
        
        for folder_name in folder_list:
            path = os.path.join(FULL_DIR, folder_name['title'])
            
            check_dir(path)
            
            for dashboard_list in get_dashboard_list(cnf.GRAFANA_API, HOST):
                if "folderUid" in dashboard_list:
                    if folder_name['uid'] == dashboard_list['folderUid']:
                        print(backup_dashboard(dashboard_list['uid'], cnf.GRAFANA_API, HOST, path))

    except yaml.YAMLError as e:
        msgr.put_msgr_target("daily_backup_grafana_dashboard yaml except : ", grp_cd="DB9993", send_title="**" + file_nm() + "**", msgr_color="RED")
    except Exception as e:
        msgr.put_msgr_target("daily_backup_grafana_dashboard except : ", grp_cd="DB9993", send_title="**" + file_nm() + "**", msgr_color="RED")
