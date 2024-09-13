SET YYYY=%date:~0,4%

@REM FORFILES /P C:\rdslog\%YYYY% /S /M *.log /D -1 /C "cmd /c move @file C:\rdslog\old"
@REM FORFILES /P C:\rdslog\old /M *.log /D -15 /C "cmd /c del @file"
@REM retention of daily report image
FORFILES /P C:\dbapgm\report\daily /M *.jpg /D -45 /C "cmd /c del @file"

@REM retention of daemon log file
FORFILES /P C:\dbapgm\log\daemon /M *.log /D -45 /C "cmd /c del @file"

@REM retention of SE log file
FORFILES /P E:\se_daily_report\old /M *.log /D -45 /C "cmd /c del @file"

@REM retention of monthly report folder
FORFILES /P "C:\dbapgm\report\monthly" /S /D -370 /C "cmd /c @rmdir /s /q @path"

