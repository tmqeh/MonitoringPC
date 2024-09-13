import os # for open, rename
import pandas as pd # row to column을 위해 pandas 활용

# common & configuration
from cfg.config_path import SE_LOG_PATH as LOG_HOME, TXT_EXT
import cmn.common_msgr as msgr
from cmn.common import get_cur_func_nm as func_nm, get_cur_file_nm as file_nm, get_func_tree as func_tree
from cmn.common_db import monPC
from cmn.common_datetime import NETBACKUP_YMD, YMD
from cmn.common_file import check_file
from cmn.common_sql import get_string, get_number

# file path
ERR_PATH       = LOG_HOME + "err"
OLD_PATH       = LOG_HOME + "old"
TARGET_PATH    = LOG_HOME 
NETBACKUP_PATH = LOG_HOME + "Netbackup"

# SE0001 : SE 잔디
TARGET_LIST = [{"파트명" :"MD",      "GRP_CD":"MD0004", "서버리스트" :["lpsisdb01", "lpsisdb02", "lpbakdb01", "lpdwsdb01",  "lpbatap01"
                                                                      ,"lpcfmap01", "lpeaiin01", "lpetlap01", "lpsisap01",  "lpsiswi01"
                                                                      ,"lpeaiex01", "lpediww01", "lpsiswo01", ]}
             , {"파트명" :"POS",     "GRP_CD":"PS0003", "서버리스트" :["lpscsdb01", "lppomap01", "lppomap02"]}
             , {"파트명" :"마케팅",   "GRP_CD":"MK0003", "서버리스트" :["cul-sqldb", "lpdlvdb01", "lpdlvdb02", "lpenr-sqlclt-t", "lpgms-sqldb"]}
             , {"파트명" :"상품권",   "GRP_CD":"GC0003", "서버리스트" :["lpgcsdb01"]}
             , {"파트명" :"경영지원", "GRP_CD":"HR0003", "서버리스트" :["ld-hrdb01",  "ld-hrdb02",  "ld-imdb1",     "lpea-sqldb",   "ld-hrap01"
                                                                      ,"ld-hrap02",  "ld-hrif",    "ld-hrinweb01", "ld-hrinweb02", "ldps"
                                                                      ,"ld-hrmob01", "ld-hrmob02", "ld-hrweb01",   "ld-hrweb02",]}
              ]

NETBACKUP_RSRC_LIST = ["B5150","B5250"]
B5150_TARGET_CNT = "60"
B5250_TARGET_CNT = "126"


