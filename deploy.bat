@echo off
echo Accès au répertoire du projet Django...

REM  Mets ici le chemin EXACT de ton projet
cd /d C:\Users\KABORE\Downloads\ecole-main

echo Activation de l'environnement virtuel...
call venv\Scripts\activate

echo Application des migrations...
python manage.py migrate

echo Collecte des fichiers statiques...
python manage.py collectstatic --noinput

echo Lancement du serveur Django...
python manage.py runserver

pause
