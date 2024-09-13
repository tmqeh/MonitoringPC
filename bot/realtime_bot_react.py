import requests
import re
import datetime # NOW reload 목적
import unicodedata # help 자간 조정 목적

# import cfg.config as cnf
from cfg.config_path import IMG_EXT, IMG_COMMON_DIR
from cfg.config_msgr import SLACK_TOKEN
from cfg.config_bot import MAPPING_PARAM, SERVERHOSTS
from cfg.config_grafana import DASHBOARD_LIST
import cmn.common_msgr as msgr
from cmn.common_db import monDB, monPC, maxgDB
from cmn.common_datetime import YMD

"""
타겟 function이랑 title 매치하고 실행하는데
send_img 경우는 channel이랑 url을 넘겨줘야되고

sql같은경우는 대상을 넘겨줘야됨
근태의 경우 사람이름이나 파트명
DB의 경우 DB명이나 기간
"""


def common_send_img(target, **args):
    # *arg는 배열형태라 args[0] 이런식으로 관리해야됨 
    # => 각 배열의 역할을 알기 어려움
    # **args는 dict 형태라 key만 지정해주면 원하는데로 가져올 수 있음

    print("=======================================================")
    print(target['title'])
    print(target['url'])
    print(args)
    print("=======================================================")

    # for key, value in args.items():
    #     print(key)
    #     print(value)

    # file_name = YMD + HMS +"_" + target['title'].replace(" ","-") + IMG_EXT
    # 동일 파일 overwrite 이슈 수정
    file_name = datetime.datetime.now().strftime("%Y%m%d%H%M%S") +"_" + target['title'].replace(" ","-") + IMG_EXT
    file_full_path = IMG_COMMON_DIR + file_name
    
    # File DownLoad
    # send_slack_image 와 충돌나서 requests로 대체
    # curl_cmd ='curl --connect-timeout 600 -H ' + ' "Authorization: Bearer ' + target['api'] + '" "' + target['url'] \
    #         + '&width=' + target['width'] + '&height=' + target['height'] \
    #         + '" > "' + file_full_path  + '"'
    
    option_param = ''
    if 'opt_param' in args:
        option_param = ''.join(args['opt_param'])
    target_channel=''
    if 'target_channel' in args:
        target_channel = ''.join(args['target_channel'])

    # print("=======================================================")
    # print("option_param : " + option_param)
    # print("target_channel : " + target_channel)
    # print("=======================================================")

    url = target['url'] + option_param + '&width=' + target['width'] + '&height=' + target['height'] 
    print(url)
    header={'Authorization':'Bearer ' + target['api']}
    # print(url)

    # File DownLoad NEW
    response = requests.get(url, stream=True, headers=header)
    with open(file_full_path, 'wb') as download:
        download.write(response.content)
        msgr.put_msgr_target(target['title'], grp_cd=None, chnl_nm=target_channel, token_val=SLACK_TOKEN, img_file_path=file_full_path)


def fill_str_with_space(input_s="", max_size=40, fill_char=" "): # help indent formmating
    """
    - 길이가 긴 문자는 2칸으로 체크하고, 짧으면 1칸으로 체크함. 
    - 최대 길이(max_size)는 40이며, input_s의 실제 길이가 이보다 짧으면 
    남은 문자를 fill_char로 채운다.
    """
    l = 0 
    for c in input_s:
        if unicodedata.east_asian_width(c) in ['F', 'W']:
            l+=2
        else: 
            l+=1
    return input_s+fill_char*(max_size-l)

def daily_check_mssql(target, channel):
    common_send_img(target, target_channel=channel)

def daily_check_oracle(target, channel):
    common_send_img(target, target_channel=channel)

def daily_check_etc_oracle(target, channel):
    common_send_img(target , target_channel=channel)

def daily_check_etc_oracle_storage(target , channel):
    common_send_img(target , target_channel=channel)

