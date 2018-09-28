python manage.py makemigrations
@echo off
set /p correct="Was migration successful? (y/n)"
@echo on
IF %correct%=="y"(
	@echo off	
	python manage.py migrate
	set /p correct="Press Enter to Continue"
	@echo on
)