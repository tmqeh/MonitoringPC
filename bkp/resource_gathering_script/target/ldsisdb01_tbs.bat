@echo off

"C:\Program Files (x86)\WinSCP\WinSCP.com" ^
  /log="F:\gatherLog\winScpLog\!Y!M!D_WinSCP.log" /ini=nul ^
  /command ^
    "open scp://oracle:oracle12%%21%%40@10.7.17.151/ -hostkey=""ssh-rsa 2048 QaL8XkufYRzEgElqLBypQ73BMzViIIKpNHkvvgXiWaw=""" ^
    "get -latest /sw/oracle/home/dba/*.tbs.log F:\gatherLog\" ^
    "exit"

set WINSCP_RESULT=%ERRORLEVEL%
if %WINSCP_RESULT% equ 0 (
  echo Success
) else (
  echo Error %WINSCP_RESULT%
)

exit /b %WINSCP_RESULT%