def daily_check_etc_batch(target , channel):
    common_send_img(target , target_channel=channel)

def daily_check_etc_sync(target , channel):
    common_send_img(target , target_channel=channel)

def daily_check_etc_dr(target , channel):
    common_send_img(target , target_channel=channel)

def daily_check_etc_bcv(target , channel):
    common_send_img(target , target_channel=channel)

def daily_check_netbackup(target , channel):
    common_send_img(target , target_channel=channel)

def work(target , channel):
    common_send_img(target , target_channel=channel)

def work_part(target, requested_opt, channel):
    common_send_img(target, opt_param=requested_opt, target_channel=channel)

def work_indivisual(target, requested_opt, channel):
    common_send_img(target, opt_param=requested_opt, target_channel=channel)

def realtime_mssql_cpu_resource (target, requested_opt, channel):
    common_send_img(target, opt_param=requested_opt, target_channel=channel)

def realtime_mssql_memory_resource (target, requested_opt, channel):
    common_send_img(target, opt_param=requested_opt, target_channel=channel)

def realtime_mssql_request_resource (target, requested_opt, channel):
    common_send_img(target, opt_param=requested_opt, target_channel=channel)

def realtime_mssql_transaction_resource (target, requested_opt, channel):
    common_send_img(target, opt_param=requested_opt, target_channel=channel)

def realtime_mssql_bufferhit_resource (target, requested_opt, channel):
    common_send_img(target, opt_param=requested_opt, target_channel=channel)

def realtime_mssql_storage_resource (target, requested_opt, channel):
    common_send_img(target, opt_param=requested_opt, target_channel=channel)

def realtime_oracle_cpu_resource (target, requested_opt, channel):
    common_send_img(target, opt_param=requested_opt, target_channel=channel)

def realtime_oracle_memory_resource (target, requested_opt, channel):
    common_send_img(target, opt_param=requested_opt, target_channel=channel)

def realtime_oracle_execution_resource (target, requested_opt, channel):
    common_send_img(target, opt_param=requested_opt, target_channel=channel)

def realtime_oracle_session_resource (target, requested_opt, channel):
    common_send_img(target, opt_param=requested_opt, target_channel=channel)

def daily_check_etc_oracle_detail(target , channel):
    conn = monDB()
    content="\n"
    sql_text = """ select A.[ServerName] 
                        , A.[IPAddr] 
                        , A.[hostName] 
                        , B.[path_name]   
                        , B.[use_pct]   
                        , B.[CollectDT]
                     from [dbo].[TB_Svr_Comm_Info_M] A left outer join [dbo].[TB_Svr_Fs_Chk_L] B
                       on A.[hostName] = B.[hostName]
                    where B.CollectDT = convert(varchar, getdate(), 112)
                      and A.UseYn = 'Y'
                      and use_pct > 95
                    order by use_pct desc, A.hostName """

    data = conn.query(sql_text)
    result = []
    if conn.rows() > 0:
            result = [dict((conn.description()[i][0], value) \
                            for i, value in enumerate(row)) for row in data]
    conn.close()
    
    if result :
        for sms_txt in result :
            content = content + '일자 : ' + sms_txt['CollectDT'] + '\n'
            content = content + '서버 : ' + sms_txt['hostName'] + '(' + sms_txt['IPAddr'] + ')' + '\n'
            content = content + '내용 : ' + sms_txt['path_name'] + ' ' + str(sms_txt['use_pct'])
            
            # print(content)
            msgr.put_msgr_target(content, grp_cd=None, chnl_nm=channel, token_val=SLACK_TOKEN)
            content="\n"

    else :
        msgr.put_msgr_target("조회결과가 없습니다.", grp_cd=None, chnl_nm=channel, token_val=SLACK_TOKEN)

    common_send_img(target , target_channel=channel)


