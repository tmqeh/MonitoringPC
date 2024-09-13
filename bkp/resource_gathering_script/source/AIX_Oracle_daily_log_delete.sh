# filename : log_del_daily.sh
#!/bin/sh
datetime=`TZ=KST-9 date +%Y%m%d`

# Audit File 삭제 (1일)
find /swlog/oracle/admin/LOTTEDEV/adump -name "*.aud" -mtime +1 -exec rm -rf {} \;

# 리스너 관련 이관
mv /sw/oracle_base/diag/tnslsnr/LD-HRDEVDB/listener/trace/listener.log \
   /sw/oracle_base/diag/tnslsnr/LD-HRDEVDB/listener/trace/listener_bk/listener_LOTTEDEV_${datetime}.log

# 리스너 관련 삭제 (15일)
find /sw/oracle_base/diag/tnslsnr/LD-HRDEVDB/listener/trace/listener_bk -name "listener*.log" -mtime +15 -exec rm -rf {} \;

find /sw/oracle_base/diag/tnslsnr/LD-HRDEVDB/listener/alert -name "log*.xml" -mtime +15 -exec rm -rf {} \;
