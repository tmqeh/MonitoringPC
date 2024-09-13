# -*- coding: utf-8 -*-
""" 
----------------------------------------------------------------------
사용법 설명 
----------------------------------------------------------------------

flask : 서버 프레임 워크 (추후 django로 전환 예정)
-> slack 에서 입력하는 POST(또는 GET) 방식의 요청을 받아서 처리함
=> 외부에서 접속 가능한 url이 있어야 하기 때문에 ngrok 필요

실행 : SET FLASK_APP=flask_app.py 하고나서 flask run 입력
(아직 경로 수정하고 실행은 안해봐서 모르겠지만 PATH 또는 변수 등록할때는 절대경로 입력하자.)


ngrok : 터널링 프로그램, 외부에서 로컬 바라볼 수 있게 만들어줌
-> 일반적인 다운로드 후, 실행은 8시간 제약사항이 있음
=> 회원가입하고 토큰 적용하면 재실행할때까지는 동일한 url 사용 가능
   https://dashboard.ngrok.com/get-started/setup 에서 "Connect your account"에 있는 내용 등록해주면 됨

slack : bot의 처리내용을 받아 메신저에 전달해주는 역할

★ ngrok 재기동 시, 바뀐 url을 하단에 접속하여 입력해주어야됨
※ 기동 명령어, 해당 exe 파일 있는 경로에서
   ngrok http 5000
APP_URL : https://api.slack.com/apps/A01R71H9SQL/event-subscriptions
=> "Request URL"이 "Verified"라고 떠야됨
★ 모니터링을 기동 시킨 상태에서 해야 verify가 뜸 (아마도 respone을 줄수 있는 상태가 되어야 되는듯)

※ 개발할 때, POST 방식에서 각종 사이트에서는 POST 방식에 대한 설명이 없을 뿐더러
   있는 사이트도 headers에 대한 얘기가 없는데 headers를 입력하면 "Verified" 쉽게 볼 수 있음.
 
※ 봇 구축 참고사이트 : https://kitle.xyz/post/60/
"""

import json
from flask  import Flask, request, make_response
from slacker import Slacker
import re # 멘션 exclude 목적

# common & configuration
from cfg.config_msgr import SLACK_TOKEN
import cmn.common_msgr as msgr
import bot.realtime_bot_react as react
from cmn.common import get_cur_func_nm as func_nm, get_cur_file_nm as file_nm, get_func_tree as func_tree

slack = Slacker(SLACK_TOKEN)
app = Flask(__name__)

