# 공통
EMS_USER_ID = ""
EMS_USER_PASSWORD = ""

DELAY_TIME = 10
EMS_LOGIN_URL = "https://ems.lotte.center/ubitsso/Login"
EMS_SERVER_LIST_SUMMARY_URL_ID = "4414344"

# daily_gather_svr_info_ems
EMS_SERVER_LIST_SUMMARY_URL = "https://ems.lotte.center/management/resourcedetail.tabgroup:tabchange/inventory?t:ac="

# daily_gather_svr_info_ems & daily_gather_svr_id_ems
EMS_SERVER_RESOURE_URL_HEADER = "https://ems.lotte.center/management/resourcedetail.serverdevices.grid.pager/"
EMS_SERVER_RESOURE_URL_TAIL = "?t:ac=4414344&t:cp=server/inventorytabviewblocks&t:inplace=true"

# daily_gather_svr_id_ems
EMS_SERVER_RESOURCE_SUMMARY_URL = "https://ems.lotte.center/management/resourcedetail.tabgroup:tabchange/inventory?t:ac="
EMS_SERVER_FILESYSTEM_RESOURE_URL = "https://ems.lotte.center/management/resourcedetail.tabgroup:tabchange/summary?t:ac="

# realtime_gather_svr_rsrc_ems
# EMS_SVR_RSRC_CPU_MEM_URL = "https://ems.lotte.center/management/resourcedetail/"
EMS_SVR_RSRC_CPU_MEM_URL = "https://ems.lotte.center/management/resourcedetail.tabgroup:tabchange/summary?t:ac="
EMS_SVR_RSRC_FS_URL = "https://ems.lotte.center/management/resourcedetail.tabgroup:tabchange/inventory?t:ac="