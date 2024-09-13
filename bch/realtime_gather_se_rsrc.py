import os

# common & configuration
from cfg.config_path import SE_LOG_PATH as LOG_HOME
import cmn.common_sql as sql
import cmn.common_msgr as msgr
from cmn.common import get_cur_func_nm as func_nm, get_cur_file_nm as file_nm, get_func_tree as func_tree
from cmn.common_db import monPC

# file path
ERR_PATH            = LOG_HOME + 'err'
OLD_PATH            = LOG_HOME + 'old'
TARGET_PATH         = LOG_HOME 


def insert_srv_rsrc_log(args):
    conn = monPC(func_nm())

    try:
        sqlTxt = "insert into dbo.TB_Svr_Rsrc_Chk_L (hostName, CollectDT, CollectHH, CollectMS, cpuUse, memUse, dskChk, RGPR_ID, RGST_DTM) values " + '\n'

        # list to list
        for i, data_list in enumerate(args): # for putting comma logic, enumerate is necessary
            # value transform to fit on insert syntax
            hostName  = data_list[0]
            CollectDT = data_list[1][0:8]
            CollectHH = data_list[1][8:10]
            CollectMS = data_list[1][10:14]
            cpuUse    = data_list[2]
            memUse    = data_list[3]
            dskChk    = data_list[4]
            RGPR_ID   = 'insert_srv_rsrc_log'
            RGST_DTM  = 'getdate()'
            
            # set bulk data query
            listToStr = '(' + \
                              sql.get_string(hostName,  'l')  + \
                        ',' + sql.get_string(CollectDT, 'l')  + \
                        ',' + sql.get_string(CollectHH, 'l')  + \
                        ',' + sql.get_string(CollectMS, 'l')  + \
                        ',' +               cpuUse           + \
                        ',' +               memUse           + \
                        ',' +               dskChk           + \
                        ',' + sql.get_string(RGPR_ID,   'l')  + \
                        ',' +               RGST_DTM         + \
                        ')'

            # except last one, put comma and new line char
            if i < len(args)-1 :
                listToStr = listToStr + ',\n' 
            sqlTxt = sqlTxt  + listToStr

        # try:
        # print(sqlTxt)
        conn.execute(sqlTxt)

        # even MS-SQL need it (MUST)
        conn.commit()
        return 1

    except Exception as e:
        # print(func_nm() + ": " + str(e))
        msgr.put_msgr_target(func_tree() + ":\n" + str(e), grp_cd="DB9993", send_title="**" + func_nm() + "**", msgr_color="RED")
        msgr.put_msgr_target(func_tree() + ": " + str(e), grp_cd="SE0001",send_title="**" + func_nm() + "**", msgr_color="RED")
        return 0

    finally:
        sqlTxt = ""
        conn.close()


def insert_srv_fs_log(args):
    conn = monPC(func_nm())
    
    try:

        sqlTxt = "insert into dbo.TB_Svr_Fs_Chk_L (hostName, CollectDT, CollectHH, CollectMS, path_name, use_pct, RGPR_ID, RGST_DTM) values " + '\n'

        # list to list
        for i, data_list in enumerate(args): # for putting comma logic, enumerate is necessary

            # value transform to fit on insert syntax
            hostName  = data_list[0]
            CollectDT = data_list[1][0:8]
            CollectHH = data_list[1][8:10]
            CollectMS = data_list[1][10:14]
            path_name = data_list[2]
            use_pct   = data_list[3]
            RGPR_ID   = 'insert_srv_fs_log'
            RGST_DTM  = 'getdate()'
            
            # set bulk data query
            listToStr = '(' + \
                              sql.get_string(hostName,  'l')  + \
                        ',' + sql.get_string(CollectDT, 'l')  + \
                        ',' + sql.get_string(CollectHH, 'l')  + \
                        ',' + sql.get_string(CollectMS, 'l')  + \
                        ',' + sql.get_string(path_name, 'l')  + \
                        ',' +               use_pct          + \
                        ',' + sql.get_string(RGPR_ID,   'l')  + \
                        ',' +               RGST_DTM         + \
                        ')'

            # except last one, put comma and new line char
            if i < len(args)-1 :
                listToStr = listToStr + ',\n' 
            sqlTxt = sqlTxt  + listToStr

        # print(sqlTxt)
        conn.execute(sqlTxt)

        # even MS-SQL need it (MUST)
        conn.commit()
        return 1

    except Exception as e:
        # print(func_nm() + ": " + str(e))
        msgr.put_msgr_target(func_tree() + ":\n" + str(e), grp_cd="DB9993", send_title="**" + func_nm() + "**", msgr_color="RED")
        msgr.put_msgr_target(func_tree() + ": " + str(e), grp_cd="SE0001",send_title="**" + func_nm() + "**", msgr_color="RED")
        return 0

    finally:
        sqlTxt = ""
        conn.close()