def event_handler(event_type, slack_event):
    channel = slack_event["event"]["channel"]
    string_slack_event = str(slack_event)

    msg_sender = ""
    tmp_user_query = "" # str type
    user_query = [] # convert to list
    
    if string_slack_event.find("{'type': 'user', 'user_id': ") != -1 : # 사용자 요청 JSON으 텍스트 일부를 체크 (개선 여지 있음)
        msg_sender = "User"
        
    elif string_slack_event.find("'pretext':") and string_slack_event.find("'fallback':") != -1 : # Grafana 요청 JSON으 텍스트 일부를 체크 (개선 여지 있음)
        msg_sender = "Grafana"
        tmp_user_query = slack_event['event']['attachments'][0]['text']
        # tmp_user_query = re.sub(r"<@[^>]+>", '', slack_event['event']['attachments'][0]['text'])
    
    # ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ 
    # 임시(디버깅) : grafana 에서 오는 요청을 제외할 때 사용 (user가 없어서 결과값 -1)
    # if string_slack_event.find("{'type': 'user', 'user_id': ") == -1 : 
    #     return

    try:
        # 20220615 갑자기 모바일 호출할때, ['elements'][1]['text']은 공백, ['elements'][2]['text']에 데이터가 들어가서 수정
        # (데스크탑이나 모바일에서 문구 복사해서 붙여넣으면 정상, 이상함)
        # print(len(slack_event['event']['blocks'][0]['elements'][0]['elements']))
        # if len(slack_event['event']['blocks'][0]['elements'][0]['elements']) == 3:
        #     user_query = slack_event['event']['blocks'][0]['elements'][0]['elements'][2]['text']
        # else :
        #     user_query = slack_event['event']['blocks'][0]['elements'][0]['elements'][1]['text']

        # 20220616 모바일 호출 시, 띄워쓰기 기준으로 배열이 갈라지는 현상 추가 발견, loop로 개선
        if msg_sender == "User":
            for i in range (1, len(slack_event['event']['blocks'][0]['elements'][0]['elements'])):
                # user_query = user_query + slack_event['event']['blocks'][0]['elements'][0]['elements'][i]['text']
                if 'text' in slack_event['event']['blocks'][0]['elements'][0]['elements'][i]:                    
                    user_query.append(slack_event['event']['blocks'][0]['elements'][0]['elements'][i]['text'].replace("\n",""))                    

        elif msg_sender == "Grafana":
            # re.sub(r"<@[^>]+>", '', slack_event['event']['attachments'][0]['text'])
            user_query = re.sub(r"<@[^>]+>", '', tmp_user_query).split("\n")

        # 추가 기능 개선
        # 1. help, 매뉴얼 : help => 텍스트로 보여주기

        # 2. 채널 추가 : 이거 뭐였지
        # => 메시지 전송 대상 매개변수 추가였음
        # => 20220114 완료
        
        # 3. 근태 관련
        # => 20220114 완료 
        
        # 4. dict에 없는 매개변수는 다른 변수로 빼는 방향
        # => 20220114 완료 
        # => 포맷 완전 통일하려다가 개별 함수 호출 매개변수 조정과 공통함수 유연하게 작성으로 조정
        
        # 5. remap할때 정렬 안되게
        # => 20211229 완료
        
        # 6. 2번 호출하는 원인 해결 => 이거 ("event" in slack_event:) 이부분 때문으로 추정
        # => if문으로 처리했지만 다수 수행 => reload가 multiple times로 수행되는게 문제로 추정
        # => ★★★ 20220114 원인 찾은거 같음, 아래 내용 (3초내로 response 줘야됨)
        """ https://github.com/slackapi/java-slack-sdk/issues/646 
            Through the official document, I knew that a retry would occur 
            if the response was not returned within 3 seconds, 
            
            and I used AsyncMethodsClient to solve this problem. 
            Nevertheless, the problem continues to arise.
            The same problem also continues to occur even though 
            the header of the Response object has returned the object X-slack-No-Retry: 1.
        """
        
        # 7. 이미지 업로드 성능 개선 방안 (안되면 쿼리로 하는 쪽으로)
        # => 20220105 완료 (8번으로 조치하면서 성능까지 개선됨)
        
        # 8. curl vs file_upload 충돌 해결
        # => 20220105 완료 (os.system 안쓰고 requests로 수정)

        # 9. grafana 봇 연동
        # => 20231031 시작 ~ 20231009 완료
        
        # 10. multi 요청 처리
        # 20231110 완료
        # => 시스템 묶어서 1장에 보여주면 좋겠는데 방법 없을까
        for request_text in user_query:
            react.bot_react_router(request_text, channel) # ★ bot 모듈 호출
        return make_response("ok", 200, ) # {"X-Slack-No-Retry": 1})
    
    except IndexError:
        pass
    message = "[%s] cannot find event handler" % event_type
    return make_response(message, 200, ) #{"c": 1})

# VERY IMPORTANT
# to prevent POST request multiple times
global client_msg_id
client_msg_id = ''

@app.route('/', methods=['POST'])
def bot_daemon():
    slack_event = json.loads(request.data)
    # print(json.dumps(slack_event["event"],indent=4))
    print(slack_event)

    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200, {"content_type": "application/json"})

    if "event" in slack_event:
        target_client_msg_id = ''
        global client_msg_id        

        # to avoid bot event
        if "client_msg_id" in slack_event["event"]:
            target_client_msg_id = slack_event["event"]['client_msg_id']

            # to prevent POST request multiple times
            if client_msg_id != target_client_msg_id:
                client_msg_id = target_client_msg_id
                event_type = slack_event["event"]["type"]
                return event_handler(event_type, slack_event)
        # grafana bot 호출
        elif "attachments" in slack_event["event"]:
            event_type = slack_event["event"]["type"]
            return event_handler(event_type, slack_event)

    # return make_response("There are no slack request events", 404, {"X-Slack-No-Retry": 1})
    return make_response("There are no slack request events", 200,) # {"X-Slack-No-Retry": 1})


