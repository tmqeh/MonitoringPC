# filename : mon_dr_chk.sh
#!/bin/sh
export PATH=$PATH:/sw/grid/crs/bin:/usr/symcli/bin

HOSTNM=`hostname`
LOGPATH=/orawork/dba

YYYYMMDD=`TZ=KST-9 date +%Y%m%d`
HH=`TZ=KST-9 date +%H`

datetime=`TZ=KST-9 date +%Y%m%d%H%M`

# SRDF
symrdf -g LPSISDB que > $LOGPATH/${YYYYMMDD}_${HOSTNM}.dr_sync.temp.log;
#sed -e "s/'//g" $LOGPATH/${YYYYMMDD}_${HOSTNM}.dr_sync.temp.log | xargs -I{} date '+%Y%m%d {}'  > $LOGPATH/${YYYYMMDD}_${HOSTNM}.dr_sync.log
sed -e "s/'//g" $LOGPATH/${YYYYMMDD}_${HOSTNM}.dr_sync.temp.log > $LOGPATH/${YYYYMMDD}_${HOSTNM}.dr_sync.log

# BCV2
#sed -e "s/'//g" /admin/bcv_script/LOG/`date +%Y%m%d`*_BCV.log | xargs -I{} date '+%Y%m%d {}' > $LOGPATH/${YYYYMMDD}_${HOSTNM}.bcv_copy.log
sed -e "s/'//g" /admin/bcv_script/LOG/`date +%Y%m%d`*_BCV.log > $LOGPATH/${YYYYMMDD}_${HOSTNM}.bcv_copy.log
