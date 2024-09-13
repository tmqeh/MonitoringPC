# common & configuration
from cfg.config_grafana import GRAFANA_API, GRAFANA_URL
import cmn.common_msgr as msgr
from cmn.common import get_cur_func_nm as func_nm, get_cur_file_nm as file_nm, get_func_tree as func_tree
from cmn.common_db import monPC
from cmn.common_datetime import YMD

URL_ARR = [{"title" :"daily_check_sap_rsrc", "title_kr" :"SAP 리소스 일일점검", "url" : GRAFANA_URL + "/C_8ACVl7k/" + "daily-check-se?orgId=1&panelId=2&tz=Asia%2FSeoul", "width" : "1000","height" : "860",  "api" : GRAFANA_API, "GRP_CD" : "FI0003", "PART_CL_CD" : "재무"} 
         , {"title" :"daily_check_sap_stat", "title_kr" :"SAP 상태 일일점검",   "url" : GRAFANA_URL + "/C_8ACVl7k/" + "daily-check-se?orgId=1&panelId=4&tz=Asia%2FSeoul", "width" : "1500","height" : "300",  "api" : GRAFANA_API, "GRP_CD" : "FI0003", "PART_CL_CD" : "재무"} 
         , {"title" :"daily_check_md_rsrc",  "title_kr" :"MD 리소스 일일점검",  "url" : GRAFANA_URL + "/C_8ACVl7k/" + "daily-check-se?orgId=1&panelId=2&tz=Asia%2FSeoul", "width" : "1000","height" : "930",  "api" : GRAFANA_API, "GRP_CD" : "MD0003", "PART_CL_CD" : "MD"} 
         , {"title" :"daily_check_md_stat",  "title_kr" :"MD 상태 일일점검",    "url" : GRAFANA_URL + "/C_8ACVl7k/" + "daily-check-se?orgId=1&panelId=4&tz=Asia%2FSeoul", "width" : "1500","height" : "1050", "api" : GRAFANA_API, "GRP_CD" : "MD0003", "PART_CL_CD" : "MD"} 
          ]

SERVER_LIST = [{"호스트명" :"IBM#1",     "서버리스트" :["lpsisdb01"]}
             , {"호스트명" :"IBM#2",     "서버리스트" :["lpsisdb02"]}
             , {"호스트명" :"IBM#3",     "서버리스트" :["lpbatap01","lpeaiex01","lpeaiin01","lpediww01","lpetlap01","lpsisap01","lpsisap03","lpsiswi01","lpsiswo01"]}
             , {"호스트명" :"IBM#4",     "서버리스트" :["lpbatap02","lpeaiex02","lpeaiin02","lpediww02","lpetlap02","lpsisap02","lpsisap04","lpsiswi02","lpsiswo02"]}
             , {"호스트명" :"sapflex01", "서버리스트" :["jmtibinap01","jmtibinap03","sapbcpdb01","sapbcpap01","sapascs01","jmalpb01"]}
             , {"호스트명" :"sapflex02", "서버리스트" :["jmtibinap02","jmtibinap04","sapbcpdb02","sapbcpap02","sapers01","sapdbmon01","jmalpbdev01"]}
             , {"호스트명" :"sapflex03", "서버리스트" :["saprouter1","sapbcpap03","sapbcqdb01","sapbcqap01"]}
             , {"호스트명" :"sapflex04", "서버리스트" :["jmtibnfs01","jmsgq01","sapbcpap04","sapsolman01","sapcockpit01","sapdevdb01","sapdevap01"]}
              ]

# 임계치 상수화
CPU_THRESHOLD = 70
MEM_THRESHOLD = 70
DSK_THRESHOLD = 85


def get_title_kr(args):
    data = URL_ARR[next((i for i, item in enumerate(URL_ARR) if item["title"] == args), None)]
    # url = data["url"] + "&width=" + data["width"] + "&height=" + data["height"] + "&var-PartNm=" + data["PART_CL_CD"]

    # redering url로 링크 클릭하면 바로 볼 수 있게 하고 싶었는데.
    # 1. auth.anonymous 권한 줘도 접근 안됨
    # 2. 모바일에서는 IP 호스팅이 안되서 안됨
    # url 빼는걸로 변경
    # return "[**" + data["title_kr"] + "**](" + url + ")"
    return "**" + data["title_kr"] + "**"


