import anthropic

# common & configuration
from cmn.common_db import monDB
from cmn.common_datetime import YMD, YMDHH24MISS, YESTERDAY_YMDHH24MISS
from cmn.common import get_cur_file_nm as file_nm


INSTANCE_IDS = "(2, 4, 5, 6, 7, 8, 11, 12, 13, 15, 16, 21, 24, 27, 39, 48, 50, 51, 52, 53, 54, 55, 56, 57, 79)"


def query_agent_job_failures(conn, collect_from, run_from):
    sql = """
        SELECT A.InstanceID, A.ServerName
             , B.JobName
             , B.LastRunDateTime
             , B.LastRunStatusMessage
             , B.NextRunDateTime, B.CollectDate
          FROM META2_M_InstanceInfo AS A with (nolock)
         CROSS APPLY (SELECT B.JobName
                           , B.LastRunDateTime
                           , B.LastRunStatusMessage
                           , B.NextRunDateTime, B.CollectDate
                        FROM (SELECT ROW_NUMBER()OVER(PARTITION BY B.LastRunDateTime ORDER BY CollectDate ASC) AS ROWNUM
                                   , B.JobName
                                   , B.LastRunDateTime
                                   , B.LastRunStatusMessage
                                   , B.NextRunDateTime, B.CollectDate
                                FROM [dbo].[TBL2_M_AgentJobInfo] AS B with (nolock)
                               WHERE A.InstanceID = B.InstanceID
                                 AND B.CollectDate  >= '{collect_from}'
                                 AND B.LastRunDateTime  >= '{run_from}'
                                 AND B.Enabled = 'Y'
                                 AND B.LastRunStatus in ('Failed','Warning')
                             ) B
                        WHERE B.ROWNUM = 1
                       ) B
         WHERE A.UseYN = 'Y'
           AND A.InstanceID IN {instance_ids}
           AND A.InstanceID <> 1
           AND B.JobName not like '%SQLServerMonitor%'
           AND B.CollectDate >= '{collect_from}'
    """.format(collect_from=collect_from, run_from=run_from, instance_ids=INSTANCE_IDS)

    data = conn.query(sql)
    if conn.rows() > 0:
        return [dict((conn.description()[i][0], value) for i, value in enumerate(row)) for row in data]
    return []


def query_sql_errorlog(conn, collect_from):
    sql = """
        SELECT distinct A.InstanceID, A.ServerName
            , dateadd(millisecond, -datepart(millisecond, B.CollectDate), B.CollectDate) as CollectDate
            , dateadd(millisecond, -datepart(millisecond, B.LOG_DATE), B.LOG_DATE) as LOG_DATE
            , B.PROCESS_INFO, B.ERRORLOG_TEXT
        FROM [META2_M_InstanceInfo] AS A with (nolock)
        INNER JOIN [dbo].[TBL2_M_SqlErrorlog] AS B with (nolock)
            ON A.InstanceID = B.InstanceID
        WHERE CollectDate >= '{collect_from}'
            AND PROCESS_INFO NOT IN ('Logon', '로그온', 'Backup', '백업')
            AND (ERRORLOG_TEXT LIKE '%error%' OR ERRORLOG_TEXT LIKE '%failed%')
            AND (ERRORLOG_TEXT NOT LIKE '%Logging SQL Server messages in file%'
            AND ERRORLOG_TEXT NOT LIKE '%The error log has been reinitialized. See the previous log for older entries.%'
            AND ERRORLOG_TEXT NOT LIKE 'Attempting to cycle%')
            AND A.InstanceID IN {instance_ids}
        ORDER BY A.InstanceID, LOG_DATE DESC
    """.format(collect_from=collect_from, instance_ids=INSTANCE_IDS)

    data = conn.query(sql)
    if conn.rows() > 0:
        return [dict((conn.description()[i][0], value) for i, value in enumerate(row)) for row in data]
    return []


