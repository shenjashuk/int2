# int2
Это проект для продключения по SSH к локальным устройствам и парсинга информации об их системе (информация о дистрибутиве, процессоре, оперативной памяти).
На данный момент приложение поддерживает устройства линукс. Для хранения информации об устройствах используется postgres.
Для использования самостоятельного использования следует изменить файл main.py
В следующих строках(8 - 14) следует ввести собственные данные:
connection_params = {
    'dbname': 'your_database',
    'user': 'your_user',
    'password': 'your_password',
    'host': 'localhost',
    'port': 5432
}
По надобности можно изменить порт.
