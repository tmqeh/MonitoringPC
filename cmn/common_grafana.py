import requests

# common & configuration
from cfg.config_grafana import GRAFANA_API


def get_image(url, file_full_path):
    header={'Authorization':'Bearer ' + GRAFANA_API}
    # File DownLoad
    response = requests.get(url, stream=True, headers=header)
    with open(file_full_path, 'wb') as download:
        download.write(response.content)


def write_log(log_path, content):
    # Logging
    with open(log_path, 'a') as logging_file: # with 절은 마지막에 자동 close
        logging_file.write(content + "\n") 