def insert_netbackup_media_log(args):
    conn = monPC(func_nm())

    # row to column을 위해 pandas 활용
    df = pd.DataFrame(args, columns=["Field", "Value"])
    # dataframe에 모든항목의 Field와 Value 모두 공백 제거
    df["Field"] = df["Field"].apply(lambda x: x.strip())
    df["Value"] = df["Value"].apply(lambda x: x.strip())
    
    # Flag는 중복 제거를 방지하기 위해서 seq를 붙임
    df['count'] = df.groupby('Field').cumcount() + 1
    df['Field'] = df.apply(lambda row: row['Field'] + str(row['count']) if 'Flag' in row['Field'] else row['Field'], axis=1)

    # pivot으로 행와 열을 switch
    df = df.set_index("Field").T
    data = df.to_dict("records")[0]

    try: # 숫자는 %d, 문자는 %s를 사용
        sqlTxt = """
        MERGE dbo.TB_Bak_Media_Stat_L AS A
        USING (SELECT %s as Disk_Pool_Name, convert(varchar,getdate(),112) CollectDT
              ) AS B
           ON (A.CollectDT = B.CollectDT and A.Disk_Pool_Name = B.Disk_Pool_Name
              )
        WHEN NOT MATCHED THEN
            INSERT (  CollectDT, Disk_Pool_Name, Disk_Type, Disk_Volume_Name, Disk_Media_ID
                    , Total_Capacity_GB,  Free_Space_GB
                    , Use_Pct, Status,    Flag1, Flag2, Flag3
                    , Num_Read_Mounts,    Num_Write_Mounts
                    , Cur_Read_Streams,   Cur_Write_Streams
                    , Num_Repl_Sources,   Num_Repl_Targets
                    , WORM_Lock_Min_Time, WORM_Lock_Max_Time
                    , RGPR_ID,            RGST_DTM
                    ) VALUES
                    ( convert(varchar,getdate(),112), %s, %s, %s, %s
                    , %d, %d
                    , %d, %s, %s, %s, %s
                    , %d, %d
                    , %d, %d
                    , %d, %d
                    , %d, %d
                    , 'insert_netbackup_media_log', getdate()
                    )
        WHEN MATCHED THEN
            UPDATE SET    A.Disk_Type          = %s
                        , A.Disk_Volume_Name   = %s
                        , A.Disk_Media_ID      = %s
                        , A.Total_Capacity_GB  = %d
                        , A.Free_Space_GB      = %d
                        , A.Use_Pct            = %d
                        , A.Status             = %s
                        , A.Flag1              = %s
                        , A.Flag2              = %s
                        , A.Flag3              = %s
                        , A.Num_Read_Mounts    = %d
                        , A.Num_Write_Mounts   = %d
                        , A.Cur_Read_Streams   = %d
                        , A.Cur_Write_Streams  = %d
                        , A.Num_Repl_Sources   = %d
                        , A.Num_Repl_Targets   = %d
                        , A.WORM_Lock_Min_Time = %d
                        , A.WORM_Lock_Max_Time = %d
                        , A.MDFPR_ID       = 'update_netbackup_media_log'
                        , A.MDF_DTM         = getdate()
        ;
        """
        # CollectDT       = "convert(varchar,getdate(),112)"
        DiskPoolName    = get_string(data["Disk Pool Name"], "b")
        DiskType        = get_string(data["Disk Type"], "b")
        DiskVolumeName  = get_string(data["Disk Volume Name"], "b")
        DiskMediaID     = get_string(data["Disk Media ID"], "b")
        TotalCapacityGB = get_number(data["Total Capacity (GB)"], "b")
        FreeSpaceGB     = get_number(data["Free Space (GB)"], "b")
        UsePct          = get_number(data["Use%"], "b")
        Status          = get_string(data["Status"], "b")
        Flag1           = get_string(data["Flag1"], "b")
        Flag2           = get_string(data["Flag2"], "b")
        Flag3           = get_string(data["Flag3"], "b")
        NumReadMounts   = get_number(data["Num Read Mounts"], "b")
        NumWriteMounts  = get_number(data["Num Write Mounts"], "b")
        CurReadStreams  = get_number(data["Cur Read Streams"], "b")
        CurWriteStreams = get_number(data["Cur Write Streams"], "b")
        NumReplSources  = get_number(data["Num Repl Sources"], "b")
        NumReplTargets  = get_number(data["Num Repl Targets"], "b")
        WORMLockMinTime = get_number(data["WORM Lock Min Time"], "b")
        WORMLockMaxTime = get_number(data["WORM Lock Max Time"], "b")

        # RGPR_ID           = "insert_netbackup_media_log"
        # RGST_DTM          = "getdate()"
        # MDFPR_ID          = "update_netbackup_media_log"
        # MDF_DTM           = "getdate()"

        conn.execute(sqlTxt
                        ######## for select
                    ,(DiskPoolName
                        ########### for insert
                    , DiskPoolName, DiskType, DiskVolumeName, DiskMediaID
                    , TotalCapacityGB, FreeSpaceGB
                    , UsePct, Status,  Flag1, Flag2, Flag3
                    , NumReadMounts,   NumWriteMounts
                    , CurReadStreams,  CurWriteStreams
                    , NumReplSources,  NumReplTargets
                    , WORMLockMinTime, WORMLockMaxTime
                        ######### for update
                    , DiskType, DiskVolumeName, DiskMediaID
                    , TotalCapacityGB, FreeSpaceGB
                    , UsePct, Status,  Flag1, Flag2, Flag3
                    , NumReadMounts,   NumWriteMounts
                    , CurReadStreams,  CurWriteStreams
                    , NumReplSources,  NumReplTargets
                    , WORMLockMinTime, WORMLockMaxTime))

        # even MS-SQL need it (MUST)
        conn.commit()

        # 파일
        return 1

    except Exception as e:
        # print(func_nm() + ": " + str(e))
        msgr.put_msgr_target(func_tree() + ":\n" + str(e), grp_cd="DB9993", send_title="**" + func_nm() + "**", msgr_color="RED")
        # msgr.put_msgr_target(func_nm() + ": " + str(e), grp_cd="SE0001",send_title="daily_report_se_netbackup insert_srv_stat_log 오류", msgr_color="RED")
        return 0

    finally:
        sqlTxt = ""
        conn.close()