def insert_srv_stat_log(args, collect_ymd):
    conn = monPC(func_nm())
    
    try:
        sqlTxt = "insert into dbo.TB_Svr_Stat_Chk_L (hostName, CollectDT, CollectHH, CollectMS, statusName, status, RGPR_ID, RGST_DTM) values " + '\n'

        splited_args = [[item[0].split(':')[0].strip(), item[0].split(':')[1].strip()] \
                          for item in args]

        # Row to Column
        # Server Status table format is permenent 
        # and shell script is being managed by SE
        hostName  = ''
        CollectDT = collect_ymd[0:8]
        CollectHH = collect_ymd[8:10]
        CollectMS = collect_ymd[10:14]
        STAT_NM  = ''
        STAT     = ''
        RGPR_ID   = 'insert_srv_stat_log'
        RGST_DTM  = 'getdate()'

        listToStr = ""
        for i, data_list in enumerate(splited_args): # for putting comma logic, enumerate is necessary

            # value transform to fit on insert syntax
            if data_list[0] == 'hostname' :
                hostName = data_list[1]
                continue
            else :
                STAT_NM = data_list[0]
                STAT    = data_list[1]
                # continue

        # set bulk data query
            listToStr = listToStr + '(' + \
                                sql.get_string(hostName,  'l')  + \
                            ',' + sql.get_string(CollectDT, 'l')  + \
                            ',' + sql.get_string(CollectHH, 'l')  + \
                            ',' + sql.get_string(CollectMS, 'l')  + \
                            ',' + sql.get_string(STAT_NM,   'l')  + \
                            ',' + sql.get_string(STAT,      'l')  + \
                            ',' + sql.get_string(RGPR_ID,   'l')  + \
                            ',' +               RGST_DTM         + \
                        ')'
            if i == len(splited_args)-1:
                continue
            else:
                listToStr = listToStr + ',' + '\n'

        # except last one, put comma and new line char
        # THIS IS NOT FOR THIS DEF (this is supposed to be in for loop)
        # if i < len(args)-1 :
        #     listToStr = listToStr + ',\n' 
        sqlTxt = sqlTxt  + listToStr

        # print(sqlTxt)
        conn.execute(sqlTxt)

        # even MS-SQL need it (MUST)
        conn.commit()
        return 1

    except Exception as e:
        # print(func_nm() + ": " + str(e))
        msgr.put_msgr_target(func_tree() + ":\n" + str(e), grp_cd="DB9993", send_title="**" + func_nm() + "**", msgr_color="RED")
        msgr.put_msgr_target(func_tree() + ": " + str(e), grp_cd="SE0001",send_title="**" + func_nm() + "**", msgr_color="RED")
        return 0

    finally:
        sqlTxt = ""
        conn.close()


