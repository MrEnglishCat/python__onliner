Доброго времени суток =)


1) Содержание файла ".env" для работы проекта. Расположение данного файла: там же(в том же каталоке,
рядом с каталогом проекта) где и каталог проекта/.venv.

    DB_NAME=<имя БД>
    DB_USER=<имя пользователя для подключения к БД>
    DB_PASSWORD=<пароль пользователя для подключения к БД>
    DB_HOST=localhost
    DB_PORT=5432


2) Список зависимостей в "requirements.txt"
    python -m pip install -r requirements.txt

3) файл notebook/parser/base_parser.by
    Строки кода 89 - 90 (примерно). Есть запись ограничивающая парсинг до 1й страницы(это первая страница).
    С какой страницы начинать парсинг регулируется атрибутами "__PAGE_COUNTER" и "__LIMIT_PAGE_COUNTER"
    класса "BaseParser".

            #  break ниже для парсинга страниц ограниченных атрибутом "__LIMIT_PAGE_COUNTER"
            break

4) Есть API и 1 ссылка для запуска парсера
                Parse:
        start_parser/

                API:
        api/swagger<format>/ --- swagger
        api/swagger/ --- swagger
        api/redoc/ --- документация от swagger
                Admin:
        admin/ --- админка