def daily_check_mssql_detail_err(target , channel):
    conn = monDB()
    content="\n"
    sql_text = """ EXEC [dbo].[usp_ShowAgentJob_Detail] """

    data = conn.query(sql_text)
    result = []
    if conn.rows() > 0:
            result = [dict((conn.description()[i][0], value) \
                            for i, value in enumerate(row)) for row in data]

    if result :
        for sms_txt in result :
            content = content + '일시 : ' + sms_txt['LastRunDateTime'].strftime("%Y-%m-%d %H:%M:%S") + '\n'
            content = content + '서버 : ' + sms_txt['ServerName'] + '\n'
            content = content + '내용 : ' + sms_txt['JobName'] + '\n' + sms_txt['LastRunStatusMessage']
            
            # print(content)
            msgr.put_msgr_target(content, grp_cd=None, chnl_nm=channel, token_val=SLACK_TOKEN)
            content="\n"

    else :
        msgr.put_msgr_target("잡 오류 조회결과가 없습니다.", grp_cd=None, chnl_nm=channel, token_val=SLACK_TOKEN)
    
    sql_text2 = """ EXEC [dbo].[usp_ShowErrorLog_Detail] """
    
    data2 = conn.query(sql_text2)
    result2 = []
    if conn.rows() > 0:
            result2 = [dict((conn.description()[i][0], value) \
                            for i, value in enumerate(row)) for row in data2]

    if result2 :
        for sms_txt in result2 :
            content = content + '일시 : ' + sms_txt['LOG_DATE'].strftime("%Y-%m-%d %H:%M:%S") + '\n'
            content = content + '서버 : ' + sms_txt['ServerName'] + '\n'
            content = content + '내용 : ' + sms_txt['PROCESS_INFO'] + '\n' + sms_txt['ERRORLOG_TEXT'] 
            
            # print(content)
            msgr.put_msgr_target(content, grp_cd=None, chnl_nm=channel, token_val=SLACK_TOKEN)
            content="\n"

    else :
        msgr.put_msgr_target("DB 오류 조회결과가 없습니다.", grp_cd=None, chnl_nm=channel, token_val=SLACK_TOKEN)

    conn.close()


def daily_check_mssql_detail_storage(target , channel):
    common_send_img(target , target_channel=channel)


def daily_check_oracle_detail_err(target , channel):
    conn = maxgDB()
    content="\n"
    sql_text = """ SELECT time, 'LPSIS1' as inst_id, value as err_detail
                     FROM LPSIS1.ORA_ALERTLOG_HISTORY Z                                                                                    
                    WHERE TIME >= CURRENT_DATE -1                                                                                                       
                      AND VALUE NOT LIKE '%KILL SESSION%'                                                                                               
                      AND VALUE NOT LIKE '%aborting process unknown ospid%'                                                                      
                      AND VALUE NOT LIKE '%ORA-01013%'   
                      AND VALUE NOT LIKE '%SQL Analyze time limit interrupt%'
                   union all
                   SELECT time, 'LPSIS2' inst_id, value
                     FROM LPSIS2.ORA_ALERTLOG_HISTORY Z                                                                                    
                    WHERE TIME >= CURRENT_DATE -1                                                                                                       
                      AND VALUE NOT LIKE '%KILL SESSION%'                                                                                               
                      AND VALUE NOT LIKE '%aborting process unknown ospid%'                                                                      
                      AND VALUE NOT LIKE '%ORA-01013%'
                      AND VALUE NOT LIKE '%SQL Analyze time limit interrupt%'
                   union all
                   SELECT time, 'LOTTEHRS1' as inst_id, value as err_detail
                     FROM LOTTEHRS1.ORA_ALERTLOG_HISTORY Z                                                                                    
                    WHERE TIME >= CURRENT_DATE -1                                                                                                       
                      AND VALUE NOT LIKE '%KILL SESSION%'                                                                                               
                      AND VALUE NOT LIKE '%aborting process unknown ospid%'                                                                      
                      AND VALUE NOT LIKE '%ORA-01013%'   
                      AND VALUE NOT LIKE '%SQL Analyze time limit interrupt%'
                   union all
                   SELECT time, 'LOTTEHRS2' inst_id, value
                     FROM LOTTEHRS2.ORA_ALERTLOG_HISTORY Z                                                                                    
                    WHERE TIME >= CURRENT_DATE -1                                                                                                       
                      AND VALUE NOT LIKE '%KILL SESSION%'                                                                                               
                      AND VALUE NOT LIKE '%aborting process unknown ospid%'                                                                      
                      AND VALUE NOT LIKE '%ORA-01013%'   
                      AND VALUE NOT LIKE '%SQL Analyze time limit interrupt%' """

    data = conn.query(sql_text)
    result = []
    if conn.rows() > 0:
            result = [dict((conn.description()[i][0], value) \
                            for i, value in enumerate(row)) for row in data]
    conn.close()
    

    if result :
        for sms_txt in result :
            content = content + '일시 : ' + sms_txt['time'].strftime("%Y-%m-%d %H:%M:%S") + '\n'
            content = content + '서버 : ' + sms_txt['inst_id'] + '\n'
            content = content + '내용 : ' + sms_txt['err_detail']

            # print(content)
            msgr.put_msgr_target(content, grp_cd=None, chnl_nm=channel, token_val=SLACK_TOKEN)
            content="\n"

    else :
        msgr.put_msgr_target("조회결과가 없습니다.", grp_cd=None, chnl_nm=channel, token_val=SLACK_TOKEN)


