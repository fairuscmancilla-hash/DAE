@echo off
rem Atajo del laboratorio: usa SIEMPRE el Python del venv (el que tiene Django)
rem y fuerza UTF-8 para que no truenen los signos del duelo en la consola.
rem Uso (desde esta carpeta):
rem   .\dale duel
rem   .\dale duel --source ai
rem   .\dale duel --question q4
rem   .\dale test blog.tests.test_front_page
rem   .\dale test
rem   .\dale shell
rem   .\dale agent --intent "{\"action\": \"posts_per_author\", \"args\": {}}"
rem Borra este archivo antes de entregar si no quieres que viaje en tu repo.
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
"%~dp0.venv\Scripts\python.exe" manage.py %*