def insert_bak_stat_log(args, collect_ymd):
    conn = monPC(func_nm())

    try:
        sqlTxt = """
        MERGE dbo.TB_Bak_Stat_Chk_L AS A
        USING (SELECT %d as JobID, %s as CollectDT, %s as Status
                ) AS B
        ON (    A.JobID     = B.JobID
            )
        WHEN NOT MATCHED THEN
            INSERT (JobID,         Type,           State,          Status,       Policy,     Schedule
                    , Client,        Dest_Media_Svr, Started,        Ended,        Elapsed
                    , Kilobytes,     KB_Per_Sec,     Active_Elapsed, Active_PID,   Attempt
                    , Backup_Type,   Completion,     Compression,    Dedupe_Ratio, Dest_StUnit
                    , [Group],       Owner,          Parent_JobID,   Policy_Type,  Retention
                    , Schedule_Type, CollectDT,      RGPR_ID,        RGST_DTM
                    ) VALUES
                    ( %d, %s, %s, %s, %s, %s
                    , %s, %s, %s, %s, %d
                    , %d, %d, %d, %d, %d
                    , %s, %d, %s, %d, %s
                    , %s, %s, %d, %s, %s
                    , %s, %s, 'insert_bak_stat_log', getdate()
                    )
        WHEN MATCHED AND A.Status <> B.status THEN
            UPDATE SET    A.Type           = %s
                        , A.State          = %s
                        , A.Status         = %s
                        , A.Schedule       = %s
                        , A.Client         = %s
                        , A.Dest_Media_Svr = %s
                        , A.Ended          = %s
                        , A.Elapsed        = %d
                        , A.Kilobytes      = %d
                        , A.KB_Per_Sec     = %d
                        , A.Active_Elapsed = %d
                        , A.Active_PID     = %d
                        , A.Attempt        = %d
                        , A.Backup_Type    = %s
                        , A.Completion     = %d
                        , A.Compression    = %s
                        , A.Dedupe_Ratio   = %d
                        , A.Dest_StUnit    = %s
                        , A.[Group]        = %s
                        , A.Owner          = %s
                        , A.Parent_JobID   = %d
                        , A.Policy_Type    = %s
                        , A.Retention      = %s
                        , A.Schedule_Type  = %s
                        , A.MDFPR_ID       = 'update_bak_stat_log'
                        , A.MDF_DTM         = getdate()
        ;
        """
        # list to list
        # for putting comma logic, enumerate is necessary
        for i, data_list in enumerate(args):
            CollectDT         = collect_ymd[0:8]
            # value transform to fit on insert syntax
            JobID             = sql.get_number(data_list[0], 'b')
            Type              = data_list[1]
            State             = data_list[2]
            Status            = data_list[3]
            Policy            = data_list[4]
            Schedule          = data_list[5]
            Client            = data_list[6]
            Dest_Media_Svr    = data_list[7]
            Started           = sql.get_datetime(data_list[8], 'b')
            Ended             = sql.get_datetime(data_list[9], 'b')
            Elapsed           = sql.get_elapsed_sec(data_list[10])
            Kilobytes         = sql.get_number(data_list[11], 'b')
            KB_Per_Sec        = sql.get_number(data_list[12], 'b')
            Active_Elapsed    = sql.get_elapsed_sec(data_list[13])
            Active_PID        = sql.get_number(data_list[14], 'b')
            Attempt           = sql.get_number(data_list[15], 'b')
            Backup_Type       = data_list[16]
            Completion        = sql.get_number(data_list[17], 'b')
            Compression       = data_list[18]
            Dedupe_Ratio      = sql.get_number(data_list[19], 'b')
            Dest_StUnit       = data_list[20]
            Group             = data_list[21]
            Owner             = data_list[22]
            Parent_JobID      = sql.get_number(data_list[23], 'b')
            Policy_Type       = data_list[24]
            Retention         = data_list[25]
            Schedule_Type     = data_list[26]
            RGPR_ID           = 'insert_bak_stat_log'
            RGST_DTM          = 'getdate()'
            
            conn.execute(sqlTxt
                           ######## for select
                       , (JobID, CollectDT, Status
                           ########### for insert
                       , JobID,         Type,           State,          Status,       Policy,     Schedule
                       , Client,        Dest_Media_Svr, Started,        Ended,        Elapsed
                       , Kilobytes,     KB_Per_Sec,     Active_Elapsed, Active_PID,   Attempt
                       , Backup_Type,   Completion,     Compression,    Dedupe_Ratio, Dest_StUnit
                       , Group,         Owner,          Parent_JobID,   Policy_Type,  Retention
                       , Schedule_Type, CollectDT
                           ######### for update
                       , Type, State, Status, Schedule, Client
                       , Dest_Media_Svr, Ended, Elapsed, Kilobytes, KB_Per_Sec
                       , Active_Elapsed, Active_PID, Attempt, Backup_Type, Completion
                       , Compression, Dedupe_Ratio, Dest_StUnit, Group, Owner
                       , Parent_JobID, Policy_Type, Retention, Schedule_Type))

        # try:
        # even MS-SQL need it (MUST)
        conn.commit()
        return 1

    except Exception as e:
        # print(func_nm() + ": " + str(e))
        msgr.put_msgr_target(str(e), grp_cd="DB9993", send_title="**" + func_nm() + "**", msgr_color="RED")
        msgr.put_msgr_target(func_nm() + ": " + str(e), grp_cd="SE0001",send_title="**" + func_nm() + "**", msgr_color="RED")
        return 0

    finally:
        sqlTxt = ""
        conn.close()


def read_log():
    # 파일 리스트 호출
    f_list = os.listdir(TARGET_PATH)
    
    # only when it needs to exec MANUALLY
    # nomally REMARKED
    # ymdHH = input("YYYYMMDDHH24를 입력하세요 :")

    # 파일 호출
    for f in f_list:
        if f.endswith(".log"): # f.startswith(ymd) and 
            hostname  = f.split('.')[0][15:]
            file_open = open(TARGET_PATH + '/' + f, 'r')
        
            lines = file_open.readlines()

            header = []
            data   = []
        
            if 'netbackup.log' in f:
                for i, line in enumerate(lines):
                    small_dataset = []
                    if i == 0:
                        for i in range(0, len(line)-1, 30):
                            header.append(str(line[i : i + 30]).rstrip().lstrip().replace(' ','_'))
                    
                    else :
                        for i in range(0, len(line)-1, 30):
                                small_dataset.append(str(line[i : i + 30]).rstrip().lstrip())
                        data.append(small_dataset)
                        
                success_Flag = insert_bak_stat_log(data, f[0:14])
            

            else:
                for line in lines:
                    data.append(line.strip().split(','))

                if   'rsrc.log' in f:
                    success_Flag = insert_srv_rsrc_log(data)
                elif 'fs.log'   in f:
                    success_Flag = insert_srv_fs_log(data)

                # below conditions are for checking core hardware and os status
                elif 'esxi.log'  in f:
                    success_Flag = insert_srv_stat_log(data, f[0:14])
                elif 'rmc.log'  in f:
                    success_Flag = insert_srv_stat_log(data, f[0:14])
                elif 'hmc.log'  in f:
                    success_Flag = insert_srv_stat_log(data, f[0:14])
                elif 'aix.log'  in f:
                    success_Flag = insert_srv_stat_log(data, f[0:14])
                elif 'rhel.log' in f:
                    success_Flag = insert_srv_stat_log(data, f[0:14])

                # to file move to err
                else :
                    msgr.put_msgr_target("file name is inaccurate: " + f, grp_cd="DB9993", send_title="**" + func_nm() + "**", msgr_color="RED")
                    msgr.put_msgr_target("file name is inaccurate: " + f, grp_cd="SE0001", send_title="**" + func_nm() + "**", msgr_color="RED")
                    success_Flag = 0
                    
                # continue

            file_open.close()

            ## for temporary comments
            if success_Flag:
                os.rename(TARGET_PATH + '/' + f, OLD_PATH + '/' + f)
                # print("success")
            else : 
                os.rename(TARGET_PATH + '/' + f, ERR_PATH + '/' + f)
                # print("fail")
                msgr.put_msgr_target("file name task is failed : " + f, grp_cd="DB9993", send_title="**" + func_nm() + "**", msgr_color="RED")
                msgr.put_msgr_target("file name task is failed : " + f, grp_cd="SE0001", send_title="**" + func_nm() + "**", msgr_color="RED")


if __name__ == "__main__":
    read_log()