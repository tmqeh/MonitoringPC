FORFILES /P F:\gatherLog /M *.log /D -1 /C "cmd /c move @file F:\gatherLog\old"
FORFILES /P F:\gatherLog\winScpLog /M *.log /D -1 /C "cmd /c move @file F:\gatherLog\old"
FORFILES /P F:\gatherLog\old /M *.log /D -45 /C "cmd /c del @file"