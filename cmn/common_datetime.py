
import datetime # for File Prefix
from dateutil.relativedelta import relativedelta

# date format lists
NOW         = datetime.datetime.now()
YYYY        = NOW.strftime("%Y")
YM          = NOW.strftime("%Y%m")
YMD         = NOW.strftime("%Y%m%d")
HMS         = NOW.strftime("%H%M%S")
YMDHMS      = NOW.strftime("%Y%m%d%H%M%S")
MM          = NOW.strftime("%m")
YMDHH       = NOW.strftime("%Y-%m-%d %H")
YMDHH24MI   = NOW.strftime("%Y-%m-%d %H:%M")
YMDHH24MISS = NOW.strftime("%Y-%m-%d %H:%M:%S")

YESTERDAY = (datetime.date.today() - datetime.timedelta(days=1))
YESTERDAY_YMDHH24MISS = YESTERDAY.strftime("%Y-%m-%d %H:%M:%S")

NETBACKUP_YMD = NOW.strftime("%Y-%m-%d")

# monthly report
TIME_YM       = (datetime.datetime.now() - relativedelta(months=1)).strftime("%Y%m")
YESTERDAY_YMD = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y%m%d")
GRAFANA_TIME  = NOW.strftime("%d/%m/%Y %H:%M:%S")

# utc Date Setting (for AWS)
NOW_UTC     = datetime.datetime.utcnow()
PRE_NOW_UTC = NOW_UTC - datetime.timedelta(seconds=60)


def check_weekday():
    # 0은 월요일, 1은 화요일, 2는 수요일, 3은 목요일, 4는 금요일 ,5는 토요일 ,6은 일요일
    return NOW.weekday()