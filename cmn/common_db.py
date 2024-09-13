# for Database Connection
import pymssql as mci
import psycopg2 as psy
from psycopg2 import sql as psysql # 외부에서 참조
# import oracledb as cx
import cx_Oracle as cx
import traceback # for Debug

# common & configuration
import cfg.config_db as cnf

# Query 작성시 참고사항
# pymssql : %d, %s 주의
# 예시 : result = conn.query("select %d as test_result, %s test from dual", (3,'abv'))

# psycopg2 : %s로 numeric 데이터도 핸들링 가능
# 예시 : result = conn.query("select %s as test_result, %s test from dual", (3,'abv'))

# cx_Oracle : :B1과 같이 바인드 변수를 사용해야됨
# 예시 : result = conn.query("select :b1 as test_result, :b2 test from dual", (3,'abv'))

# DB Connection 생성 및 실행 참고
# 예시 : conn = monPC() 로 최초 선언
# 사용 : conn.execute, conn.query 등
# 종료 : conn.close()
# 기타 : 단건은 execute 뒤에 commit()을 하고 loop일 경우 close 직전에 1회만 conn.commit() 실행
# 참고 : conn.close vs conn.close()
#        conn.close : 단순히 참조 -> 실행하지 않음
#        conn.close() : 해당 함수를 실행   
#     => 따라서, 모든 함수 실행은 함수명() 로 작성할 것

""" list comprehension 부분 공통 전환 검토 중
    data = conn.query(sql_text)
    result = []
    if conn.rows() > 0:
            result = [dict((conn.description()[i][0], value) \
                            for i, value in enumerate(row)) for row in data]
"""


class maxgDB:

    def __init__(self, appname=None):
        self._conn = psy.connect(host=cnf.DATASOURCE['maxgDB']['host'],
                                 port=cnf.DATASOURCE['maxgDB']['port'],
                                 user=cnf.DATASOURCE['maxgDB']['user'],
                                 password=cnf.DATASOURCE['maxgDB']['password'],
                                 database=cnf.DATASOURCE['maxgDB']['database'],
                                 application_name=appname)
        self._cursor = self._conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @ property
    def connection(self):
        return self._conn

    @ property
    def cursor(self):
        return self._cursor

    def commit(self):
        self.connection.commit()

    def close(self, commit=True):
        if commit:
            self.commit()
        self.connection.close()

    def execute(self, sql, params=None):
        try:
            if params is not None:
                self.cursor.execute(sql, params)
            else:
                self.cursor.execute(sql)

        except Exception as e:
            print(f"Error executing query: {e}")

    def fetchall(self):
        return self.cursor.fetchall()

    def fetchone(self):
        return self.cursor.fetchone()

    def query(self, sql, params=None):
        try:
            if params is not None:
                self.cursor.execute(sql, params)
            else:
                self.cursor.execute(sql)

            return self.fetchall()
        except Exception as e:
            print(f"Error executing query: {e}")

    def rows(self):
        return self.cursor.rowcount
    
    def description(self):
        return self.cursor.description


class monDB:

    def __init__(self, appname=None):
        self._conn = mci.connect(server=cnf.DATASOURCE['monDB']['server'],
                                 port=cnf.DATASOURCE['monDB']['port'],
                                 user=cnf.DATASOURCE['monDB']['user'],
                                 password=cnf.DATASOURCE['monDB']['password'],
                                 database=cnf.DATASOURCE['monDB']['database'],
                                 charset=cnf.DATASOURCE['monDB']['charset'],
                                 appname=appname)
        self._cursor = self._conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @ property
    def connection(self):
        return self._conn

    @ property
    def cursor(self):
        return self._cursor

    def commit(self):
        self.connection.commit()

    def close(self, commit=True):
        if commit:
            self.commit()
        self.connection.close()

    def execute(self, sql, params=None):
        try:
            if params is not None:
                self.cursor.execute(sql, params)
            else:
                self.cursor.execute(sql)

        except Exception as e:
            print(f"Error executing query: {e}")

    def fetchall(self):
        return self.cursor.fetchall()

    def fetchone(self):
        return self.cursor.fetchone()

    def query(self, sql, params=None):
        try:
            if params is not None:
                self.cursor.execute(sql, params)
            else:
                self.cursor.execute(sql)

            return self.fetchall()
        except Exception as e:
            print(f"Error executing query: {e}")

    def rows(self):
        return self.cursor.rowcount

    def description(self):
        return self.cursor.description