def daily_check_oracle_detail_storage(target , channel):
    conn = maxgDB()
    content="\n"
    sql_text = """ SELECT INST_ID, TABLESPACE_NAME, TOTAL_SPACE, USED_SPACE, FREE_SPACE, USE_PRCT
                     FROM (
                         SELECT 'LPSISAL' INST_ID, 
                                 TABLESPACE_NAME,  
                                 ROUND(SUM(TOTAL_SPACE)/1024.0,2) TOTAL_SPACE,
                                 ROUND((SUM(TOTAL_SPACE) - SUM(FREE_SPACE) )  /1024.0,2) AS USED_SPACE,   
                                 ROUND(SUM(FREE_SPACE)/1024.0,2) AS FREE_SPACE,
                                 ROUND(COALESCE(      
                                 ROUND((SUM(TOTAL_SPACE)/1024.0 - SUM(FREE_SPACE)/1024.0),2) / CASE WHEN ROUND(SUM(TOTAL_SPACE)/1024.0,2) = 0 THEN NULL 
                                                                                                     ELSE ROUND(SUM(TOTAL_SPACE)/1024.0,2)
                                                                                                 END, 0) * 100,2) AS USE_PRCT,
                                 DATE_TRUNC('day', A.TIME ) AS TIME
                             FROM LPSIS1.ORA_TABLESPACE_INFO A, (SELECT MAX(TIME) AS MAX_TIME, MAX(PARTITION_KEY) AS PARTITION_KEY
                                                                 FROM LPSIS1.ORA_TABLESPACE_INFO) B
                         WHERE TIME = B.MAX_TIME
                             AND A.PARTITION_KEY = B.PARTITION_KEY
                             AND TABLESPACE_NAME NOT LIKE '%UNDO%'
                             AND TABLESPACE_NAME NOT LIKE '%TEMP%'
                         GROUP BY TABLESPACE_NAME, DATE_TRUNC('day', A.TIME)
                     UNION ALL
                         SELECT 'LOTTEHRS' INST_ID, 
                                 TABLESPACE_NAME,  
                                 ROUND(SUM(TOTAL_SPACE)/1024.0,2) TOTAL_SPACE,
                                 ROUND((SUM(TOTAL_SPACE) - SUM(FREE_SPACE) )  /1024.0,2) AS USED_SPACE,   
                                 ROUND(SUM(FREE_SPACE)/1024.0,2) AS FREE_SPACE,
                                 ROUND(COALESCE(      
                                 ROUND((SUM(TOTAL_SPACE)/1024.0 - SUM(FREE_SPACE)/1024.0),2) / CASE WHEN ROUND(SUM(TOTAL_SPACE)/1024.0,2) = 0 THEN NULL 
                                                                                                     ELSE ROUND(SUM(TOTAL_SPACE)/1024.0,2)
                                                                                                 END, 0) * 100,2) AS USE_PRCT,
                                 DATE_TRUNC('day', A.TIME ) AS TIME
                             FROM LOTTEHRS1.ORA_TABLESPACE_INFO A, (SELECT MAX(TIME) AS MAX_TIME, MAX(PARTITION_KEY) AS PARTITION_KEY
                                                                 FROM LOTTEHRS1.ORA_TABLESPACE_INFO) B
                         WHERE TIME = B.MAX_TIME
                             AND A.PARTITION_KEY = B.PARTITION_KEY
                             AND TABLESPACE_NAME NOT LIKE '%UNDO%'
                             AND TABLESPACE_NAME NOT LIKE '%TEMP%'
                         GROUP BY TABLESPACE_NAME, DATE_TRUNC('day', A.TIME)
                     ORDER BY USE_PRCT DESC
                     ) AS TBS_CHK WHERE USE_PRCT > 95 """
    
    data = conn.query(sql_text)
    result = []
    if conn.rows() > 0:
            result = [dict((conn.description()[i][0], value) \
                            for i, value in enumerate(row)) for row in data]
    conn.close()

    if result :
        for sms_txt in result :
            content = content + '일시 : ' + YMD + '\n'
            content = content + '서버 : ' + sms_txt['inst_id'] + '\n'
            content = content + '내용 : ' + sms_txt['tablespace_name'] + ': ' + str(sms_txt['use_prct'])

            # print(content)
            msgr.put_msgr_target(content, grp_cd=None, chnl_nm=channel, token_val=SLACK_TOKEN)
            content="\n"

    else :
        msgr.put_msgr_target("조회결과가 없습니다.", grp_cd=None, chnl_nm=channel, token_val=SLACK_TOKEN)

    common_send_img(target , target_channel=channel)