def list_srv_rsrc_log(title, part_cl_cd, grp_cd, args=YMD):
    conn = monPC(func_nm())
    sqlTxt = """
             SELECT Z.hostName AS [호스트명]
                  -- , Z.serviceName AS [서비스명]
                  , Z.IP_ADDR AS [IP]
                  , Z.CPUUSE AS [CPU사용량(%)]
                  , Z.MEMUSE AS [메모리사용량(%)]
                  , Z.DSKCHK AS [디스크85%사용초과]
                  , STUFF((SELECT ', ' + X.path_name + ' (' + convert(varchar,x.use_pct) + ')'
                             FROM (SELECT collectDT, hostname, path_name, use_pct, ROW_NUMBER() OVER (PARTITION BY c.hostname, path_name order by c.rgst_dtm desc) rnk
                                     FROM TB_SVR_FS_CHK_L c
                                    WHERE c.CollectDT = Z.CollectDT
                                      AND c.hostname = z.hostname
                                      AND c.use_pct >= %d
                                      AND abs(DATEDIFF(s, c.RGST_DTM, z.RGST_DTM)) < 300
                                      ) X where X.rnk = 1
                                  ORDER BY X.path_name
                              FOR XML PATH('')), 1, LEN(','), '') AS [경로]
                  , Z.RGST_DTM AS [일시]
                FROM (SELECT A.hostName
                          -- , A.serviceName
                          , B.CollectDT
                          , A.IP_ADDR
                          , B.CPUUSE
                          , B.MEMUSE
                          , B.DSKCHK
                          , B.RGST_DTM
                          , ROW_NUMBER() OVER (PARTITION BY a.hostname order by b.rgst_dtm desc) rnk
                        FROM TB_SVR_COMM_INFO_M (NOLOCK) A
                        LEFT OUTER JOIN TB_SVR_RSRC_CHK_L  (NOLOCK) B
                          ON A.hostName = B.hostName
                        AND B.collectDt = %s
                      WHERE A.RSRC_YN = 'Y'
                        AND A.PART_CL_CD = %s
                        -- 문자 전송 임계치
                        AND (cpuUse >=%d OR memUse >=%d OR dskChk >=1 OR B.RGST_DTM IS NULL)
                      )  Z
                WHERE RNK = 1
             """

    try:
        # print(sqlTxt)
        data = conn.query(sqlTxt, (DSK_THRESHOLD, args, part_cl_cd, CPU_THRESHOLD, MEM_THRESHOLD))
        content = []

        if conn.rows() > 0:
            results = [dict((conn.description()[i][0], value) 
                            for i, value in enumerate(row)) for row in data]

            # 시작은 정상 signal (GREEN)으로 시작, 체크로직 타면서 긴급도 변경
            # LOOP를 돌면서 심각도에 따라서 GREEN > YELLOW > RED로 변경 됨 (RED가 되면 더이상 변하지 않음)
            alert_color = "GREEN"

            for result in results:
                if result["일시"] == None:  # data가 누락 될 경우, RED
                    # print(result["호스트명"] + "(" + result["IP"] + ")" + " No Data found")
                    result["CPU사용량(%)"] = 0  # 비교문에 None Type이 들어가면 오류가 발생
                    result["메모리사용량(%)"] = 0
                    result["디스크85%사용초과"] = 0
                    result["일시"] = args + " **데이터없음**"
                    alert_color = "RED"

                if alert_color == "GREEN":  # 기본 임계치 초과 시, YELLOW
                    if result["CPU사용량(%)"] >= 70 or result["메모리사용량(%)"] >= 70:
                        alert_color = "YELLOW"

                elif alert_color == "YELLOW":
                    if (result["CPU사용량(%)"] >= 80 or result["메모리사용량(%)"] >= 80 or result["디스크85%사용초과"] > 0):
                        # print("RED 조건 성립")
                        alert_color = "RED"

                title_content = result["호스트명"] + "(" + result["IP"] + ")"

                if isinstance(result["일시"], str):
                    desc_content = result["일시"]

                elif isinstance(result["경로"], str):
                     desc_content = "CPU사용량(%):"      + str(result["CPU사용량(%)"])      + "\n" \
                                 + "메모리사용량(%):"   + str(result["메모리사용량(%)"])   + "\n" \
                                 + "디스크85%사용초과:" + str(result["디스크85%사용초과"]) + "\n" \
                                 + str(result["경로"])
                else:
                    desc_content = "CPU사용량(%):"      + str(result["CPU사용량(%)"])      + "\n" \
                                 + "메모리사용량(%):"   + str(result["메모리사용량(%)"])   + "\n" \
                                 + "디스크85%사용초과:" + str(result["디스크85%사용초과"]) 

                content.append({"title": title_content, "description": desc_content})
                # 실시간으로 바꿀려면 이부분을 title_content + \n + desc_content 이런식으로 바꿔야됨

            message_content = ""
            for i, message in enumerate(content):
                message_content = message_content + "**" + message["title"] + "**" + "\n" + message["description"]  # 이렇게 해야겠네
                if i == len(content) - 1:  # 마지막줄은 개행 추가 안함
                    continue
                else:
                    message_content = message_content + "\n\n"
            msgr.put_msgr_target(message_content, grp_cd, send_title = get_title_kr(title), msgr_color = alert_color)

        else:
            msgr.put_msgr_target("점검 특이사항 없음", grp_cd,send_title = get_title_kr(title), msgr_color = "GREEN")

    except Exception as e:
        # print(func_nm() + ": " + str(e))
        msgr.put_msgr_target(func_tree() + ":\n" + str(e), grp_cd="DB9993", send_title="**" + func_nm() + "**", msgr_color="RED")
        msgr.put_msgr_target(str(e), grp_cd, send_title = get_title_kr(title), msgr_color = "RED")

    finally:
        sqlTxt = ""
        conn.close()


