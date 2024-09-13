# filename : mon_tbs.sh
#!/bin/sh
HOSTNM=`hostname`
LOGPATH=/home/oracle/dba

YYYYMMDD=`TZ=KST-9 date +%Y%m%d`
HH=`TZ=KST-9 date +%H`

datetime=`TZ=KST-9 date +%Y%m%d%H`

su - oracle << EOF
sqlplus -s / as sysdba
set colsep ,
set headsep off
set pagesize 0
set linesize 5000
set trimspool on
set feedback off
column TOT_GB  format 999990.99
column FREE_GB format 999990.99
column USE_GB  format 999990.99
column USE_PCT format 999990.99
spool $LOGPATH/${YYYYMMDD}_${HOSTNM}.tbs.log
  SELECT (SELECT NAME FROM v\$DATABASE) DBNAME
       , TO_CHAR (SYSDATE, 'YYYYMMDD') DT
       , TABLESPACE_NAME TBS_NM
       , ROUND (TABLESPACE_SIZE * VALUE / 1024 / 1024 / 1024, 2) TOT_GB
       , ROUND ((TABLESPACE_SIZE - USED_SPACE) * VALUE / 1024 / 1024 / 1024, 2) FREE_GB
       , ROUND (USED_SPACE * VALUE / 1024 / 1024 / 1024, 2) USE_GB
       , ROUND (USED_PERCENT, 2) USE_PCT
    FROM DBA_TABLESPACE_USAGE_METRICS A
       , (SELECT VALUE
            FROM V\$PARAMETER
           WHERE NAME = 'db_block_size') B
   WHERE TABLESPACE_NAME NOT LIKE 'UNDO%'
     AND TABLESPACE_NAME NOT LIKE 'TEMP%'
ORDER BY USE_PCT DESC;
spool off;
EOF