# 단건이면 slack으로 그래프까지 보여주고
# 여러개면 아래껄로 잔디에 쏴주는 형식으로 하는게 어떨까 싶음
@app.route('/grafana', methods=['POST'])
def grafana_alaram():
    # grafana_event = json.dumps(json.loads(request.data),indent=4)
    grafana_event = json.loads(request.data)["alerts"] # 
    # grafana_event2 = json.loads(request.data)["message"] # str
    
    title_content = ""
    content = ""
    alert_color = ""

    try:
        for data in grafana_event: # 여기서부터 dict니까 key value로 핸들링 하자
            # 불필요 항목 (%url) 제거
            del data["generatorURL"]
            del data["silenceURL"]
            del data["dashboardURL"]
            del data["panelURL"]
            # 추가 제거
            del data["fingerprint"]
            # print(data["valueString"])
            del data["valueString"]
            # print(data) # 🔥✅
            alert_color = "yellow"
            
            print(data)
            
            # 일일이 가공해야되는게 되게 별로다.
            # 더 좋은 방법이 없을까
            for data_key, data_value in data.items():
                print(" ========================================")

                if data_key == "status" and data_value == "firing":
                    content = "" # ★ 🔥
                    alert_color = "RED"
                    title_content = "[C] "
                elif data_key == "status" and data_value == "resolved":
                    content = "" # ☆ ✅
                    alert_color = "GREEN"
                    title_content = "[N] "
                
                if data_key == "labels":
                    key_order = ["ServerName","리소스","rulename"] # label 순서 지정
                    sorted_dict = {key:data_value[key] for key in key_order if key in data_value}
                    
                    # key_order에 없는 항목들은 key_order 뒤에 그대로 이어 붙임
                    for sort_key, sort_value in data_value.items():
                        if sort_key not in sorted_dict:
                            sorted_dict[sort_key] = sort_value

                    # 필요없다고 판단되는 라벨은 무시하고 건너뜀
                    for lable_key, label_value in sorted_dict.items():
                        if any(item in lable_key for item in ["alertname", "grafana_folder", "DBMS", "채널", "ref_id"]): # 불필요 label pass
                            continue
                            
                        # label rename
                        if lable_key == "PartName":
                            lable_key = "파트"
                        elif lable_key == "ServerName":
                            lable_key = "서버"
                            if alert_color == "RED": # 제일 중요하다고 판단되는 라벨의 값에 dummy 링크 씌워서 강조 표시
                                label_value = "[" + label_value +"]()"
                            title_content = title_content + label_value + " "
                        elif lable_key == "리소스":
                            if alert_color == "RED": # 제일 중요하다고 판단되는 라벨의 값에 dummy 링크 씌워서 강조 표시
                                label_value = "[" + label_value +"]()"
                            title_content = title_content + label_value + " "
                        elif lable_key == "rulename":
                            lable_key = "규칙"
                        # 데이터 수집 지연 현상이 있을 때, datasource_uid 가 같이 딸려옴
                        elif lable_key == "datasource_uid":
                            content = content + "데이터 수집 지연 현상" + "\n" 
                            continue
                        # 소숫점이 들어올때 2째자리 까지만 표기하도록 수정
                        elif lable_key == "현재값":
                            # print(isinstance(label_value))
                            label_value = float(label_value)
                            if isinstance(label_value, int):
                                label_value = label_value
                            elif isinstance(label_value, float):
                                label_value = f"{label_value:.2f}"

                        content = content + lable_key + ": " + label_value + "\n"

                # 시간 표기
                if data_key == "startsAt":
                    content = content + "발생: " + data_value.replace("T"," ").replace("+09:00","") + "\n" 
                elif data_key == "endsAt" and data_value != "0001-01-01T00:00:00Z":
                    content = content + "해소: " + data_value.replace("T"," ").replace("+09:00","")[:19] + "\n" 

                # grafana Expressions 데이터
                # 참고 : thredshold는 0/1 Flag로 전달됨
                if data_key == "values" and data_value is None:
                    data_value = ""
                elif data_key == "values" and data_value is not None:
                    for values_key, values_value in data_value.items():
                        if values_key == "임계치" and values_value == 1:
                            values_value = "임계치 초과"
                        elif values_key == "임계치" and values_value == 0:
                            # values_value = "임계치 해소"
                            continue 
                        content = content + values_key + ": " + str(values_value) + "\n"

                # print(data_key)
                # print(data_value)

            print(content)
            # if alert_color == "RED":
            #     title_content = "**확인필요**"
            # else:
            #     title_content = "**정상화**"                        
            msgr.put_msgr_target(content, grp_cd="DB0003",send_title=title_content, msgr_color=alert_color)
            content = ""
            title_content = ""

            # test
            
        return make_response("There are no grafana request events", 200,) # {"X-Slack-No-Retry": 1})
    except Exception as e:
        msgr.put_msgr_target(func_tree() + ":\n" + str(e), grp_cd="DB9993", send_title="**" + func_nm() + "**", msgr_color="RED")


if __name__ == '__main__':
    try:
        # 모든 호스트에서 접속 가능하도록 설정
        # flask 서비스 포트 5000
        app.run(host='0.0.0.0', port=5000, debug=True)

    except Exception as e:
        msgr.put_msgr_target(str(e), grp_cd="DB9993", send_title="**" + file_nm() + "**", msgr_color="RED")