def list_srv_stat_log(title, part_cl_cd, grp_cd, args=YMD):
    conn = monPC(func_nm())
    sqlTxt = """
              SELECT [호스트명], [상태이름], [상태], RGST_DTM
                FROM (SELECT A.hostName as [호스트명], B.statusName as [상태이름], B.status [상태], B.RGST_DTM
                          , ROW_NUMBER() OVER (PARTITION BY A.HOSTNAME, B.STATUSNAME ORDER BY B.RGST_DTM DESC) RNK
                          , A.serviceName
                        FROM TB_SVR_COMM_INFO_M (NOLOCK) A
                      INNER JOIN TB_Svr_Stat_Chk_L  (NOLOCK) B
                          ON A.hostName = B.hostName
                        AND B.COLLECTDT = %s
                        -- AND B.STATUS = 'NOK'
                      WHERE A.STAT_YN = 'Y'
                        AND A.PART_CL_CD = %s
                    ) Z
              WHERE RNK = 1
                AND z.[상태] = 'NOK'
             """

    try:
        # print(sqlTxt)
        data = conn.query(sqlTxt, (args, part_cl_cd))

        content = []

        if conn.rows() > 0:
            alert_color = "GREEN"
            results = [dict((conn.description()[i][0], value) 
                            for i, value in enumerate(row)) for row in data]

            for result in results:
                if alert_color == "GREEN":
                    if result["상태"] == "NOK":
                        alert_color = "RED"

                # 이렇게 하면 2중 배열이됨
                # warning_server_lists = [row["서버리스트"] for row in server_list if result["호스트명"] == row['호스트명']]

                # 아래처럼 한번 더 씌움
                warning_server_lists = [row for rowset in SERVER_LIST if result["호스트명"] == rowset['호스트명'] for row in rowset["서버리스트"]]

                if warning_server_lists:
                    content.append({"title":"호스트명:" + result["호스트명"], "description":"상태이름:" + result["상태이름"] + "\n" \
                                             + "상태:" + result["상태"] + "\n" + "서버리스트:" + str(warning_server_lists)})
                # 실시간으로 바꿀려면 이부분을 title_content + \n + desc_content 이런식으로 바꿔야됨
                else:
                    content.append({"title":"호스트명:" + result["호스트명"], "description":"상태이름:" + result["상태이름"] + "\n" \
                                              +"상태:" + result["상태"] }) 
                # 실시간으로 바꿀려면 이부분을 title_content + \n + desc_content 이런식으로 바꿔야됨

            message_content = ""
            for i, message in enumerate(content):
                message_content = message_content + "**" + message["title"] + "**" + "\n" + message["description"]  # 이렇게 해야겠네
                if i == len(content) - 1:  # 마지막줄은 개행 추가 안함
                    continue
                else:
                    message_content = message_content + "\n\n"
            msgr.put_msgr_target(message_content, grp_cd, send_title = get_title_kr(title), msgr_color = alert_color)

        else:
            msgr.put_msgr_target("점검 특이사항 없음", grp_cd,send_title = get_title_kr(title), msgr_color = "GREEN")

    except Exception as e:
        # print(func_nm() + ": " + str(e))
        msgr.put_msgr_target(func_tree() + ":\n" + str(e), grp_cd="DB9993", send_title="**" + func_nm() + "**", msgr_color="RED")
        msgr.put_msgr_target(str(e), grp_cd, send_title = get_title_kr(title), msgr_color = "RED")

    finally:
        sqlTxt = ""
        conn.close()


# MAIN
if __name__ == "__main__":
    for data in URL_ARR:
        if data["title"] == "daily_check_sap_rsrc":
            list_srv_rsrc_log(data["title"], data["PART_CL_CD"], data["GRP_CD"])
        elif data["title"] == "daily_check_sap_stat":
            list_srv_stat_log(data["title"], data["PART_CL_CD"], data["GRP_CD"])
        elif data["title"] == "daily_check_md_rsrc":
            list_srv_rsrc_log(data["title"], data["PART_CL_CD"], data["GRP_CD"])
        elif data["title"] == "daily_check_md_stat":
            list_srv_stat_log(data["title"], data["PART_CL_CD"], data["GRP_CD"])

        # for test
        # if data['title'] == 'daily_check_md_stat':
        #   list_srv_stat_log(data["title"], data["PART_CL_CD"], data["GRP_CD"])