def query_mssql_locks(conn, collect_from):
    sql = """
        SELECT Z.[수집시간], Z.[시스템명], Z.[락지속시간(s)], Z.[인스턴스ID]
             , X.[타입], X.[대기정보], X.[오브젝트명], X.[시작시간], X.[호스트명]
             , X.[SQL_TEXT]
          FROM (SELECT [수집시간], [시스템명], [락지속시간(s)], [인스턴스ID]
                  FROM (SELECT CLCT_DTM [수집시간]
                              , JOB_NM [시스템명]
                              , ROUND(BLK_TM/1000,0) [락지속시간(s)]
                              , INST_ID [인스턴스ID]
                              , ROW_NUMBER() OVER(PARTITION BY JOB_NM ORDER BY CLCT_DTM DESC) RNUM
                          FROM TB_DAILYREPORT_S with (nolock)
                          WHERE CLCT_DTM >= '{collect_from}'
                          AND INST_ID IN {instance_ids}
                          AND BLK_TM > 60000
                          ) Z
                  WHERE RNUM = 1
              ) Z
          LEFT JOIN (SELECT DISTINCT
                              A.INSTANCEID AS [인스턴스ID], A.COLLECTDATE AS [수집시간]
                          , N'BLOCKED' + ' (' + CONVERT(VARCHAR,SESSION_ID) + ' by ' + CONVERT(VARCHAR,A.BLOCKING_SESSION_ID) + ')' AS [타입]
                          , REPLACE(REPLACE(REPLACE(REPLACE(WAIT_INFO,CHAR(9),' '),' ','<>'),'><',''),'<>',' ') AS [대기정보]
                          , OBJECTNAME AS [오브젝트명]
                          , TRAN_START_TIME AS [시작시간]
                          , HOST_NAME AS [호스트명]
                          , SUBSTRING(REPLACE(REPLACE(REPLACE(REPLACE(SQL_TEXT,CHAR(9),' '),' ','<>'),'><',''),'<>',' '),1,200) AS [SQL_TEXT]
                          , ROW_NUMBER() OVER (PARTITION BY A.INSTANCEID ORDER BY A.COLLECTDATE DESC) AS RNUM
                      FROM [DBO].[TBL2_M_WHOISACTIVE] A WITH(NOLOCK)
                      WHERE 1=1
                          AND A.COLLECTDATE >= '{collect_from}'
                          AND BLOCKING_SESSION_ID <> 0
                      ) X
                  ON Z.[인스턴스ID] = X.[인스턴스ID]
                 AND X.RNUM = 1
    """.format(collect_from=collect_from, instance_ids=INSTANCE_IDS)

    data = conn.query(sql)
    if conn.rows() > 0:
        return [dict((conn.description()[i][0], value) for i, value in enumerate(row)) for row in data]
    return []


def format_monitoring_data(job_failures, sql_errors, locks):
    sections = []

    if job_failures:
        lines = ["## MSSQL Agent Job 실패 목록"]
        for row in job_failures:
            lines.append(
                f"- [{row['InstanceID']}] {row['ServerName']} | Job: {row['JobName']} | "
                f"실행시간: {row['LastRunDateTime']} | 메시지: {row['LastRunStatusMessage']}"
            )
        sections.append("\n".join(lines))
    else:
        sections.append("## MSSQL Agent Job 실패 목록\n- 해당 없음")

    if sql_errors:
        lines = ["## SQL Server Error Log 목록"]
        for row in sql_errors[:50]:  # limit to avoid token overrun
            lines.append(
                f"- [{row['InstanceID']}] {row['ServerName']} | 수집: {row['CollectDate']} | "
                f"로그일시: {row['LOG_DATE']} | 프로세스: {row['PROCESS_INFO']} | {row['ERRORLOG_TEXT']}"
            )
        sections.append("\n".join(lines))
    else:
        sections.append("## SQL Server Error Log 목록\n- 해당 없음")

    if locks:
        lines = ["## MSSQL Lock 발생 현황"]
        for row in locks:
            lines.append(
                f"- [{row['인스턴스ID']}] {row['시스템명']} | 지속시간: {row['락지속시간(s)']}초 | "
                f"타입: {row.get('타입', 'N/A')} | 오브젝트: {row.get('오브젝트명', 'N/A')} | "
                f"SQL: {row.get('SQL_TEXT', 'N/A')}"
            )
        sections.append("\n".join(lines))
    else:
        sections.append("## MSSQL Lock 발생 현황\n- 해당 없음")

    return "\n\n".join(sections)


def analyze_with_claude(monitoring_text, date_label):
    client = anthropic.Anthropic()

    prompt = f"""다음은 {date_label} 기준 MSSQL DB 모니터링 결과입니다.
각 항목을 분석하여 다음 내용을 한국어로 답변해주세요:

1. **전체 요약**: 오늘 발생한 주요 이슈 요약
2. **Agent Job 실패 분석**: 실패한 Job의 심각도와 원인 추정
3. **SQL Error Log 분석**: 에러 패턴 및 반복 여부, 주요 에러 설명
4. **Lock 발생 분석**: Lock이 발생한 서버와 SQL 분석, 영향도 평가
5. **조치 권고사항**: DBA가 즉시 확인해야 할 항목 및 우선순위

---
{monitoring_text}
"""

    print("Claude API 분석 중...")
    result_text = ""
    with client.messages.stream(
        model="claude-opus-4-8",
        max_tokens=4096,
        thinking={"type": "adaptive"},
        messages=[{"role": "user", "content": prompt}]
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
            result_text += text

    print()
    return result_text


if __name__ == "__main__":
    conn = None
    try:
        collect_from = YMDHH24MISS
        run_from = YESTERDAY_YMDHH24MISS
        date_label = YMD

        print(f"[{date_label}] 모니터링 데이터 수집 중...")
        conn = monDB()

        job_failures = query_agent_job_failures(conn, collect_from, run_from)
        print(f"  Agent Job 실패: {len(job_failures)}건")

        sql_errors = query_sql_errorlog(conn, collect_from)
        print(f"  SQL Error Log: {len(sql_errors)}건")

        locks = query_mssql_locks(conn, collect_from)
        print(f"  Lock 발생: {len(locks)}건")

        monitoring_text = format_monitoring_data(job_failures, sql_errors, locks)

        print("\n" + "="*60)
        print(f"[Claude 분석 결과 - {date_label}]")
        print("="*60 + "\n")

        analyze_with_claude(monitoring_text, date_label)

    except Exception as e:
        print(f"[ERROR] {file_nm()}: {e}")
        raise
    finally:
        if conn:
            conn.close()
