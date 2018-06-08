## Системные требования

1. Python версии не ниже 3.5 ([ссылка для скачивания](https://www.python.org/ftp/python/3.6.5/python-3.6.5.exe))

## Использование парсера (как модуль)

```
import converter

converter.convert(
    logs_file,       # Путь к файлу с логами
    struct_file,     # Путь к XML-файлу со структурой курса
    quests_file,     # Список путей к файлам с ответами
    quests_encoding, # Кодировка файлов с ответами
    log_encoding,    # Кодировка файла логов
    delimiter,       # CSV-разделитель файла с логами
    output           # Каталог, в который выводить результат
)
```

Если какие-то файлы отсутствуют, необходимо передать пустую строку.

Каталог, в который будет выводиться результат, должен быть предварительно создан.

## Использование парсера (как отдельное приложение)

Парсер преобразует логи Moodle в формат 5CSV.

### Формат данных

Парсер работает со следующими данными:

1. Лог-файл Moodle

    Файл имеет формат CSV (с названиями колонок) с разделителем `,`. Колонки должны иметь названия:
    * Время
    * Полное имя пользователя
    * Затронутый пользователь
    * Контекст события
    * Компонент
    * Название события
    * Описание

1. Файлы ответов студентов

    Файл имеет формат CSV (с названиями колонок) с разделителем `,`. Колонки должны иметь названия:
    * Фамилия
    * Имя
    * Учреждение (организация)
    * Отдел
    * Адрес электронной почты
    * Состояние
    * Тест начат
    * Завершено
    * Затраченное время
    * Оценка/10,00
    * Вопрос N
    * Ответ N
    * Правильный ответ: N
    * ...

    Для каждого теста должен быть выгружен отдельный файл ответов.

    Название файла должно иметь вид "название_теста.csv".

### Запуск

1. Запустить парсер

    ```
    $ python main.py --logs ../data/logs --struct ../data/imsmanifest.xml --quests ../data/Test1.csv ../data/Test2.csv -- csv
    ```

    * Файл `../data/logs` — лог-файл Moodle
    * Файл `../data/imsmanifest.xml` — файл со структурой курса
    * Файлы `../data/Test1.csv`, `../data/Test2.csv` — файлы ответов студентов (на тесты `Test1` и `Test2`)

1. Результатом работы будут файлы `csv{1..5}.csv` в текущем каталоге.

При использовании парсера в параметрах запуска можно указать кодировку файлов.

* Кодировка лог-файла: `-e utf8` (по умолчанию используется utf-8 с BOM)
* Кодировка файлов с ответами: `-E cp1251` (по умолчанию используется utf-8 с BOM)

При использовании парсера в параметре `-d` можно указать CSV-разделитель в логах.

### Настройка каталога для вывода результатов

Для изменения каталога вывода результата его нужно передать последним аргументом при запуске:
```
$ python main.py --logs ../data/logs --struct ../data/imsmanifest.xml --quests ../data/Test1.csv ../data/Test2.csv -- my/catalog/
```

Результатом будут файлы `my/catalog/csv{1..5}.csv`.