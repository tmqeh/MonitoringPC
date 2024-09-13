# filename : mon_dr_chk.sh
#!/bin/sh

HOSTNM=`hostname`
LOGPATH=/orawork/dba

YYYYMMDD=`TZ=KST-9 date +%Y%m%d`
HH=`TZ=KST-9 date +%H`

datetime=`TZ=KST-9 date +%Y%m%d%H`

# SRDF
#sh /HORCM/script/UR/HRDB/00.UR_HRDB_display.sh | xargs -I{} date '+%Y%m%d {}' > $LOGPATH/${YYYYMMDD}_${HOSTNM}.dr_sync.log
sh /HORCM/script/UR/HRDB/00.UR_HRDB_display.sh > $LOGPATH/${YYYYMMDD}_${HOSTNM}.dr_sync.log


# BCV2
#cat /HORCM/script/SI/log/`date +%Y%m%d`*_script.log | xargs -I{} date '+%Y%m%d {}' > $LOGPATH/${YYYYMMDD}_${HOSTNM}.bcv_copy.log
cat /HORCM/script/SI/log/`date +%Y%m%d`*_script.log > $LOGPATH/${YYYYMMDD}_${HOSTNM}.bcv_copy.log
