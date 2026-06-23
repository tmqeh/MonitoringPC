import requests
import json
from slack_sdk import WebClient

# common & configuration
import cfg.config_msgr as cnf
from datetime import datetime

# 20240830 line -> jandi default로 변경
def send_line_message(args, line_token=cnf.LINE_TOKEN) :
  # response = 
  requests.post(cnf.LINE_API_URL,
                headers={'Authorization': 'Bearer ' + line_token},
                data={'message': args}
                )


def send_line_image (args, line_token=cnf.LINE_TOKEN) :
  # File Open (Read Binary)
  with open(args, 'rb') as file:
    # Request send Image to User
    response = requests.post(cnf.LINE_API_URL,
                             headers={'Authorization': 'Bearer ' + line_token},
                            #  data={'message': 'On-Premise DB 일일 점검 내용입니다.'},
                             files= {'imageFile': file}
                             )
  # Check Log
  # print(response.text)


def send_slack_message (contents, slack_channel=cnf.SLACK_CHANNEL_BRAD) :
  msg = {"channel": slack_channel,"text": contents}
  response = requests.post(cnf.SLACK_API_URL,headers={"Authorization": "Bearer "+cnf.SLACK_TOKEN}, data=msg)
  # print(response)


def send_slack_image (file_full_path, title, slack_channel=cnf.SLACK_CHANNEL_BRAD) :
  # File Open (Read Binary)
  with open(file_full_path, 'rb') as image_name:
    response = WebClient(token=cnf.SLACK_TOKEN).files_upload(channels=slack_channel,
                                                             initial_comment=title,
                                                             file=image_name,
                                                             )
    # Check Log
    # print(response)
# for send_data in file_list:


def send_jandi_message (data, title="프로그램오류", jandi_token=cnf.JANDI_TOKEN_DEFAULT, connect_color="RED") :

  jandi_url = cnf.JANDI_API_URL + jandi_token
  body_color = connect_color
  
  # print(body_color)
  # if connect_color=='RED':
  #   print(data)

  header ={"Accept": "application/vnd.tosslab.jandi-v2+json",\
           "Content-Type": "application/json"
          }

  # print(data)
  # print(data[0]["title"])
  body = {"body":title, \
          "connectColor":body_color,"connectInfo":[{"description": data}]}
  print(body)
  
  response = requests.post(url=jandi_url, data=json.dumps(body), headers=header)

  # Check Log
  print(response)


def send_webex_message (msg, send_title="",send_funcnm="") :
  webex_url = cnf.WEBEX_API_URL
  webex_token = cnf.WEBEX_TOKEN_DB_BOT
  webex_roomid = cnf.WEBEX_ROOMID_DEFAULT

  current_dtm = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

  headers = {
      'Authorization': f'Bearer {webex_token}'
      ,'Content-Type': 'application/json'
      }
  
  data = {
    'roomId': webex_roomid,
    'markdown': 'Please click the button below to confirm your attendance.',
              'attachments': [
                  {
                      "contentType": "application/vnd.microsoft.card.adaptive",
                      "content": {
                          "type": "AdaptiveCard",
                          "version": "1.0",
                          "body": [                          
                              {
                                  "type": "TextBlock",
                                  "text": send_title,
                                  "weight": "Bolder",
                                  "size": "Large"
                              },
                              {
                                  "type": "TextBlock",
                                  "spacing": "None",
                                  "text": "Created "+ current_dtm,
                                  "isSubtle": True,
                                  "wrap": True
                              },                              
                              {
                                  "type": "TextBlock",
                                  "text": msg,
                                  "wrap": True,
                                  "spacing": "ExtraLarge"
                              },
                              {
                                  "type": "TextBlock",
                                  "text": "# function : " + send_funcnm,
                                  "size": "Small",
                                  "color": "Light",
                                  "isSubtle": True,
                                  "wrap": True,
                                  "spacing": "ExtraLarge"
                              }   
                          ]
                      }
                  }
              ]              
      }

  response = requests.post(webex_url, headers=headers, json=data)

  if response.status_code == 200:
      print('Webhook 생성 성공:', response.json())
  else:
      print('Webhook 생성 실패:', response.status_code, response.text)

# Test Example
# file_full_path = 'C:\\rdslog\\daily_check\\' + cnf.YMD + '_DMS-Daily-Report_Grafana_Daily.jpg'
# send_line_message("send_line_message test")
# send_line_image(file_full_path)
# send_slack_message("send_slack_message test",'D041DMDCESV')
# send_slack_image(file_full_path,'image test','D041DMDCESV')
# send_jandi_message("다이렉트 메시지 전송 테스트")