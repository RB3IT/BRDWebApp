@echo OFF
set address="192.168.1.119:8000"
IF NOT "%~1"=="" (set address=%1)
@echo ON
call clearcache.bat
start run.bat %address%
start gotopage.bat %address%