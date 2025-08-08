@echo off
echo === DEMARRAGE DES SERVEURS ===

echo.
echo 1. Demarrage du serveur Django...
start "Django Server" cmd /k "cd /d %~dp0 && env\Scripts\activate && python manage.py runserver"

echo.
echo 2. Attente de 3 secondes...
timeout /t 3 /nobreak >nul

echo.
echo 3. Demarrage du serveur Vue.js...
start "Vue.js Server" cmd /k "cd /d %~dp0\frontend && set NODE_NO_WARNINGS=1 && set NODE_OPTIONS=--no-deprecation && npm run dev"

echo.
echo === SERVEURS DEMARRES ===
echo Django: http://localhost:8000
echo Vue.js: http://localhost:3000
echo.
echo Appuyez sur une touche pour fermer cette fenetre...
pause >nul