**Для запуска проекта у вас должен быть установлен:**

    1. Python 3.7<
    2. MongoDB 5.0<
    3. Elasticsearch 7.14.1<

**После скачивания репозитория нужно:**

    1. Создать и запустить virtual environment
    2. Установить зависимости из requirements.txt (Не забываем обновить pip)
    3. Задать значение для двух переменных окружения 
        FLASK_APP=index.py,
        API_TOKEN
    4. В файле index.py необходимо указать URI для mongodb
    5. Убедится, что сервер mongodb и elasticsearch запущены
    6. Запустить приложение командой: `flask run`