def send_netbackup_media_stat():
    conn = monPC(func_nm())
    content = ""
    alert_color = "GREEN"
    sqlTxt = """SELECT replace(Disk_Pool_Name,'dp_disk_','') + ' : ' + convert(varchar,Use_Pct) + '%' 
                     + ' (' + convert(varchar,ceiling((Total_Capacity_GB-Free_Space_GB)/1024))+ 'TB / ' 
                     + convert(varchar,ceiling(Total_Capacity_GB/1024)) + 'TB)' as content, Use_Pct
                  FROM [dbo].[TB_Bak_Media_Stat_L]
                 WHERE CollectDT = convert(varchar,getdate(),112)
             """
    try: # 숫자는 %d, 문자는 %s를 사용
        data = conn.query(sqlTxt)

        if conn.rows() > 0:
            results = [dict((conn.description()[i][0], value) 
                            for i, value in enumerate(row)) for row in data]
        
        for i, result in enumerate(results):
            # 임계치
            if (alert_color == "YELLOW" or alert_color == "GREEN") and int(result["Use_Pct"]) >= 95:
                alert_color = "RED"
                result["content"] = "[" + result["content"] + "]()" # [내용](공백)으로 잔디 링크 써서 강조 표시
            elif int(result["Use_Pct"]) >= 80:
                alert_color = "YELLOW"
                result["content"] = "[" + result["content"] + "]()" # [내용](공백)으로 잔디 링크 써서 강조 표시

            content = content + result["content"]
            if i == len(results) -1:
                continue
            else:
                content = content + "\n"

        msgr.put_msgr_target(content, "SE0001", send_title = "**Netbackup 미디어 상태**", msgr_color=alert_color)

    except Exception as e:
        # print(func_nm() + ": " + str(e))
        msgr.put_msgr_target(func_tree() + ":\n" + str(e), grp_cd="DB9993", send_title="**" + func_nm() + "**", msgr_color="RED")

    finally:
        conn.close()


def list_netbakcup_stat(args=None):
    conn = monPC(func_nm())
    sqlTxt = ""
    sqlTxt = """select Client, Status
                    , convert(varchar(16)
                    , max(Ended), 121) AS Ended 
                 from [dbo].[TB_Bak_Stat_Chk_L] 
                where started >= %s 
                group by Client, Status
            """
    try:
        # print(sqlTxt)
        data = conn.query(sqlTxt, NETBACKUP_YMD)

        if conn.rows() > 0:
            results = [dict((conn.description()[i][0], value) 
                            for i, value in enumerate(row)) for row in data]
        return results
    
    except Exception as e:
        # print(func_nm() + ": " + str(e))
        msgr.put_msgr_target(func_tree() + ":\n" + str(e), grp_cd="DB9993", send_title="**" + func_nm() + "**", msgr_color="RED")

    finally:
        conn.close()


def send_netbackup_stat(args, data):
    # netbackup은 주의(Yellow) 가 없는 형태로 작성되어 있음 (진행 중, 부분완료가 "주의"에 적합할 듯)
    # 정상(Green)과 심각(Red)만 존재하기 때문에 Status를 보고 
    # "정상"과 "심각"으로 바로 리스트 append 및 메시지 전송

    list_normal   = [] # 정상 완료 리스트
    list_critical = [] # 심각 상태 리스트

    try:
        # create_netbackup_alert_content & send_netbackup_stat 로 찢을 수 있음
        # 너무 잘게 찢는거 같아서 현상 유지
        for result in data:
            if result["Client"] in args["서버리스트"]:
                if result["Status"] == "0" or result["Status"] == "1":
                    list_normal.append({"title": result["Client"], "description": "완료 일시 : " + result["Ended"]})
                elif result["Status"] == "":
                    list_critical.append({"title": result["Client"], "description": "진행 중"})
                else:
                    list_critical.append({"title": result["Client"], "description": "상태 코드 : " + result["Status"]})

        # 정상 메시지 발송
        if list_normal:
            message_content = ""
            for i, message in enumerate(list_normal):
                message_content = message_content + "**" + message["title"] + "**" + "\n" + message["description"]
                if i == len(list_normal)-1 : # 마지막줄은 개행 추가 안함
                    continue
                else :
                    message_content = message_content + "\n\n"

            if args["파트명"] != "마케팅": # 마케팅 정상 메시지 제외 요청
                msgr.put_msgr_target(message_content, args["GRP_CD"], send_title = "**" + args["파트명"] + " Netbackup 정상**", msgr_color = "GREEN")

        # 심각 메시지 발송
        if list_critical:
            message_content = ""
            for i, message in enumerate(list_critical):
                message_content = message_content + "**" + message["title"] + "**" + "\n" + message["description"]
                if i == len(list_critical)-1 : # 마지막줄은 개행 추가 안함
                    continue
                else :
                    message_content = message_content + "\n\n"
            # 파티별 + SE       
            msgr.put_msgr_target(message_content, args["GRP_CD"], send_title = "**" + args["파트명"] + " Netbackup 확인필요**", msgr_color = "RED")
            msgr.put_msgr_target(message_content, "SE0001", send_title = "**Netbackup 확인 필요**", msgr_color = "RED")

    except Exception as e:
        # print(func_nm() + ": " + str(e))
        msgr.put_msgr_target(func_tree() + ":\n" + str(e), grp_cd="DB9993", send_title="**" + func_nm() + "**", msgr_color="RED")


