# OracleStruct
В данном репозитории представлен набор скриптов, позволяющих выполнить экспорт и импорт структуры БД Oracle, а так же, перенести данные из БД источника в целевую (локальную). Весь процесс делится на несколько этапов.


### Экспорт структуры

Запускается скриптом _export_struct.cmd_. После запуска в интерактивном режиме от вас потребуется ввести три параметра: псевдоним БД, имя пользователя (структуры) и пароль. После введения этих параметров скрипт подключится к БД и начнёт выгружать DDL всех объектов в текстовый файл _struct.sql_ (будет размещен в той же директории, от куда вы запускали _export_struct.cmd_). Выгрузка займёт некоторое время, прогресс будет отображаться в консоли. Перечень выгружаемых объектов:
- Таблицы
- Представления
- Индексы
- Типы
- Пакеты
- Триггеры
- Последовательности


### Создание пользователя

На данном этапе вам требуется создать нового пользователя (в локальной БД или удалённой - все равно), в которого вы будете импортировать схему, полученную в результате экспорта в предыдущем пункте.  Если пользователь уже существует, вы можете удалить его следующим запросом:
```
DROP USER SUPER_USER CASCADE;
```
Где SUPER_USER - имя вашего пользователя.

Если пользователь не существует - используйте набор запросов ниже:
```
CREATE USER SUPER_USER IDENTIFIED BY "1";
GRANT ALL PRIVILEGES TO SUPER_USER;
GRANT DBA TO SUPER_USER;
GRANT EXECUTE ON dbms_flashback TO SUPER_USER;
GRANT EXECUTE ON dbms_crypto TO SUPER_USER;
```
Первый запрос - запрос на создание пользователя SUPER_USER с паролем 1. Остальные запросы - установка привилегий (прав).

### Установка структуры

Запускается скриптом _install_struct.cmd_. Как и в пункте про экспорт, от вас потребуется ввести данные подключения к БД (псевдоним, имя пользователя и пароль). В данном случае вы уже подключаетесь к БД, в которую будет установлена структура. Во время установки вы можете увидеть предупреждения - это нормально. Главное после завершения установки просмотрите объекты БД на предмет их наличия. На этом процесс экспорта и импорта структуры окончен. Если данные в новой БД вам не нужны - на этом можно закончить.

### Копирование данных

Запускается скриптом _fill_data.cmd_. По аналогии с предыдущими скриптами, вам потребуется ввести данных подключения к БД. перед запуском убедитесь, что рядом со скриптом лежит файл _tables.sql_. В нём построчно должны быть перечислены имена таблиц, данные которых будут скопированы. В файле поддерживаются комментарии через символ #. Копирование займет некоторое время, прогресс вы увидите в консоли.