class workDB:

    def __init__(self, appname=None):
        self._conn = mci.connect(server=cnf.DATASOURCE['workDB']['server'],
                                 port=cnf.DATASOURCE['workDB']['port'],
                                 user=cnf.DATASOURCE['workDB']['user'],
                                 password=cnf.DATASOURCE['workDB']['password'],
                                 database=cnf.DATASOURCE['workDB']['database'],
                                 charset=cnf.DATASOURCE['workDB']['charset'],
                                 appname=appname)
        self._cursor = self._conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @ property
    def connection(self):
        return self._conn

    @ property
    def cursor(self):
        return self._cursor

    def commit(self):
        self.connection.commit()

    def close(self, commit=True):
        if commit:
            self.commit()
        self.connection.close()

    def execute(self, sql, params=None):
        try:
            if params is not None:
                self.cursor.execute(sql, params)
            else:
                self.cursor.execute(sql)

        except Exception as e:
            print(f"Error executing query: {e}")

    def fetchall(self):
        return self.cursor.fetchall()

    def fetchone(self):
        return self.cursor.fetchone()

    def query(self, sql, params=None):
        try:
            if params is not None:
                self.cursor.execute(sql, params)
            else:
                self.cursor.execute(sql)

            return self.fetchall()
        except Exception as e:
            print(f"Error executing query: {e}")

    def rows(self):
        return self.cursor.rowcount
    
    def description(self):
        return self.cursor.description


class monPC:

    def __init__(self, appname=None):
        self._conn = mci.connect(server=cnf.DATASOURCE['monPC']['server'],
                                 port=cnf.DATASOURCE['monPC']['port'],
                                 user=cnf.DATASOURCE['monPC']['user'],
                                 password=cnf.DATASOURCE['monPC']['password'],
                                 database=cnf.DATASOURCE['monPC']['database'],
                                 charset=cnf.DATASOURCE['monPC']['charset'],
                                 appname=appname)
        self._cursor = self._conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @ property
    def connection(self):
        return self._conn

    @ property
    def cursor(self):
        return self._cursor

    def commit(self):
        self.connection.commit()

    def close(self, commit=True):
        if commit:
            self.commit()
        self.connection.close()

    def execute(self, sql, params=None):
        # try:
        if params is not None:
            self.cursor.execute(sql, params)
        else:
            self.cursor.execute(sql)

        # except Exception as e:
        #     print(f"Error executing query: {e}")

    def fetchall(self):
        return self.cursor.fetchall()

    def fetchone(self):
        return self.cursor.fetchone()

    def query(self, sql, params=None):
        # try:
        if params is not None:
            self.cursor.execute(sql, params)
        else:
            self.cursor.execute(sql)

        return self.fetchall()
        # except Exception as e:
        #     print(f"Error executing query: {e}")

    def rows(self):
        return self.cursor.rowcount
    
    def description(self):
        return self.cursor.description


class batDB:

    def __init__(self, appname=None):
        self._conn = cx.connect(dsn=cnf.DATASOURCE['batDB']['server'] + ':' +
                                cnf.DATASOURCE['batDB']['port'] + '/' +
                                cnf.DATASOURCE['batDB']['database'],
                                user=cnf.DATASOURCE['batDB']['user'],
                                password=cnf.DATASOURCE['batDB']['password'],
                                encoding='UTF-8')
        if appname is not None:
            self._conn.module = appname
        self._cursor = self._conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @ property
    def connection(self):
        return self._conn

    @ property
    def cursor(self):
        return self._cursor

    def commit(self):
        self.connection.commit()

    def close(self, commit=True):
        if commit:
            self.commit()
        self.connection.close()

    def execute(self, sql, params=None):
        try:
            if params is not None:
                self.cursor.execute(sql, params)
            else:
                self.cursor.execute(sql)

        except Exception as e:
            print(f"Error executing query: {e}")

    def fetchall(self):
        return self.cursor.fetchall()

    def fetchone(self):
        return self.cursor.fetchone()

    def query(self, sql, params=None):
        try:
            if params is not None:
                self.cursor.execute(sql, params)
            else:
                self.cursor.execute(sql)

            return self.fetchall()
        except Exception as e:
            print(f"Error executing query: {e}")

    def rows(self):
        return self.cursor.rowcount
    
    def description(self):
        return self.cursor.description


class metaDB:

    def __init__(self, appname=None):
        self._conn = cx.connect(dsn=cnf.DATASOURCE['metaDB']['server'] + ':' +
                                cnf.DATASOURCE['metaDB']['port'] + '/' +
                                cnf.DATASOURCE['metaDB']['database'],
                                user=cnf.DATASOURCE['metaDB']['user'],
                                password=cnf.DATASOURCE['metaDB']['password'],
                                encoding='UTF-8')
        if appname is not None:
            self._conn.module = appname
        self._cursor = self._conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @ property
    def connection(self):
        return self._conn

    @ property
    def cursor(self):
        return self._cursor

    def commit(self):
        self.connection.commit()

    def close(self, commit=True):
        if commit:
            self.commit()
        self.connection.close()

    def execute(self, sql, params=None):
        try:
            if params is not None:
                self.cursor.execute(sql, params)
            else:
                self.cursor.execute(sql)

        except Exception as e:
            print(f"Error executing query: {e}")

    def fetchall(self):
        return self.cursor.fetchall()

    def fetchone(self):
        return self.cursor.fetchone()

    def query(self, sql, params=None):
        try:
            if params is not None:
                self.cursor.execute(sql, params)
            else:
                self.cursor.execute(sql)

            return self.fetchall()
        except Exception as e:
            print(f"Error executing query: {e}")

    def rows(self):
        return self.cursor.rowcount
    
    def description(self):
        return self.cursor.description