def daily_check_detail_rds_err(target, ServerHost, channel) :
    conn = monPC()
    content="\n"
    sql_text = """ SELECT ServerHost, CollectDt, CollectHH, Message_Text, CollectDTM
                     FROM [dbo].[TB_Rds_Err_Chk_L]
                    WHERE CollectDT BETWEEN CONVERT(VARCHAR, GETDATE()-1, 112) AND CONVERT(VARCHAR, GETDATE(), 112) 
                      AND ServerHost like '%' + '""" + ServerHost + """' + '%'
                    ORDER BY CollectDTM """
    
    result = conn.query(sql_text)
    conn.close()
    # result = monPC.query(sql_text, args)
    
    if result :
        for sms_txt in result :
            if 'page_cleaner:' and 'The settings might not be optimal.' in sms_txt['Message_Text']:
                continue
            # ★★ until TMS_APP_DEVICE_LIST issue solved, exclude tms rds
            elif 'tms' in sms_txt['ServerHost']:
                continue
            else:
                content = content + '일시 : ' + sms_txt['CollectDTM'].strftime("%Y-%m-%d %H:%M:%S") + '\n'
                content = content + '서버 : ' + sms_txt['ServerHost'] + '\n'
                content = content + '내용 : ' + sms_txt['Message_Text']
                
                # print(content)
                msgr.put_msgr_target(content, grp_cd=None, chnl_nm=channel, token_val=SLACK_TOKEN)
                content="\n"
    
    else :
        msgr.put_msgr_target("조회결과가 없습니다.", grp_cd=None, chnl_nm=channel, token_val=SLACK_TOKEN)    


