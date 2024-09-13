import os

# common & configuration
from cfg.config_path import BACKUP_DIR
import cmn.common_msgr as msgr
from cmn.common import get_cur_func_nm as func_nm, get_cur_file_nm as file_nm, get_func_tree as func_tree
from cmn.common_db import monPC, monDB
from cmn.common_file import check_dir

DETAIL_DIR = "resource_gathering_script/DB"
FULL_DIR = BACKUP_DIR + DETAIL_DIR
TARGET_LIST = ['monDB','monPC']


def get_mssql_procedure(args):
    try:
        # DB 기본 접속 정보
        if args == 'monPC':
            conn = monPC()
        elif args == 'monDB':
            conn = monDB()
        else:
            raise Exception('접속 할 수 없는 DB입니다.')

        sqlTxt = ""

        # SQL 호출
        sqlTxt = """/* Procedure Backup Script */
                    SELECT @@SERVERNAME as SERVER_NAME, o.name as OBJECT_NAME, p.definition
                         , case o.type when 'P' then 'sp' when 'FN' then 'fn' else null end as extension
                      FROM sys.sql_modules p
                     INNER JOIN sys.objects o ON p.object_id = o.object_id    
                     INNER JOIN sys.schemas s ON o.schema_id = s.schema_id    
                     WHERE o.name NOT LIKE 'USP2%'
                       AND UPPER(p.[definition]) LIKE UPPER('%dbo%'); -- Use your schema here
                 """

        # print(sqlTxt)
        data = conn.query(sqlTxt)
        result = []
        # DBA_logging_info(sqlTxt, 'get_mssql_procedure')
        if conn.rows() > 0:
            result = [dict((conn.description()[i][0], value) \
                            for i, value in enumerate(row)) for row in data]

            return result

    except Exception as e:
        # print("get_mssql_procedure except : " + str(e))
        msgr.put_msgr_target(func_tree() + ":\n" + str(e), grp_cd="DB9993", send_title="**" + func_nm() + "**", msgr_color="RED")

    finally:
        conn.close()


if __name__ == "__main__":
    try:
        for target in TARGET_LIST:
            procedure_text = get_mssql_procedure(target)
            # print(procedure_text)
            for source_script in procedure_text:
                # path = os.path.join(FULL_DIR, source_script['OBJECT_NAME'])
                path = os.path.join(FULL_DIR, source_script['SERVER_NAME'])
                
                file_name = path + '/' + source_script['OBJECT_NAME'] + '.' + source_script['extension']
                check_dir(path)
                    
                with open(file_name, 'w', encoding='utf-8') as f:
                    f.write (source_script['definition'])
                    f.close()

    except Exception as e:
        msgr.put_msgr_target(str(e), grp_cd="DB9993", send_title="**" + file_nm() + "**", msgr_color="RED")
