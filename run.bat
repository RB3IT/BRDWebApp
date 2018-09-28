@echo OFF
call getip.cmd
IF NOT "%~1"=="" (set address=%1)
@echo ON
python manage.py runserver %address%