import subprocess

# common & configuration
from cfg.config_path import BACKUP_DIR, SCHEDULER_FOLDER as FOLDER_PATH
import cmn.common_msgr as msgr
from cmn.common import get_cur_func_nm as func_nm, get_cur_file_nm as file_nm, get_func_tree as func_tree

DETAIL_DIR = "windows_scheduler"
FULL_DIR = BACKUP_DIR + DETAIL_DIR


def export_schduler():
    try:
        # PowerShell 스크립트 작성
        powershell_script = f'''
        $folderPath = "{FOLDER_PATH}"
        $outputPath = "{FULL_DIR}"

        # 지정된 폴더의 작업 스케줄러 가져오기
        $tasks = Get-ScheduledTask -TaskPath $folderPath

        foreach ($task in $tasks) {{
                $xmlPath = Join-Path $outputPath "$($task.TaskName).xml"
                Export-ScheduledTask -TaskPath $folderPath -TaskName $task.TaskName | Out-File -FilePath $xmlPath
            }}


        Write-Host "작업 스케줄러가 $outputPath 폴더에 내보내졌습니다."

        '''

        # PowerShell 스크립트 실행
        subprocess.run(["powershell", powershell_script])

    except Exception as e:
        msgr.put_msgr_target(func_tree() + ":\n" + str(e), grp_cd="DBWX99", send_title="**" + func_nm() + "**", msgr_color="RED", send_funcnm=func_nm())


if __name__ == "__main__":
    try:
        export_schduler()

    except Exception as e:
        msgr.put_msgr_target(str(e), grp_cd="DBWX99", send_title="**" + file_nm() + "**", msgr_color="RED", send_funcnm=func_nm())
