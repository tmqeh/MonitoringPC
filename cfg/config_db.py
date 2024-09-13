DATASOURCE = {"maxgDB"   : {"host"  :"10.7.7.42",   "port":"9600", "user":"lpview",    "password":"lpview12!",  "database":"MFO"},
              "monDB"    : {"server":"10.7.7.42",   "port":"2001", "user":"lpview",    "password":"lpview12!",  "database":"MonitoringDB", "charset":"UTF-8"},
              "monPC"    : {"server":"10.12.111.1", "port":"2001", "user":"lpmonmt",   "password":"lpmonmt12!", "database":"MonitoringDB", "charset":"UTF-8"},
              "workDB"   : {"server":"10.13.8.11",  "port":"1444", "user":"lpview",    "password":"lpview12!",  "database":"posDuty",      "charset":"UTF-8"},
              "batDB"    : {"server":"10.7.17.51",  "port":"9500", "user":"ORADBA",    "password":"imsi00",     "database":"LPCTR"},
              "metaDB"   : {"server":"10.44.1.80", "port":"9500", "user":"ORADBA",     "password":"imsi00",     "database":"LDSIS"}
              }

        # conn = cx.connect(dsn='10.7.17.151:9500/LDSIS', user='아이디', password='비밀번호', encoding='UTF-8') #, charset='EUC-KR'