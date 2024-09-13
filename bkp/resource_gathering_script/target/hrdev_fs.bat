@echo off

"C:\Program Files (x86)\WinSCP\WinSCP.com" ^
  /log="F:\gatherLog\winScpLog\!Y!M!D_WinSCP.log" /ini=nul ^
  /command ^
    "open scp://oracle:oracle12%%21%%40@10.44.1.27/ -hostkey=""ssh-ed25519 256 inuUA3yp7lYkv+GZbal7SEdSz8ISw8r9W/Ly4xF5O5c=""" ^
    "get -latest /home/oracle/dba/*.fs.log F:\gatherLog\" ^
    "exit"

set WINSCP_RESULT=%ERRORLEVEL%
if %WINSCP_RESULT% equ 0 (
  echo Success
) else (
  echo Error %WINSCP_RESULT%
)

exit /b %WINSCP_RESULT%