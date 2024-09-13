import requests
import json
import os # for os.path.getsize

# common & configuration
import cmn.common_msgr_direct as msgr # for DB down (sending direct)
from cmn.common import get_cur_func_nm as func_nm, get_cur_file_nm as file_nm, get_func_tree as func_tree
import cmn.common_db as db


# korean needs    .encode('ISO-8859-1').decode('euc-kr') for array
def parse_response(response):
    if len(response) == 0: # 잔디
        return "Finished"
    elif 'ok' in response: # 슬랙
        if response['ok'] == True:
            return "Finished"
        else:
            return str(response['error'])
    elif 'status' in response: # 라인
        if response['status'] == 200:
            return "Finished"
        else:
            return "[" + str(response['status']) + "]" + str(response['message'])
    elif 'code' in response:
        return "[" + str(response['code']) + "]" + str(response['msg'])
    else:
        msgr.send_jandi_message('realtime_msgr parse_response :' + "알수없는 json 형태입니다.")

        
def get_msgr_target(conn):
    # cursor = conn.cursor

    sqlTxt = """ select SEND_SEQNO, CHNL_CL_CD, API_URL, TKN_VAL, CHNL_NM, SEND_CONT, RSLT_CONT, IMG_FILE_PATH, SEND_TIT, MSGR_COLR
                   from TB_MSG_SEND_I
                  where RSLT_CONT = 'Requested'
             """

    try:
        data = conn.query(sqlTxt)
        result = []
        result = [dict((conn.description()[i][0], value) \
                            for i, value in enumerate(row)) for row in data]
        return result

    except Exception as e:
        # print(func_nm() + ": " + str(e))
        msgr.send_jandi_message(func_tree() + ":\n" + str(e))

    finally:
        sqlTxt = ""
        # conn.close()


def update_msgr_in_process(args, conn):
    # cursor = conn.cursor

    sqlTxt = """
                MERGE dbo.TB_MSG_SEND_I AS A
                USING (SELECT %d as SEND_SEQNO
                    ) AS B
                ON (    A.SEND_SEQNO = B.SEND_SEQNO
                )
                WHEN MATCHED AND A.RSLT_CONT = 'Requested' THEN
                    UPDATE SET   A.RSLT_CONT = %s
                            , A.MDFPR_ID  = 'update_msgr_in_process'
                            , A.MDF_DTM   = getdate()
            ;
            """
    # list to list
    # for putting comma logic, enumerate is necessary
    send_seqno  = args['SEND_SEQNO']
    result_cont = 'in Process'
    
    # print(sqlTxt)
    conn.execute(sqlTxt
                    ######## for select
                    , (send_seqno
                    ########### for insert
                    ######### for update
                    , result_cont))

    try:
        # even MS-SQL need it (MUST)
        conn.commit()

    except Exception as e:
        # print(func_nm() + ": " + str(e))
        msgr.send_jandi_message(func_tree() + ":\n" + str(e))

    finally:
        sqlTxt = ""
        # conn.close()


def update_msgr_finished(args, response, conn):
    # cursor = conn.cursor

    sqlTxt = """
                MERGE dbo.TB_MSG_SEND_I AS A
                USING (SELECT %d as SEND_SEQNO
                    ) AS B
                ON (    A.SEND_SEQNO = B.SEND_SEQNO
                )
                WHEN MATCHED AND A.RSLT_CONT = 'in Process' THEN
                    UPDATE SET   A.RSLT_CONT = %s
                            , A.MDFPR_ID  = 'update_msgr_finished'
                            , A.MDF_DTM   = getdate()
            ;
            """
    # list to list
    # for putting comma logic, enumerate is necessary
    send_seqno  = args['SEND_SEQNO']
    result_cont = response
    
    # print(sqlTxt)
    conn.execute(sqlTxt
                    ######## for select
                    , (send_seqno
                    ########### for insert
                    ######### for update
                    , result_cont))

    try:
        # even MS-SQL need it (MUST)
        conn.commit()

    except Exception as e:
        # print(func_nm() + ": " + str(e))
        msgr.send_jandi_message(func_tree() + ":\n" + str(e))

    finally:
        sqlTxt = ""
        # conn.close()


