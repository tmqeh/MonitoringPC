# filename : mon_ora_alert.sh
#!/bin/sh
HOSTNM=`hostname`
LOGPATH=/home/oracle/dba

YYYYMMDD=`TZ=KST-9 date +%Y%m%d`
HH=`TZ=KST-9 date +%H`

datetime=`TZ=KST-9 date +%Y%m%d%H`

su - oracle << EOF
sqlplus -s / as sysdba
set colsep ";"
set headsep off
set pagesize 0
set linesize 5000
set trimspool on
set feedback off
spool $LOGPATH/${YYYYMMDD}_${HOSTNM}.ora.alert.log
SELECT TO_CHAR(ORIGINATING_TIMESTAMP,'YYYYMMDD') DT
     , TO_CHAR(ORIGINATING_TIMESTAMP,'HH24') HH
     , ROW_NUMBER() OVER (PARTITION BY TO_CHAR(ORIGINATING_TIMESTAMP,'YYYYMMDD'), TO_CHAR(ORIGINATING_TIMESTAMP,'HH24') ORDER BY INDX) SEQ
     , HOST_ID, HOST_ADDRESS
     , REPLACE(REPLACE(REPLACE(MESSAGE_TEXT,CHR(10),''),CHR(13),''),CHR(9),'') MESSAGE_TEXT
     , MODULE_ID, PROBLEM_KEY, DETAILED_LOCATION, TO_CHAR(ORIGINATING_TIMESTAMP,'YYYYMMDDHH24MISS') ORIGINATING_TIMESTAMP
  FROM X\$DBGALERTEXT A
 WHERE 1=1
   AND MESSAGE_TEXT NOT LIKE '%KILL SESSION%'                                                                        
   AND MESSAGE_TEXT NOT LIKE '%aborting process unknown ospid%'
   AND MESSAGE_TEXT NOT LIKE '%ORA-01013%'
   AND MESSAGE_TEXT NOT LIKE '%SQL Analyze time limit interrupt%'
   AND MESSAGE_TEXT NOT LIKE '%Archived Log entry % added for thread % sequence % ID %'
   AND MESSAGE_TEXT NOT LIKE '%Thread % advanced to log sequence % (LGWR switch)%'
   AND MESSAGE_TEXT NOT LIKE '%Current log# % seq# % mem# %'
   AND MESSAGE_TEXT     LIKE '%ORA-%'
   AND NVL(MESSAGE_GROUP,'Nothing') <> 'startup'
   AND TO_CHAR(ORIGINATING_TIMESTAMP,'YYYYMMDD') > TO_CHAR(SYSDATE -1,'YYYYMMDD')
   ORDER BY 1,2,INDX;
spool off;
EOF

