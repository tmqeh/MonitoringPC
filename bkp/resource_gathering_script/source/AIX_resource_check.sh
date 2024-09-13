# filename : mon_rsrc.sh
#!/bin/sh

HOSTNM=`hostname`
LOGPATH=/home/oracle/dba

YYYYMMDD=`TZ=KST-9 date +%Y%m%d`
HH=`TZ=KST-9 date +%H`

datetime=`TZ=KST-9 date +%Y%m%d%H`

# Memory Usage
# MEMORY_PERCENT=`svmon -G |grep memory |perl -ane 'printf"%0.1f \n", 100 - ( ( $F[3] / $F[1] ) * 100 ) '`
MEMINUSE=`svmon -G  | grep "in use" | awk '{print ($3)}'`
MEMCOMP=`svmon -G  | grep "memory" | awk '{print ('$MEMINUSE'/$2*100)}'`
MEMORY_PERCENT=$(printf %.1f $MEMCOMP)

# CPU Usage
#CPU_PERCENT=`top -b -n 1 | grep -i cpu\(s\)| awk -F, '{print $4}' | tr -d "%id," | awk '{print 100-$1}'`
CPU_PERCENT=`sar 1 2|tail -1|awk '{use=int($2+$3)}END{printf "%.0f\n",use}'`

# Disk Usage Count Over 95%
DISK_95_CNT=`df -P | grep -v ^Filesystem | sed 's/%//' | awk 'BEGIN {CNT=0} {$5>95?CNT=CNT+1:CNT=CNT+0} END {print CNT}'`

# Main Proccess Count
PRCS_CNT=`ps -ef | grep XDS | wc -l`

# echo $CPU_PERCENT $MEMORY_PERCENT $DISK_95_CNT
echo $HOSTNM,$YYYYMMDD,$HH,$CPU_PERCENT,$MEMORY_PERCENT,$DISK_95_CNT,$PRCS_CNT > $LOGPATH/${datetime}_${HOSTNM}.rsrc.log
