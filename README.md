# Социальная сеть yatube_project
Моя программа для создания сайта YAtube поддерживает авторизацию и безопасную аутентификацию пользователей, а также размещение постов, которые можно редактировать, разделять по группам и комментировать. У каждого пользователя есть возможность подписаться на любимых авторов и следить за их новостями. 
## Технологии
- [Python 3.7](https://www.python.org/downloads/release/python-370/)
- [Django 2.2.19](https://www.djangoproject.com/download/)
## Запуск проекта в dev-режиме на локальном сервере:
Клонировать репозиторий и перейти в директорию с ним:
```
git clone git@github.com:Polina1Kostina/hw05_final.git
```
Cоздать и активировать виртуальное окружение:
```
python3 -m venv env
```
```
source venv/bin/activate
```
Установить зависимости из файла requirements.txt:
```
python3 -m pip install --upgrade pip
```
```
pip install -r requirements.txt
```
Выполнить миграции:
```
cd yatube
```
```
python3 manage.py makemigrations
```
```
python3 manage.py migrate
```
Запустить проект:
```
python3 manage.py runserver
```
Сервер будет доступен по адресу:
```
http://127.0.0.1:8000/
```
## Авторы
[Полина Костина](https://github.com/Polina1Kostina) :eyes:
