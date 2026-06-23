# for grafana
GRAFANA_API = "eyJrIjoic21FdzNEcldCdmRIRVFzQ2p2VFJXMGlYYkt5RWVvTkkiLCJuIjoiQVdTX2dyYWZhbmEiLCJpZCI6MX0="
GRAFANA_URL = "https://dbagrafana.dpt.co.kr:3000/render/d-solo"
GRAFANA_HOST = "https://dbagrafana.dpt.co.kr:3000"

TEMPLATE_API     = "/api/v1/provisioning/templates"
ALERTRULE_API    = "/api/v1/provisioning/alert-rules"
CONTACTPOINT_API = "/api/v1/provisioning/contact-points"
POLICY_API       = "/api/v1/provisioning/policies"

# for grafana bot
DASHBOARD_LIST = [{"title" :"daily_check",                    "url" : "", "api" : GRAFANA_API, "parameter" : "없음", "kor_ex" : "일일점검"
                    , "lists":[{"title" :"daily_check_mssql",              "url" : GRAFANA_URL + "/SAYksG54k/" + "daily-check?orgId=1&panelId=9&tz=Asia%2FSeoul" , "width" : "1840", "height" : "1000", "api" : GRAFANA_API, "parameter" : "없음", "kor_ex" : "일일점검 시퀄"} 
                            , {"title"  :"daily_check_oracle",             "url" : GRAFANA_URL + "/SAYksG54k/" + "daily-check?orgId=1&panelId=4&tz=Asia%2FSeoul" , "width" : "1020", "height" : "250",  "api" : GRAFANA_API, "parameter" : "없음", "kor_ex" : "일일점검 오라클"} 
                            , {"title"  :"daily_check_etc_oracle",         "url" : GRAFANA_URL + "/SAYksG54k/" + "daily-check?orgId=1&panelId=17&tz=Asia%2FSeoul", "width" : "1020", "height" : "310",  "api" : GRAFANA_API, "parameter" : "없음", "kor_ex" : "일일점검 기타 오라클"}
                            , {"title"  :"daily_check_etc_dr",             "url" : GRAFANA_URL + "/SAYksG54k/" + "daily-check?orgId=1&panelId=19&tz=Asia%2FSeoul", "width" : "1000", "height" : "410", "api" : GRAFANA_API, "parameter" : "없음", "kor_ex" : "일일점검 기타 dr"}]} 
                , {"title" :"daily_check_mssql",              "url" : GRAFANA_URL + "/SAYksG54k/" + "daily-check?orgId=1&panelId=9&tz=Asia%2FSeoul" , "width" : "1840", "height" : "1000", "api" : GRAFANA_API, "parameter" : "없음", "kor_ex" : "일일점검 시퀄"} 
                , {"title" :"daily_check_oracle",             "url" : GRAFANA_URL + "/SAYksG54k/" + "daily-check?orgId=1&panelId=4&tz=Asia%2FSeoul" , "width" : "1020", "height" : "250",  "api" : GRAFANA_API, "parameter" : "없음", "kor_ex" : "일일점검 오라클"} 
                , {"title" :"daily_check_etc_oracle",         "url" : GRAFANA_URL + "/SAYksG54k/" + "daily-check?orgId=1&panelId=17&tz=Asia%2FSeoul", "width" : "1020", "height" : "310",  "api" : GRAFANA_API, "parameter" : "없음", "kor_ex" : "일일점검 기타 오라클"} 
                , {"title" :"daily_check_etc_dr",             "url" : GRAFANA_URL + "/SAYksG54k/" + "daily-check?orgId=1&panelId=19&tz=Asia%2FSeoul", "width" : "1000", "height" : "410", "api" : GRAFANA_API, "parameter" : "없음", "kor_ex" : "일일점검 기타 dr"} 
                
                , {"title" :"daily_check_etc",                "url" : "", "api" : GRAFANA_API, "parameter" : "없음", "kor_ex" : "일일점검 기타"
                  , "lists":[{"title" :"daily_check_etc_batch",          "url" : GRAFANA_URL + "/SAYksG54k/" + "daily-check?orgId=1&panelId=11&tz=Asia%2FSeoul", "width" :  "500", "height" : "150", "api" : GRAFANA_API, "parameter" : "없음", "kor_ex" : "일일점검 기타 batch (서버명 중복 주의)"}  
                          , {"title"  :"daily_check_etc_sync",           "url" : GRAFANA_URL + "/SAYksG54k/" + "daily-check?orgId=1&panelId=14&tz=Asia%2FSeoul", "width" :  "800", "height" : "220", "api" : GRAFANA_API, "parameter" : "없음", "kor_ex" : "일일점검 기타 sync (서버명 중복 주의)"} 
                          , {"title"  :"daily_check_etc_bcv",            "url" : GRAFANA_URL + "/SAYksG54k/" + "daily-check?orgId=1&panelId=21&tz=Asia%2FSeoul", "width" : "1000", "height" : "200", "api" : GRAFANA_API, "parameter" : "없음", "kor_ex" : "일일점검 기타 bcv"}]} 
                , {"title" :"daily_check_etc_batch",          "url" : GRAFANA_URL + "/SAYksG54k/" + "daily-check?orgId=1&panelId=11&tz=Asia%2FSeoul", "width" :  "500", "height" : "150", "api" : GRAFANA_API, "parameter" : "없음", "kor_ex" : "일일점검 기타 batch (서버명 중복 주의)"} 
                , {"title" :"daily_check_etc_sync",           "url" : GRAFANA_URL + "/SAYksG54k/" + "daily-check?orgId=1&panelId=14&tz=Asia%2FSeoul", "width" :  "800", "height" : "220", "api" : GRAFANA_API, "parameter" : "없음", "kor_ex" : "일일점검 기타 sync (서버명 중복 주의)"} 
                , {"title" :"daily_check_etc_bcv",            "url" : GRAFANA_URL + "/SAYksG54k/" + "daily-check?orgId=1&panelId=21&tz=Asia%2FSeoul", "width" : "1000", "height" : "200", "api" : GRAFANA_API, "parameter" : "없음", "kor_ex" : "일일점검 기타 bcv"} 

                , {"title" :"daily_check_etc_oracle_storage",    "url" : GRAFANA_URL + "/SAYksG54k/" + "daily-check?orgId=1&panelId=13&tz=Asia%2FSeoul",                                 "width" : "1200", "height" : "450", "api" : GRAFANA_API, "parameter" : "없음", "kor_ex" : "일일점검 기타 오라클 스토리지"}  
                , {"title" :"daily_check_etc_oracle_detail",     "url" : GRAFANA_URL + "/Jkqas16Wk/" + "daily-check-etc-oracle-detail-history?orgId=1&tz=Asia%2FSeoul&panelId=2",        "width" : "2000", "height" : "800", "api" : GRAFANA_API, "parameter" : "없음", "kor_ex" : "일일점검 기타 오라클 상세"} 
                , {"title" :"daily_check_mssql_detail_storage",  "url" : GRAFANA_URL + "/mxOhUElWz/" + "daily-check-mssql-detail-storage-history?orgId=1&tz=Asia%2FSeoul&panelId=2",     "width" : "2000", "height" : "800", "api" : GRAFANA_API, "parameter" : "없음", "kor_ex" : "일일점검 시퀄 상세 디스크"} 
                , {"title" :"daily_check_oracle_detail_storage", "url" : GRAFANA_URL + "/DzyaUJeZz/" + "daily-check-oracle-detail-tablespace-history?orgId=1&tz=Asia%2FSeoul&panelId=2", "width" : "2000", "height" : "800", "api" : GRAFANA_API, "parameter" : "없음", "kor_ex" : "일일점검 오라클 상세 디스크"} 
                
                , {"title" :"daily_check_mssql_detail_err",  "url" : "", "api" : GRAFANA_API, "parameter" : "없음", "kor_ex" : "일일점검 시퀄 상세 에러"} 
                , {"title" :"daily_check_oracle_detail_err", "url" : "", "api" : GRAFANA_API, "parameter" : "없음", "kor_ex" : "일일점검 오라클 상세 에러"} 
                
                , {"title" :"daily_check_netbackup",         "url" : GRAFANA_URL + "/SAYksG54k/" + "daily-check?orgId=1&panelId=23&tz=Asia%2FSeoul" , "width" : "1400","height" : "550", "api" : GRAFANA_API, "parameter" : "없음", "kor_ex" : "일일점검 넷백업"} 
                
                # for executing realtime% lists below
                # MS-SQL
                , {"title" :"realtime_mssql_resource",         "url" : "", "api" : GRAFANA_API, "parameter" : "서버명(default=All)", "kor_ex" : "실시간 시퀄 사용량 매출"
                    , "lists":[{"title" :"realtime_mssql_cpu_resource",        "url" : GRAFANA_URL + "/ce2xrcn4k/" + "realtime-mssql-cpu?orgId=1&tz=Asia%2FSeoul&panelId=2&from=now-6h&to=now&var-ServerName=",         "width" : "1000", "height" : "500", "api" : GRAFANA_API}
                            , {"title" :"realtime_mssql_memory_resource",      "url" : GRAFANA_URL + "/E4LqUcnVk/" + "realtime-mssql-memory?orgId=1&tz=Asia%2FSeoul&panelId=2&from=now-6h&to=now&var-ServerName=",      "width" : "1000", "height" : "500", "api" : GRAFANA_API}
                            , {"title" :"realtime_mssql_request_resource",     "url" : GRAFANA_URL + "/GyhSLo7Vk/" + "realtime-mssql-request?orgId=1&tz=Asia%2FSeoul&panelId=2&from=now-6h&to=now&var-ServerName=",     "width" : "1000", "height" : "500", "api" : GRAFANA_API}
                            , {"title" :"realtime_mssql_transaction_resource", "url" : GRAFANA_URL + "/ZTUOh174k/" + "realtime-mssql-transaction?orgId=1&tz=Asia%2FSeoul&panelId=2&from=now-6h&to=now&var-ServerName=", "width" : "1000", "height" : "500", "api" : GRAFANA_API}
                            , {"title" :"realtime_mssql_bufferhit_resource",   "url" : GRAFANA_URL + "/yVjS017Vz/" + "realtime-mssql-bufferhit?orgId=1&tz=Asia%2FSeoul&panelId=2&from=now-6h&to=now&var-ServerName=",   "width" : "1000", "height" : "500", "api" : GRAFANA_API}
                            , {"title" :"realtime_mssql_storage_resource",     "url" : GRAFANA_URL + "/Eeybr5nVk/" + "realtime-mssql-storage?orgId=1&tz=Asia%2FSeoul&panelId=2&from=now-30d&to=now&var-ServerName=",    "width" : "1000", "height" : "500", "api" : GRAFANA_API}]} 
                    , {"title" :"realtime_mssql_cpu_resource",         "url" : GRAFANA_URL + "/ce2xrcn4k/" + "realtime-mssql-cpu?orgId=1&tz=Asia%2FSeoul&panelId=2&from=now-6h&to=now&var-ServerName=",                 "width" : "1000", "height" : "500", "api" : GRAFANA_API, "parameter" : "서버명(default=All)", "kor_ex" : "실시간 시퀄 시피유 사용량 매출"} 
                    , {"title" :"realtime_mssql_memory_resource",      "url" : GRAFANA_URL + "/E4LqUcnVk/" + "realtime-mssql-memory?orgId=1&tz=Asia%2FSeoul&panelId=2&from=now-6h&to=now&var-ServerName=",              "width" : "1000", "height" : "500", "api" : GRAFANA_API, "parameter" : "서버명(default=All)", "kor_ex" : "실시간 시퀄 메모리 사용량 매출"} 
                    , {"title" :"realtime_mssql_request_resource",     "url" : GRAFANA_URL + "/GyhSLo7Vk/" + "realtime-mssql-request?orgId=1&tz=Asia%2FSeoul&panelId=2&from=now-6h&to=now&var-ServerName=",             "width" : "1000", "height" : "500", "api" : GRAFANA_API, "parameter" : "서버명(default=All)", "kor_ex" : "실시간 시퀄 요청 사용량 매출"} 
                    , {"title" :"realtime_mssql_transaction_resource", "url" : GRAFANA_URL + "/ZTUOh174k/" + "realtime-mssql-transaction?orgId=1&tz=Asia%2FSeoul&panelId=2&from=now-6h&to=now&var-ServerName=",         "width" : "1000", "height" : "500", "api" : GRAFANA_API, "parameter" : "서버명(default=All)", "kor_ex" : "실시간 시퀄 트랜잭션 사용량 매출"} 
                    , {"title" :"realtime_mssql_bufferhit_resource",   "url" : GRAFANA_URL + "/yVjS017Vz/" + "realtime-mssql-bufferhit?orgId=1&tz=Asia%2FSeoul&panelId=2&from=now-6h&to=now&var-ServerName=",           "width" : "1000", "height" : "500", "api" : GRAFANA_API, "parameter" : "서버명(default=All)", "kor_ex" : "실시간 시퀄 버퍼 사용량 매출"} 
                    , {"title" :"realtime_mssql_storage_resource",     "url" : GRAFANA_URL + "/Eeybr5nVk/" + "realtime-mssql-storage?orgId=1&tz=Asia%2FSeoul&panelId=2&from=now-30d&to=now&var-ServerName=",            "width" : "1000", "height" : "500", "api" : GRAFANA_API, "parameter" : "서버명(default=All)", "kor_ex" : "실시간 시퀄 스토리지 사용량 매출"} 

                 # Oracle
                , {"title" :"realtime_oracle_resource",                    "url" : "", "api" : GRAFANA_API, "parameter" : "서버명(default=All)", "kor_ex" : "실시간 오라클 사용량 영업통합#1"
                , "lists":[{"title" :"realtime_oracle_cpu_resource",       "url" : GRAFANA_URL + "/B0V30U44k/" + "realtime-oracle-cpu?orgId=1&tz=Asia%2FSeoul&panelId=2&from=now-6h&to=now&var-ServerName=",        "width" : "1000", "height" : "500", "api" : GRAFANA_API}
                        , {"title" :"realtime_oracle_memory_resource",     "url" : GRAFANA_URL + "/lb53A8VVk/" + "realtime-oracle-memory?orgId=1&tz=Asia%2FSeoul&panelId=2&from=now-6h&to=now&var-ServerName=",     "width" : "1000", "height" : "500", "api" : GRAFANA_API}
                        , {"title" :"realtime_oracle_execution_resource",  "url" : GRAFANA_URL + "/LKJqAU4Vk/" + "realtime-oracle-executions?orgId=1&tz=Asia%2FSeoul&panelId=2&from=now-6h&to=now&var-ServerName=", "width" : "1000", "height" : "500", "api" : GRAFANA_API}
                        , {"title" :"realtime_oracle_session_resource",    "url" : GRAFANA_URL + "/2JP3A8VVk/" + "realtime-oracle-sessions?orgId=1&tz=Asia%2FSeoul&panelId=2&from=now-6h&to=now&var-ServerName=",   "width" : "1000", "height" : "500", "api" : GRAFANA_API}]} 
                , {"title" :"realtime_oracle_cpu_resource",                "url" : GRAFANA_URL + "/B0V30U44k/" + "realtime-oracle-cpu?orgId=1&tz=Asia%2FSeoul&panelId=2&from=now-6h&to=now&var-ServerName=",        "width" : "1000", "height" : "500", "api" : GRAFANA_API, "parameter" : "서버명(default=All)", "kor_ex" : "실시간 오라클 씨피유 사용량 영업통합#1"} 
                , {"title" :"realtime_oracle_memory_resource",             "url" : GRAFANA_URL + "/lb53A8VVk/" + "realtime-oracle-memory?orgId=1&tz=Asia%2FSeoul&panelId=2&from=now-6h&to=now&var-ServerName=",     "width" : "1000", "height" : "500", "api" : GRAFANA_API, "parameter" : "서버명(default=All)", "kor_ex" : "실시간 오라클 메모리 사용량 영업통합#1"} 
                , {"title" :"realtime_oracle_execution_resource",          "url" : GRAFANA_URL + "/LKJqAU4Vk/" + "realtime-oracle-executions?orgId=1&tz=Asia%2FSeoul&panelId=2&from=now-6h&to=now&var-ServerName=", "width" : "1000", "height" : "500", "api" : GRAFANA_API, "parameter" : "서버명(default=All)", "kor_ex" : "실시간 오라클 실행 사용량 영업통합#1"} 
                , {"title" :"realtime_oracle_session_resource",            "url" : GRAFANA_URL + "/2JP3A8VVk/" + "realtime-oracle-sessions?orgId=1&tz=Asia%2FSeoul&panelId=2&from=now-6h&to=now&var-ServerName=",   "width" : "1000", "height" : "500", "api" : GRAFANA_API, "parameter" : "서버명(default=All)", "kor_ex" : "실시간 오라클 세션 사용량 영업통합#1"} 

                # for executing work 
                , {"title" :"work",            "url" : GRAFANA_URL + "/0wEdUWTnk/" + "work-check?orgId=1&tz=Asia%2FSeoul&panelId=4",                    "width" : "1200", "height" : "450", "api" : GRAFANA_API, "parameter" : "없음", "kor_ex" : "근태"} 
                , {"title" :"work_part",       "url" : GRAFANA_URL + "/0wEdUWTnk/" + "work-check?orgId=1&tz=Asia%2FSeoul&panelId=5&var-PartNm=",        "width" : "1000", "height" : "600", "api" : GRAFANA_API, "parameter" : "(필수)파트명", "kor_ex" : "근태 파트 인프라"} 
                , {"title" :"work_indivisual", "url" : GRAFANA_URL + "/0wEdUWTnk/" + "work-check?orgId=1&tz=Asia%2FSeoul&panelId=10&var-IndivisualNm=", "width" : "1000", "height" : "500", "api" : GRAFANA_API, "parameter" : "(필수)팀원명", "kor_ex" : "근태 개인 김진우"} 

                # for manual
                , {"title" : "help"}
                , {"title" : "keyword"}
                 ]