def help(target, channel):
    content="\n"
    for text in DASHBOARD_LIST:
        if text['title'] == 'help' or text['title'] == 'keyword':
            continue
        desc_fn  = '화　면 : ' + fill_str_with_space(text['title'],max_size=40) 
        desc_ex  = '명령어 : ' + fill_str_with_space(text['kor_ex'],max_size=40)
        desc_var = '변　수 : ' + text['parameter']
        content = content + '\n' + desc_fn + '\n' + desc_ex + '\n' + desc_var + '\n'
        
    msgr.put_msgr_target(content, grp_cd=None, chnl_nm=channel, token_val=SLACK_TOKEN)


def keyword(target, channel):
    content="\n"
    for key, value in MAPPING_PARAM.items() :
        input_val    = '입력값 : ' + fill_str_with_space(key,max_size=20)
        mapping_val  = '매핑값 : ' + value
        # content = content + desc_fn + desc_ex + desc_var + '\n'
        content = content + '\n' + input_val + mapping_val
        
    msgr.put_msgr_target(content, grp_cd=None, chnl_nm=channel, token_val=SLACK_TOKEN)


# # ----------------------------------------------------------------------------------------------------
# MAIN 
# ----------------------------------------------------------------------------------------------------

"""
이거 문제 해결이 필요
1. split으로 mapping 시키고 다시 붙일때 "_"를 붙이던가
=> remap_request에서 join

2. 작은 함수 안에서 매개변수 취급하고 다른함수 호출시키던가
=> ()로 시작하는 함수는 다 없애고
=> 1번에 대해서는 remap_request, common_send_img로 공통 빼고 매개변수 전달

20220114 추가
3. 좀 써보고 범위 조회나 특정서버만 조회하는게 필요하다면 추가 매개변수 전달 검토
4. 이미지만 호출하는 함수들은 하나로 합쳐서 더 줄여볼까?
   아니면 cnf에서 
   type을 쪼개서
   1. img : 이미지만 호출
   2. sql : SQL만 호출
   3. both : 둘다 호출
   이렇게 카테고리 나눠서 공통함수 호출하게? 
   물론 SQL은 쿼리 자체는 각각 있어야됨
5. 오늘 채널 추가하면서 번거롭던데, global target_channel 만들어서 
   bot_react_router > common_send_img 이나 send_slack_message에 전달하는 방식은?
"""

def remap_request(input_param):
    # remove whitespace
    # remove PartName : [POS], [MD] ...
    regex = '\[[^)]+\]'
    # split_param = input_param.lower().replace(u'\xa0',u'').split(' ')
    split_param = re.sub(regex, "", input_param).lower().replace(u'\xa0',u'').split(' ') # .replace('#','%23')
    print(split_param)

    # split_param = input_param.re.sub(regex, "", lower().replace(u'\xa0',u'')).split(' ')

    # 기준이 MAPPING_PARAM 순서로 정렬되어 변경
    # changed_param = [value for key, value in MAPPING_PARAM.items() if key in split_param]
    changed_param = []
    option_param = []
    for each_param in split_param:
        # put all of splited content to OPTION_PARAM
        option_param.append(each_param)
        for key, value in MAPPING_PARAM.items() :
            # if MAPPING_PARAM has key, REMOVE IT
            if key == each_param:
                changed_param.append(value)
                option_param.remove(each_param)
        
        # for SERVERHOSTS serverHost mapping
        # if each_param is not included above and below, then it take as what it is
        for key, value in SERVERHOSTS.items() :
            if key == each_param:
                option_param.remove(each_param)
                option_param.append(value)

        # for key, value in tableName.items() :
        #     if key == each_param:
        #         option_param.remove(each_param)
        #         option_param.append(value)

    result_param = "_".join(changed_param)
    return result_param, option_param

