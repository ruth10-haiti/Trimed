@echo off
echo Demarrage du serveur Trimed Backend...
cd /d "%~dp0"
python manage.py runserver 0.0.0.0:8000
pause