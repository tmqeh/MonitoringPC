@echo off

"C:\Program Files (x86)\WinSCP\WinSCP.com" ^
  /log="F:\gatherLog\winScpLog\!Y!M!D_WinSCP.log" /ini=nul ^
  /command ^
    "open sftp://oracle:oracle34%%23%%24@10.7.20.2/ -hostkey=""ssh-ed25519 256 inuUA3yp7lYkv+GZbal7SEdSz8ISw8r9W/Ly4xF5O5c=""" ^
    "get -latest /orawork/dba/*.dr_sync.log F:\gatherLog\" ^
    "get -latest /orawork/dba/*.bcv_copy.log F:\gatherLog\" ^
    "exit"

set WINSCP_RESULT=%ERRORLEVEL%
if %WINSCP_RESULT% equ 0 (
  echo Success
) else (
  echo Error %WINSCP_RESULT%
)

exit /b %WINSCP_RESULT%