def bot_react_router(requested_parm=None, channel='D01R13ZPHL3'):
    print ("requested_parm ===========================================")
    print(requested_parm)

    if requested_parm ==  None or requested_parm ==  '':
        msgr.put_msgr_target("실행에 사용될 매개변수가 없습니다.", grp_cd=None, chnl_nm=channel, token_val=SLACK_TOKEN)
        return
    
    requested_parm, requested_opt = remap_request(requested_parm)

    print(requested_parm)
    print(requested_opt)

    target_exist_check=False
    target=[]

    for check_target in DASHBOARD_LIST:
        if requested_parm == check_target['title']:
            target=check_target
            target_exist_check=True

    if target_exist_check!=True:
            msgr.put_msgr_target("실행 할 수 없는 요청입니다.", grp_cd=None, chnl_nm=channel, token_val=SLACK_TOKEN)
    
    if target_exist_check == True:
        if requested_parm ==  None or requested_parm ==  '':
            msgr.put_msgr_target("실행에 사용될 매개변수가 없습니다.", grp_cd=None, chnl_nm=channel, token_val=SLACK_TOKEN)
            return
        elif requested_parm == 'daily_check':
            for list in target['lists']:
                if list['title'] == 'daily_check_mssql':
                    daily_check_mssql(list, channel)
                elif list['title'] == 'daily_check_oracle':
                    daily_check_oracle(list, channel)
                elif list['title'] == 'daily_check_etc_oracle':
                    daily_check_etc_oracle(list, channel)
        elif requested_parm == 'daily_check_mssql':
            daily_check_mssql(target, channel)
        elif requested_parm == 'daily_check_oracle':
            daily_check_oracle(target, channel)
        elif requested_parm == 'daily_check_etc_oracle':
            daily_check_etc_oracle(target, channel)
        elif requested_parm == 'daily_check_etc_oracle_storage':
            daily_check_etc_oracle_storage(target, channel)
        elif requested_parm == 'daily_check_etc_batch':
            daily_check_etc_batch(target, channel)
        elif requested_parm == 'daily_check_etc':
            for list in target['lists']:
                if list['title'] == 'daily_check_etc_batch':
                    daily_check_etc_batch(list, channel)
                elif list['title'] == 'daily_check_etc_sync':
                    daily_check_etc_sync(list, channel)
                elif list['title'] == 'daily_check_etc_dr':
                    daily_check_etc_dr(list, channel)
                elif list['title'] == 'daily_check_etc_bcv':
                    daily_check_etc_bcv(list, channel)
        elif requested_parm == 'daily_check_etc_sync':
            daily_check_etc_sync(target, channel)
        elif requested_parm == 'daily_check_etc_dr':
            daily_check_etc_dr(target, channel)
        elif requested_parm == 'daily_check_etc_bcv':
            daily_check_etc_bcv(target, channel)
        elif requested_parm == 'daily_check_etc_oracle_detail':
            daily_check_etc_oracle_detail(target, channel)
        elif requested_parm == 'daily_check_mssql_detail_storage':
            daily_check_mssql_detail_storage(target, channel)
        elif requested_parm == 'daily_check_oracle_detail_storage':
            daily_check_oracle_detail_storage(target, channel)
        elif requested_parm == 'daily_check_mssql_detail_err':
            daily_check_mssql_detail_err(target, channel)
        elif requested_parm == 'daily_check_oracle_detail_err':
            daily_check_oracle_detail_err(target, channel)
        elif requested_parm == 'daily_check_netbackup':
            daily_check_netbackup(target, channel)
            
        # 실시간 mssql 사용량
        elif requested_parm == 'realtime_mssql_resource':
            if len(requested_opt) == 1 : requested_opt[0] ='All'
            for list in target['lists']:
                if list['title'] == 'realtime_mssql_cpu_resource':
                    realtime_mssql_cpu_resource(list, requested_opt, channel)
                elif list['title'] == 'realtime_mssql_memory_resource':
                    realtime_mssql_memory_resource(list, requested_opt, channel)
                elif list['title'] == 'realtime_mssql_request_resource':
                    realtime_mssql_request_resource(list, requested_opt, channel)
                elif list['title'] == 'realtime_mssql_transaction_resource':
                    realtime_mssql_transaction_resource(list, requested_opt, channel)
                elif list['title'] == 'realtime_mssql_bufferhit_resource':
                    realtime_mssql_bufferhit_resource(list, requested_opt, channel)
                elif list['title'] == 'realtime_mssql_storage_resource':
                    realtime_mssql_storage_resource(list, requested_opt, channel)
        elif requested_parm == 'realtime_mssql_cpu_resource':
            if len(requested_opt) == 1 : requested_opt[0] ='All'
            realtime_mssql_cpu_resource(target, requested_opt, channel)
        elif requested_parm == 'realtime_mssql_memory_resource':
            if len(requested_opt) == 1 : requested_opt[0] ='All'
            realtime_mssql_memory_resource(target, requested_opt, channel)
        elif requested_parm == 'realtime_mssql_request_resource':
            if len(requested_opt) == 1 : requested_opt[0] ='All'
            realtime_mssql_request_resource(target, requested_opt, channel)
        elif requested_parm == 'realtime_mssql_transaction_resource':
            if len(requested_opt) == 1 : requested_opt[0] ='All'
            realtime_mssql_transaction_resource(target, requested_opt, channel)
        elif requested_parm == 'realtime_mssql_bufferhit_resource':
            if len(requested_opt) == 1 : requested_opt[0] ='All'
            realtime_mssql_bufferhit_resource(target, requested_opt, channel)
        elif requested_parm == 'realtime_mssql_storage_resource':
            if len(requested_opt) == 1 : requested_opt[0] ='All'
            realtime_mssql_storage_resource(target, requested_opt, channel)

        # 실시간 oracle 사용량
        elif requested_parm == 'realtime_oracle_resource':
            if len(requested_opt) == 1 : requested_opt[0] ='All'
            for list in target['lists']:
                print(target['lists'])
                if list['title'] == 'realtime_oracle_cpu_resource':
                    realtime_oracle_cpu_resource(list, requested_opt, channel)
                elif list['title'] == 'realtime_oracle_memory_resource':
                    realtime_oracle_memory_resource(list, requested_opt, channel)
                elif list['title'] == 'realtime_oracle_execution_resource':
                    realtime_oracle_execution_resource(list, requested_opt, channel)
                elif list['title'] == 'realtime_oracle_session_resource':
                    realtime_oracle_session_resource(list, requested_opt, channel)
        elif requested_parm == 'realtime_oracle_cpu_resource':
            if len(requested_opt) == 1 : requested_opt[0] ='All'
            realtime_oracle_cpu_resource(target, requested_opt, channel)
        elif requested_parm == 'realtime_oracle_memory_resource':
            if len(requested_opt) == 1 : requested_opt[0] ='All'
            realtime_oracle_memory_resource(target, requested_opt, channel)
        elif requested_parm == 'realtime_oracle_execution_resource':
            if len(requested_opt) == 1 : requested_opt[0] ='All'
            realtime_oracle_execution_resource(target, requested_opt, channel)
        elif requested_parm == 'realtime_oracle_session_resource':
            if len(requested_opt) == 1 : requested_opt[0] ='All'
            realtime_oracle_session_resource(target, requested_opt, channel)

        # 근태
        elif 'work' in requested_parm:
            if requested_parm == 'work':
                work(target, channel)
            elif requested_parm == 'work_part':
                work_part(target, requested_opt, channel)
            elif requested_parm == 'work_indivisual':
                work_indivisual(target, requested_opt, channel)
            else :
                msgr.put_msgr_target("실행 할 수 없는 요청입니다.", grp_cd=None, chnl_nm=channel, token_val=SLACK_TOKEN)
                return

        # 매뉴얼
        elif 'help' in requested_parm:
            help(target, channel)
        elif 'keyword' in requested_parm:
            keyword(target, channel)