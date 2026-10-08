# Отчёт

## 1. Описание приложения
Просто flask приложение для создания заметок

## 2. Версии инструментов
[есть список](пруфы_трудов/versions-before.txt)

## 3. Конфигурация Compose
Конфигурация готова и работает. 
Можно в файле глянуть: [link](пруфы_трудов/compose-config.redacted.txt)

## 4. Запуск и проверка приложения
Мою VM в облаке не смогла запустить :( видимо ввели ограничения понятно из-за чего
![печаль](image-1.png)

Поэтому запускаю локально пока
![прога](image-2.png)

Вот healthcheck ещё
![alt text](image.png)

## 5. Сохранность PostgreSQL при замене контейнера
Создала контрольную заметку, потом заменила контейнер, заметка осталась той же. Т.к. именованный volume остался и новая бд использует прежние данные.
![alt text](image-4.png)

## 6. Холодный backup и восстановление
volume:
![alt text](image-6.png)

Остановила стек:
![alt text](image-7.png)

Создала архив через временный контейнер и удалила volume:
![alt text](image-8.png)

Создала новый пустой volume и контейнер бд подняла:
![alt text](image-9.png)

Восстановила архив, запустила с тем же образом, заметка на месте:
![alt text](image-10.png)

## 7. Сетевая изоляция
Просто скрин покажу
![alt text](image-11.png)

TCP подключение не работает:
![alt text](image-12.png)

## 8. Переменные и имя Compose-проекта
Итог `docker compose config`: [link](пруфы_трудов/compose-config.redacted.txt)

Имя проекта достается из `COMPOSE_PROJECT_NAME` в `.env`, а `name` из `compose.yaml` игнорируется, так как приоритет ниже.

## 9. Анализ и оптимизация образа в dive

### Анализ образа до оптимизации
Это dive с изначальным Dockerfile
![dive before](image-3.png)

Команды:
```bash
docker build --no-cache -t homework2-app:before .
docker image inspect homework2-app:before --format 'ID={{.Id}} Size={{.Size}} bytes'
CI=true dive homework2-app:before
```

![alt text](image-5.png)

Полученные показатели есть тут [link](пруфы_трудов/dive-before.txt). Но вынесу в табличку:

| Показатель          | До оптимизации |
|---------------------|----------------|
| Размер образа       | 240343125 bytes|
| Efficiency score    | 97.6078 %      |
| Wasted bytes        | 5651651 bytes (5.7 MB) |
| User wasted percent | 6.6400 %       |
| Результат dive      | PASS           |


### Анализ образа после оптимизации


## 10. Различие down и down -v


## 11. Очистка ресурсов