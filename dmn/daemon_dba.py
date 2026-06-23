"""
# 데몬 서비스 등록은
# python xxx.py install 이라고 등록하던지
# sc create DBADaemon binpath= "C:\ProgramData\Anaconda3\python.exe C:\dbapgm\src\dmn\daemon_dba.py" DisplayName= "DBADaemon" start= auto 
# 라고 등록하면됨
# debug는 python xxx.py debug
# ※ 소스 정리후 "sc create"문으로 안됨 (원인 확인 안됨), 
#    "python daemon_dba.py install"로 구성 및 "from logging import Formatter, Handler, handlers" 주석 해제로 해결
"""
import time # for sleep 
import os # for log rotation
import datetime # for refresh now

# standard python libs 
import logging 
from logging import Formatter, Handler, handlers # this is important to register service

# for Windows Service Registration 
import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import traceback  # 추가: 예외 처리시 상세한 정보 출력을 위해 추가

# common & configuration
from cfg.config_path import LOG_HOME
import cmn.common_msgr as msgr
from cmn.common_datetime import YMDHH24MISS, NOW
import bch.realtime_report_err_dba as realtime_err
from cmn.common import get_cur_func_nm as func_nm, get_cur_file_nm as file_nm, get_func_tree as func_tree

# file path
# STDIN_PATH          = LOG_HOME
# STDOUT_PATH         = LOG_HOME + "log" 
STDERR_PATH         = LOG_HOME + "daemon/"
# TARGET_PATH         = LOG_HOME + "target"
# SQL_PATH            = LOG_HOME + "sql" 

# Constant
DAEMON_SLEEP_TIME   =  60
GATHER_DB_INTERVAL  = 300

DAEMON_NAME         = "DBADaemon"
DISPLAY_NAME        = "DBADaemon"
LOGGER_NAME         = "DBADaemonLog"


class AppServerSvc (win32serviceutil.ServiceFramework):
    global DAEMON_NAME
    global DISPLAY_NAME
    _svc_name_         = DAEMON_NAME
    _svc_display_name_ = DISPLAY_NAME
    
    def __init__(self,args):
        win32serviceutil.ServiceFramework.__init__(self,args)
        self.hWaitStop = win32event.CreateEvent(None,0,0,None)
        socket.setdefaulttimeout(60)
        
        # self.configure_logging()
        self.is_running = True  # 초기화
        # msgr.put_msgr_target("DBADaemon is Started.", grp_cd="DBWX99", send_title=func_tree(), msgr_color="WHITE")

    def configure_logging(self):
        # formatter Setting
        self.formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        
        # handler Setting
        # StreamHandler : Console View
        # FileHandler   : File Write
        # self.handler = logging.StreamHandler()
        
        # with out log lotation
        # self.handler = logging.FileHandler(STDERR_PATH + "/" + ymd + "_" + self._svc_name_ + ".log")
    
        # when restart, not append log file but rename
        if (self._svc_name_+".log") in os.listdir(STDERR_PATH+"/"): 
            os.rename(STDERR_PATH+"/"+self._svc_name_+".log", STDERR_PATH+"/" + NOW.strftime("%Y-%m-%d_%H-%M-%S") +"_" + self._svc_name_ + ".log")

        # with log lotation when="midnight"
        self.handler = logging.handlers.TimedRotatingFileHandler(filename=STDERR_PATH+"/"+self._svc_name_+".log",when="midnight") # when="S" ,interval=5)

        # self.handler = logging.Handler.TimedRotatingFileHandler(filename=STDERR_PATH+"/"+now+"_"+self._svc_name_+".log",when="S",interval=5)
        self.handler.setFormatter(self.formatter)

        # Logging Setting
        # Filemode : a(aapend)
        # Level : NOTSET (0), DEBUG (10), INFO (20), WARNING (30), ERROR (40), CRITICAL (50)
        logging.basicConfig(filemode = "a", level = logging.NOTSET) # ,level = logging.DEBUG
        self.logger = logging.getLogger(LOGGER_NAME)
        # self.logger.setLevel(logging.DEBUG)  
        self.logger.addHandler(self.handler)

        # Logging Write Examples
        # self.logger.debug   ("Debug    Message")
        # self.logger.info    ("Info     Message")
        # self.logger.warn    ("Warn     Message")
        # self.logger.error   ("Error    Message")
        # self.logger.critical("Critical Message")

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        # msgr.put_msgr_target("DBADaemon is Stopped.", grp_cd="DBWX99", send_title=func_tree(), msgr_color="WHITE")
        self.is_running = False

    def SvcDoRun(self):
        # Log that we are starting
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_,""))
        try:
            msgr.put_msgr_target("DBADaemon is Started.", grp_cd="DBWX99", send_title=func_tree(), msgr_color="WHITE", send_funcnm=func_nm())
            self.main()
        except Exception as e:
            # self.logger.error("SvcDoRun: " + str(e))
            # servicemanager.LogErrorMsg(f"Service terminated unexpectedly: {str(e)}")
            msgr.put_msgr_target(file_nm() + f"Service terminated unexpectedly: {str(e)}", grp_cd="DBWX99", send_title=func_tree(), msgr_color="WHITE", send_funcnm=func_nm())

    def main(self):
        global GATHER_DB_INTERVAL
        GATHER_DB_TIME = GATHER_DB_INTERVAL
        self.is_running = True

        # Time Setting
        target_dtm = YMDHH24MISS
        current_dtm = target_dtm
        
        while self.is_running:
            try:
                # DB 에러 읽어오는 배치 (GATHER_DB_TIME 만큼 대기 (초))
                if GATHER_DB_TIME >= GATHER_DB_INTERVAL : 
                    # self.logger.info(" Executed " + target_dtm) # str(datetime.datetime.now())
                    print("before module = " + target_dtm)
                    current_dtm = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    # target_dtm = realtime_err.read_db_errors(target_dtm)
                    realtime_err.read_db_errors(target_dtm)
                    target_dtm = current_dtm
                    print("after module = " + target_dtm)
                    GATHER_DB_TIME = 0
                else : 
                    GATHER_DB_TIME = GATHER_DB_TIME + DAEMON_SLEEP_TIME
                
                # 파일 읽어서 문자로 전송 (DAEMON_SLEEP_TIME 만큼 대기 (초))
                # print(str(datetime.datetime.now()) + " Waiting ")
                # self.logger.info(" Waiting ") # str(datetime.datetime.now())
                time.sleep(DAEMON_SLEEP_TIME)
                
            except Exception as e:
                # self.logger.error("main: " + str(e), exc_info=True) # 추가적인 디버깅 정보를 위해 exc_info=True 옵션을 사용하여 스택 트레이스를 로그에 기록
                msgr.put_msgr_target(file_nm() + " is failed : " + str(e), grp_cd="DBWX99", send_title=func_tree(), msgr_color="WHITE", send_funcnm=func_nm())
                # added 20210907
                # 비정상 종료 시 예외를 발생시켜 로그를 남기고 종료를 유도
                raise # continue


if __name__ == "__main__":
    try:
        win32serviceutil.HandleCommandLine(AppServerSvc)
    except Exception as e:
        msgr.put_msgr_target("DBADaemon is dead : " + str(e), grp_cd="DBWX99", send_title=func_tree(), msgr_color="WHITE", send_funcnm=func_nm())