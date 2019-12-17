# Дата создания: 31.05.2019
# Автор: Ходжаев Сергей Искандарович
# Почта автора: wingrada@gmail.com

# Название программы: Synchronization json file to sqlite

# Принцип работы: Программа синхронизирует данные из json в sqlite,
# Создает соединение с slite, если файла sqlite нету, создается новый.
# Создает таблицу если она не существует.
# Сравнивает два списка данных(json, sqlite) и, в зависимости от результата,
#     удаляет, добавляет или изменяет данные в sqlite
#
# При выполнении учитывается что данные уже проверены, и не требуется валидация.

import sqlite3
import json


db = sqlite3.connect('sqlite_db.sqlite', timeout=5.0)
cursor = db.cursor()


def sync(json_file, table_name):
    create_table(table_name)

    json_data = get_list_values_from_json(json_file)
    sqlite_data = get_sqlite_as_json(table_name)

    if is_delete(sqlite_data, json_data):
        delete(sqlite_data, json_data)

    if is_add(sqlite_data, json_data):
        try:
            add(sqlite_data, table_name, json_data)

        except sqlite3.IntegrityError:
            change(sqlite_data, json_data)

    print("Everything is good :! ")


def create_table(table_name):
    cursor.execute(f'''CREATE TABLE IF NOT EXISTS {table_name} (
                              name TEXT NOT NULL,
                              email TEXT PRIMARY KEY NOT NULL ,
                              active TEXT NOT NULL)
    ''')


def delete(sqlite_data, json_data):
    """Удаление происходит в двух случаях:
    Если пользователь был удален из json,
    Если пользователь изменил почту(уникальный элемент в sqlite)
    """
    emails_to_delete = get_list_emails_to_delete(sqlite_data, json_data)

    query = 'DELETE FROM data_personnel WHERE email IN ({})'.format(", ".join("?" * len(emails_to_delete)))
    cursor.execute(query, emails_to_delete)

    print("Something deleted :(")


def change(sqlite_data, json_data):
    """ Изменяю строки в которых были изменения, изменению подвергаются name и email """
    changed_rows = get_list_changed_rows_in_json(sqlite_data, json_data)
    swap(changed_rows)   # Меняю местами email с active

    for items in changed_rows:
        sql = "UPDATE data_personnel SET name=?, active=? WHERE email=?"
        cursor.execute(sql, items)

    print("Something changed xD ")


def add(sqlite_data, table_name, json_data):
    list_to_add = get_list_to_add(sqlite_data, json_data)

    cursor.executemany(f"INSERT INTO {table_name} VALUES (?,?,?)", list_to_add)
    print("Something added :)")


def is_delete(sqlite_data, json_data):
    """ Возвращает False, если ни одно условие не верно """
    if len(get_list_emails_to_delete(sqlite_data, json_data)) > 0:
        return True

    return False


def is_add(sqlite_data, json_data):
    if len(get_list_to_add(sqlite_data, json_data)) > 0:
        return True

    return False


def get_list_to_add(sqlite_data, json_data):
    return [item for item in json_data if item not in sqlite_data]


def get_list_emails_to_delete(sqlite_data, json_data):
    sqlite_emails = get_emails(sqlite_data)
    json_emails = get_emails(json_data)

    return [email for email in sqlite_emails if email not in json_emails]


def get_list_changed_rows_in_json(sqlite_data, json_data):
    return [list(item) for item in json_data if item not in sqlite_data]


def get_list_values_from_json(json_file):
    """ Получаю из списка словарей значение, далее записываю в список списков и возвращаю """
    json_data = read_json(json_file)

    return [list(part_data.values()) for part_data in json_data]


def get_sqlite_as_json(table_name):
    """ Получаю список кортежей из бд и преобразую его в список списков, для изменнений в дальнейшем """
    cursor.execute(f"SELECT * FROM {table_name}")
    list_tuples = cursor.fetchall()

    sqlite_in_list = [list(item) for item in list_tuples]
    convert_sqlite_in_json(sqlite_in_list)

    return sqlite_in_list


def get_emails(data):
    """ Получаю почту по индексу """
    return [email[1] for email in data]


def convert_sqlite_in_json(sqlite_data):
    """Конвертирую Оригинальные данные получение из бд в аналог json"""
    for i in range(len(sqlite_data)):

        if sqlite_data[i][2] == '0':
            sqlite_data[i][2] = False

        elif sqlite_data[i][2] == '1':
            sqlite_data[i][2] = True

        else:
            print("Слушай... в функции 'conver_sqlite', что то пошло не так")


def read_json(json_file):
    """Читает JSON файл, и возвращает полученый список"""
    try:
        with open(json_file, 'r') as js:
            return json.load(js)

    except FileNotFoundError:
        print(f"Error: {json_file} is empty")


def swap(data):
    for items in data:
       items[1], items[2] = items[2], items[1]


sync('hr_db.json', 'data_personnel')
db.commit()
db.close()