def move_msgr_results(args, conn):
    # cursor = conn.cursor

    sqlTxt = """
                insert into dbo.TB_MSG_SEND_L 
                     ( SEND_SEQNO,    CHNL_CL_CD
                     , API_URL,      TKN_VAL,   CHNL_NM
                     , SEND_CONT,    RSLT_CONT
                     , IMG_FILE_PATH
                     , SEND_TIT,     MSGR_COLR
                     , RGPR_ID,      RGST_DTM
                     , MDFPR_ID,     MDF_DTM)
                select SEND_SEQNO,    CHNL_CL_CD
                     , API_URL,      TKN_VAL,   CHNL_NM
                     , SEND_CONT,    RSLT_CONT
                     , IMG_FILE_PATH
                     , SEND_TIT,     MSGR_COLR
                     , RGPR_ID,      RGST_DTM
                     , MDFPR_ID,     MDF_DTM
                  from TB_MSG_SEND_I
                 where SEND_SEQNO = %d
                   -- and RSLT_CONT = 'Finished'
            """
    

    sqlTxt2 = """
                  delete from TB_MSG_SEND_I
                  where SEND_SEQNO = %d
                  -- and RSLT_CONT = 'Finished'
              """
    # list to list
    send_seqno = args['SEND_SEQNO']
    
    # print(sqlTxt)
    # print(sqlTxt2)
    conn.execute(sqlTxt,  (send_seqno))
    conn.execute(sqlTxt2, (send_seqno))

    try:
        # even MS-SQL need it (MUST)
        conn.commit()

    except Exception as e:
        # print(func_nm() + ": " + str(e))
        msgr.send_jandi_message(func_tree() + ":\n" + str(e))
        # return 0

    finally:
        sqlTxt = ""
        # conn.close()


