# filename : mon_fs.sh
#!/bin/sh
HOSTNM=`hostname`
LOGPATH=/home/oracle/dba

YYYYMMDD=`TZ=KST-9 date +%Y%m%d`
HH=`TZ=KST-9 date +%H`

datetime=`TZ=KST-9 date +%Y%m%d%H`

# FileSystem Usage
DISK_USAGE=`df -g | grep -v "^Filesystem" | grep -v "^/proc" | awk '{gsub("%","");print $7 "," $4}'`

# echo FileSystem Usage
for disk_usage in $DISK_USAGE
do
echo $HOSTNM,$YYYYMMDD,$disk_usage >> $LOGPATH/${YYYYMMDD}_${HOSTNM}.fs.log
done
