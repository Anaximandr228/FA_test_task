# Тестовое задание


## Для запуска приложения:
1. Для создания контейнера введите команду ``docker compose build``
2. Для запуска контейнера введите команду ``docker compose up``

## Для просмотра документации перейдите вызовите http://localhost:8000/docs#/

## Для проверки эндпоинтов:
1. Вызовите метод POST "/register" и передайте в него имя пользователя и пароль
<br>Curl:
>curl -X 'POST' \
  'http://localhost:8000/register' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "username": "Admin",
  "password": "password"
}'
>
<br>Формат тела JSON:
>{
  "username": "Admin",
  "password": "password"
}
2. Вызовите метод POST "/tasks/" и передайте в него данные заметки
<br>Curl:
>curl -X 'POST' \
  'http://localhost:8000/tasks/' \
  -H 'accept: application/json' \
  -H 'Authorization: Basic Z3Jva2U6MTExMTE=' \
  -H 'Content-Type: application/json' \
  -d '{
  "title": "string",
  "description": "string",
  "status": "pending"
}'
>
<br>Формат тела JSON:
>{
  "title": "string",
  "description": "string",
  "status": "pending"
}
> 
3. Вызовите метод GET "tasks/?status=?&skip=?&limit=?" для просмотра добавленных задач (заполните вопросительные знаки на нужные параметы)
<br>Curl:
>curl -X 'GET' \
  'http://localhost:8000/tasks/?status=done&skip=0&limit=100' \
  -H 'accept: application/json' \
  -H 'Authorization: Basic Z3Jva2U6MTExMTE='
>

4. Вызовите метод PUT "/tasks/{id}" для редактирования задачи по его id
<br>Curl:
>curl -X 'PUT' \
  'http://localhost:8000/tasks/1' \
  -H 'accept: application/json' \
  -H 'Authorization: Basic Z3Jva2U6MTExMTE=' \
  -H 'Content-Type: application/json' \
  -d '{
  "title": "string",
  "description": "string",
  "status": "done"
}'
>
<br>Формат тела JSON:
>{
  "title": "string",
  "description": "string",
  "status": "done"
}
> 
6. Вызовите метод DELETE "/tasks/{id}" для удаления задачи
<br>Curl:
>curl -X 'DELETE' \
  'http://localhost:8000/tasks/1' \
  -H 'accept: */*' \
  -H 'Authorization: Basic Z3Jva2U6MTExMTE='
>