# B5150     : 정상 상태 수
# B5250     : 정상 상태 수
def list_netbackup_resource():
    content = ""
    alert_color = "GREEN"

    for target in NETBACKUP_RSRC_LIST:
        full_path = NETBACKUP_PATH + "/" + target + TXT_EXT
        file_exists_check = check_file(full_path) 
        
        if file_exists_check == "Y":
            with open(full_path, "r") as lines:
            
                for i, line in enumerate(lines):
                    line = line.strip()

                    if target == "B5150":
                        if line.strip() != B5150_TARGET_CNT:
                            alert_color = "RED"
                            content = content + "B5150 하드웨어 상태 : " + "[" + line + " / " + B5150_TARGET_CNT + "]()\n" # [내용](공백)으로 잔디 링크 써서 강조 표시
                        else : 
                            content = content + "B5150 하드웨어 상태 : " + line + " / " + B5150_TARGET_CNT + "\n"
                    
                    elif target == "B5250":
                        if line.strip() != B5250_TARGET_CNT:
                            alert_color = "RED"
                            content = content + "B5250 하드웨어 상태 : " + "[" + line + " / " + B5250_TARGET_CNT + "]()\n" # [내용](공백)으로 잔디 링크 써서 강조 표시
                        else : 
                            content = content + "B5250 하드웨어 상태 : " + line + " / " + B5250_TARGET_CNT + "\n"

            os.rename(full_path, OLD_PATH + "/" + NETBACKUP_YMD + "_" + target + TXT_EXT) # with open sytanx include close at the end of loop

        else:
            msgr.put_msgr_target("not exist file : " + full_path, "DB9993", send_title = "list_netbackup_resource err", msgr_color = "RED")
    
    msgr.put_msgr_target(content, "SE0001", send_title = "**Netbackup 미디어 하드웨어 상태**", msgr_color = alert_color)

def read_log():
    # 파일 리스트 호출
    f_list = os.listdir(NETBACKUP_PATH)

    # 파일 호출
    for f in f_list:
        if f.startswith(YMD) and f.endswith(".log"):
            file_open = open(NETBACKUP_PATH + "/" + f, "r")
            lines = file_open.readlines()
            data   = []

            if   "media.log" in f:
                for line in lines:
                    if line == "\n":
                        continue
                    data.append(line.strip().split(":"))
                success_Flag = insert_netbackup_media_log(data)
                
            else : # B5150, B5250 파일은 *.txt로 떨어지기 때문에 *.log에서 애초에 걸러짐
                msgr.put_msgr_target("file name is inaccurate: " + f, "DB9993", send_title="**" + func_nm() + "**", msgr_color = "RED")
                # msgr.put_msgr_target("file name is inaccurate: " + f, grp_cd="SE0001",send_title="daily_report_se_netbackup read_log 오류", msgr_color="RED")
                success_Flag = 0
                    

            file_open.close()

            # for temporary comments
            if success_Flag:
                os.rename(NETBACKUP_PATH + "/" + f, OLD_PATH + "/" + f)
                # print("success")

            else : 
                os.rename(NETBACKUP_PATH + "/" + f, ERR_PATH + "/" + f) # to file move to err
                # print("fail")
                msgr.put_msgr_target("daily_report_se_netbackup read_log() file name task is failed : " + f, "DB9993", send_title="**" + func_nm() + "**", msgr_color = "RED")


# MAIN
if __name__=="__main__":

    data = list_netbakcup_stat() # DB에서 데이터는 1회만 조회
    
    # 파트별 넷백업 상태 전송
    for target in TARGET_LIST: # Loop 돌면서 파트별 일치하는 서버 찾아서 list 생성 및 메시지 전송
        send_netbackup_stat(target, data)

    # 넷백업 미디어 체크
    read_log()
    send_netbackup_media_stat()

    # 하드웨어 정상 카운트
    list_netbackup_resource()  # B5150, B5250 