def send_msg(args):
    # need convert encoding
    args['SEND_CONT'] = args['SEND_CONT'].encode('ISO-8859-1').decode('euc-kr')
    if args['SEND_TIT']:
        args['SEND_TIT']  = args['SEND_TIT'].encode('ISO-8859-1').decode('euc-kr')

    try:
        if args['CHNL_CL_CD'] == 'SL' and args['IMG_FILE_PATH'] == None: # 슬랙/이미지X
            msg = {"channel": args['CHNL_NM'],"text": args['SEND_CONT']}
            response = requests.post(args['API_URL'],
                                     headers = {"Authorization": "Bearer " + args['TKN_VAL']}, 
                                     data    =   msg
                                    )
            # Check response
            return parse_response(response.json())

        elif args['CHNL_CL_CD'] == 'SL' and args['IMG_FILE_PATH'] != None: # 슬랙/이미지O
            # File Open (Read Binary)
            with open(args['IMG_FILE_PATH'], 'rb') as image_name:
                # 파일 업로드 URL 확보
                pre_msg = {"filename": args['IMG_FILE_PATH'], "length" : os.path.getsize(args['IMG_FILE_PATH'])}
                pre_response = requests.post(args['API_URL'],
                                         headers = {"Authorization": "Bearer " + args['TKN_VAL']},
                                         data    =   pre_msg
                                        )
                if pre_response.status_code != 200:
                    return parse_response(pre_response.json())

                # 파일 업로드 요청
                response_upload = requests.post(pre_response.json()["upload_url"], files={'upload_file': image_name})
                if response_upload.status_code != 200:
                    return parse_response(response_upload.json())

                # 업로드 파일 채널 공유
                msg = {"files" : [{"id":pre_response.json()["file_id"], "title": args['SEND_CONT']}], "channel_id": args['CHNL_NM'], "pretty":1}
                response = requests.post("https://slack.com/api/files.completeUploadExternal",
                                         headers = {"Authorization": "Bearer " + args['TKN_VAL'], "Content-type": "application/json; charset=utf-8"},
                                         json    =   msg
                                        )

                # Check response
                return parse_response(response.json())
            
        elif args['CHNL_CL_CD'] == 'LN' and args['IMG_FILE_PATH'] == None: # 라인/이미지X
            msg = {'message': args['SEND_CONT']}
            response = requests.post(args['API_URL'],
                                     headers = {'Authorization': 'Bearer ' + args['TKN_VAL']},
                                     data    =   msg
                                    )
            # Check response
            return parse_response(response.json())
                       
        elif args['CHNL_CL_CD'] == 'LN' and args['IMG_FILE_PATH'] != None: # 라인/이미지O
            # File Open (Read Binary)
            with open(args['IMG_FILE_PATH'], 'rb') as file:
                msg = {'message': args['SEND_CONT']}
                # Request send Image to User
                response = requests.post(args['API_URL'],
                                         headers = {'Authorization': 'Bearer ' + args['TKN_VAL']},
                                         data    =   msg,
                                         files   = {'imageFile': file}
                                        )
                # Check response
                return parse_response(response.json())
                                
        elif args['CHNL_CL_CD'] == 'JD': # 잔디
            jandi_url = args['API_URL'] + args['TKN_VAL']
            body_color = args['MSGR_COLR']
            if not body_color:
                body_color = 'GREEN'
            header = {"Accept": "application/vnd.tosslab.jandi-v2+json",
                      "Content-Type": "application/json"
                     }
            msg = json.dumps({"body": args['SEND_TIT'],# ymdHH24MISS,#args['SEND_CONT'],  
                              # jandi body 가시성이나 포맷이 너무 형편없는데 이렇게 하면 어플 푸시에 시간만 떠서 이부분은 고민좀해봐야되겠다.
                              # 잔디 SE 일일점검하고 합치려면 골치 꽤나 썩을듯.
                              # 그냥 connectInfo에 title을 걷어내고 description만 쓰는식으로 바꿔야될듯.
                              # body에는 args['SEND_TIT'] 그대로 넣고 (그럼 테이블 구조변경이나 별도 작업 필요 없고)
                              # title이 bold 처리외엔 별거 없어서 그냥 걷어내도 될듯.
                              "connectColor": body_color,
                              "connectInfo":[{# "title": args['SEND_TIT'], 
                                              "description": args['SEND_CONT']}
                                            ]
                              })
            response = requests.post(url=jandi_url, data=msg, headers=header)
            # Check response
            return parse_response(response.json())

        else:
            msgr.send_jandi_message('realtime_msgr send_msg: ' + '규격에 맞지 않는 데이터입니다.')
            
    except Exception as e:
        # print(func_nm() + ": " + args['CHNL_CL_CD'] +' ' + args['IMG_FILE_PATH'] + '\n' + str(e))
        msgr.send_jandi_message(func_tree() + ":\n" + args['CHNL_CL_CD'] +' ' + args['IMG_FILE_PATH'] + '\n' + str(e))

    finally:
        # msgr.send_jandi_message('send_msg Finished')
        pass


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------        
if __name__ == "__main__":
    conn = db.monPC(file_nm())
    # cursor = conn.cursor
    result = get_msgr_target(conn) # 1. select target (Requsted)
    try :
        if result:
            for dataset in result:
                # 2. update send_seqno -> in Process
                update_msgr_in_process(dataset, conn)
                
                # 3. branch by chnl_cl_cd
                # 4. send message
                response = send_msg(dataset)
                
                # 5. update send_seqno -> Finished
                update_msgr_finished(dataset, response, conn)
                
                # 6. move to Log Table and Delete
                # commented for test
                move_msgr_results(dataset, conn)
        else:
            pass       
        
    except Exception as e:
        # print(file_nm() + ": " + str(e))
        msgr.send_jandi_message(file_nm() + ": " + str(e))
        
    finally:
        conn.close()
        