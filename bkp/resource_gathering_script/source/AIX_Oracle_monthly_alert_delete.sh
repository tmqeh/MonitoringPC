# filename : log_mov_monthly.sh
#!/bin/sh
datetime=`TZ=KST-9 date +%Y%m%d`

mv /swlog/oracle/diag/rdbms/lottedev/LOTTEDEV/trace/alert_LOTTEDEV.log \
   /swlog/oracle/diag/rdbms/lottedev/LOTTEDEV/trace/alert_bk/alert_LOTTEDEV_${datetime}.log
