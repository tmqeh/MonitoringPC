@echo off
REM SET YYYY=%date:~0,4%

REM DO NOT USE KOREAN in REM(Cause errors)

REM Purpose :
REM Sometimes the daemon does not working on RUNNING stauts
REM and could not find cause why the daemon hang

REM 20221104 Add loop timeout1 for stop command does not work
REM 20230504 set DBADaemon into SERVICE_NAME
REM 20230504 set WAIT_TIME for waiting

set SERVICE_NAME=DBADaemon
set WAIT_TIME=120

REM Stop the service
sc stop %SERVICE_NAME%

REM Wait until the service status is STOPPED
:wait_stop
sc query %SERVICE_NAME% | find "STOPPED" && (
  echo %SERVICE_NAME% service has been stopped successfully.
  goto start_service
)

REM Get the process id (PID) of the service
for /f "tokens=3" %%a in ('sc queryex %SERVICE_NAME% ^| find "PID"') do set PID=%%a

REM If the service is not stopped within the specified time, kill the process
set /a WAIT_TIME-=1
if %WAIT_TIME%==0 (
  echo %SERVICE_NAME% service has not stopped within the specified time. Killing the process...
  echo %PID%
  taskkill /pid %PID% /f
  goto start_service
)

REM Wait for a second and check the service status again
timeout /t 1 > nul
goto wait_stop

:start_service
REM Start the service
sc start %SERVICE_NAME%
echo %SERVICE_NAME% service has been started successfully.