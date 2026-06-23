# common & configuration
# import cmn.common_db as db
import cmn.common_msgr_direct as msgr
from cmn.common_db import monPC


def put_msgr_target(args, grp_cd='DBWX99', chnl_nm=None, token_val=None, img_file_path=None, send_title=None, msgr_color=None, send_funcnm=None):

    conn = monPC()

    # 20240524 insert "Unclosed quotation mark after the character string" 이슈로 인한 replace 추가
    args = args.replace("\x00","")
    sqlTxt = ""
    api_url = ""
    chnl_cl_cd = ""

    if not grp_cd == None:
        sqlTxt = """ select CHNL_CL_CD, TKN_VAL, CHNL_NM, GRP_CD
                    from TB_MSG_CHNL_M
                  where GRP_CD = %s
              """

        conn.execute(sqlTxt, (grp_cd))
        fetchData = conn.fetchall()

        result =  [dict((conn.description()[i][0], value) \
                        for i, value in enumerate(row)) for row in fetchData]

        if result:
            if result[0]["CHNL_CL_CD"] == "SL" and img_file_path != None:
                api_url = "https://slack.com/api/files.getUploadURLExternal"
            elif result[0]["CHNL_CL_CD"] == "SL" and img_file_path == None:
                api_url = "https://slack.com/api/chat.postMessage"
            elif result[0]["CHNL_CL_CD"] == "LN":
                api_url = "https://notify-api.line.me/api/notify"
            elif result[0]["CHNL_CL_CD"] == "JD":
                api_url = "https://wh.jandi.com/connect-api/webhook/"
            elif result[0]["CHNL_CL_CD"] == "WX":
                api_url = "https://webexapis.com/v1/messages"
            else:
                msgr.send_jandi_message("common_msgr put_msgr_target: " + "매개변수 오류")
                return
        else:
            msgr.send_jandi_message("common_msgr put_msgr_target: " + "GRP_CD 없음")
            return

        # SQL 호출
        sqlTxt = """
                insert into TB_MSG_SEND_I 
                    ( CHNL_CL_CD
                    , API_URL
                    , TKN_VAL
                    , CHNL_NM
                    , RSLT_CONT
                    , RGST_DTM
                    , SEND_CONT
                    , IMG_FILE_PATH
                    , RGPR_ID
                    , SEND_TIT
                    , MSGR_COLR
                    , REQ_FUN_NM)
                select CHNL_CL_CD
                    , %s as API_URL
                    , TKN_VAL
                    , CHNL_NM
                    , 'Requested' as RSLT_CONT
                    , GETDATE() as RGST_DTM
                    , %s as SEND_CONT
                    , %s as IMG_FILE_PATH
                    , 'put_msgr_target' -- 여기는 소스명
                    , %s as SEND_TIT
                    , %s as MSGR_COLR
                    , %s as REQ_FUN_NM
                  from TB_MSG_CHNL_M
                where GRP_CD = %s -- 여기가 변수
              """

        # only Slack
        """
        작성 배경 : 토큰과 채널 모두 공통 테이블로 관리하고 싶었으나,
                    bot에서 사용하는 경우, 
                    봇이 종속된 협업툴 메신저에 종속된 소스와 종속된 토큰을 소스 또는 설정 파일에 넣을 수 밖에 없다.
                    
                    DBA만 사용하는 봇일 경우, token을 고정 시킬 수 있지만
                    범용으로 사용하기 위해서는 변수로 토큰을 받도록 def를 수정하고
                    공통 테이블을 거치지 않고 insert할 수 있도록 수정해야한다.
        """
    # grp_cd == None & chnl_nm != None
    else:
        if len(chnl_nm) <= 11:
            chnl_cl_cd = "SL"
        elif len(chnl_nm) > 11 and "/" in chnl_nm:
            chnl_cl_cd = "JD"
            api_url = "https://wh.jandi.com/connect-api/webhook/"
        else:
            chnl_cl_cd = "LN"
            api_url = "https://notify-api.line.me/api/notify"

        if token_val and img_file_path != None:
            api_url = "https://slack.com/api/files.getUploadURLExternal"
        elif token_val and img_file_path == None:
            api_url = "https://slack.com/api/chat.postMessage"
        else:
            msgr.send_jandi_message("common_msgr put_msgr_target: " + "매개변수 오류")
            return

        # SQL 호출
        sqlTxt = """
                insert into TB_MSG_SEND_I 
                    ( CHNL_CL_CD
                    , API_URL
                    , TKN_VAL
                    , CHNL_NM
                    , RSLT_CONT
                    , RGST_DTM
                    , SEND_CONT
                    , IMG_FILE_PATH
                    , RGPR_ID
                    , SEND_TIT
                    , MSGR_COLR
                    , REQ_FUN_NM)
                values 
                     ( %s
                     , %s 
                     , %s
                     , %s
                     , 'Requested'
                     , GETDATE()
                     , %s 
                     , %s 
                     , 'put_msgr_target' -- 여기는 소스명
                     , %s 
                     , %s
                     , %s 
                      )
              """
    try:
        if not grp_cd == None:
            conn.execute(sqlTxt, (api_url, args, img_file_path, send_title, msgr_color, send_funcnm, grp_cd))

        else:  # grp_cd == None & chnl_nm != None
            # print(sqlTxt)
            conn.execute(sqlTxt, (chnl_cl_cd, api_url, token_val, chnl_nm, args, img_file_path, send_title, msgr_color, send_funcnm))
        conn.commit()

    except Exception as e:
        msgr.send_jandi_message("common_msgr put_msgr_target Error except : " + str(e))

    finally:
        conn.close()


# put_msgr_target('슬랙 이미지 파일 전송 테스트', 'DB0001', img_file_path=r'C:\rdslog\daily_check\20230112083001_daily_check_etc_dr_Grafana_Daily.jpg')
# put_msgr_target('슬랙 텍스트 전송 테스트', 'DB0001')
# put_msgr_target('블루', 'DBWX99', send_title='타이틀 테스트', msgr_color='BLUE')
# put_msgr_target('그린', 'DBWX99', send_title='타이틀 테스트')
