@echo OFF
call getip.cmd
IF NOT "%~1"=="" (set address=%1)
@echo ON
start run.bat %address%
start gotopage.bat %address%