import oracledb
import time
import os
import datetime
import getpass

db_alias = input("Enter the database alias: ")
db_user = input("Enter the database user: ")
db_password = getpass.getpass("Enter the database password: ")
table_index = 0
file_tables_path = os.path.abspath(__file__).replace(os.path.basename(__file__), "") + "tables.txt"

# ---------------------------------------------------------------------------------------
def get_db_link(cursor):
    try:
        cursor.execute("SELECT db_link FROM user_db_links")
        db_link = cursor.fetchone()[0]
        return db_link
    except Exception as e:
        print("Can't get db_link. " + str(e))
    return None
# ---------------------------------------------------------------------------------------
def get_trigger_list(cursor):
    try:
        r = cursor.execute("SELECT trigger_name FROM user_triggers ORDER BY trigger_name")
        trigger_list = []
        for trigger_name in r:
            trigger_list.append(trigger_name[0])
        return trigger_list
    except Exception as e:
        print("Can't get the trigger list: " + str(e))
    return None
# ---------------------------------------------------------------------------------------
def get_table_list():
    try:
        file_tables = open(file_tables_path, 'r')
        table_list = file_tables.read().splitlines()
        file_tables.close()

        # Удаляем все пустые строки из списка
        while (str() in table_list):
            table_list.remove(str())
        return table_list
    except Exception as e:
        print("Can't get the table list. " + str(e))
    return None
# ---------------------------------------------------------------------------------------
def set_triggers(is_enable):
    action = "ENABLE" if is_enable else "DISABLE"
    try:
        for trigger_name in trigger_list:
            cursor.execute("ALTER TRIGGER " + trigger_name + " " + action)
        return True
    except Exception as e:
        print("Can't set active (to {}) trigger. {}"
              .format(action, e))
    return False
# ---------------------------------------------------------------------------------------
oracledb.init_oracle_client()

# Подключаемся к БД и получаем курсор
print("Connecting to {} as {}...".format(db_alias, db_user))
try:
    connection = oracledb.connect(user=db_user, password=db_password, dsn=db_alias)
except Exception as e:
    print("Can't connect to the database: " + str(e))
    exit(1)
cursor = connection.cursor()

# Получаем DBLink
db_link = get_db_link(cursor)
if db_link == None:
    exit(1)

# Получаем список триггеров для дальнейшего отключения и включения
trigger_list = get_trigger_list(cursor)
if trigger_list == None:
    exit(1)

# Вытаскиваем список таблиц
table_list = get_table_list()
if table_list == None:
    exit(1)

# Отключаем триггеры
print("Disable tiggers...")
if set_triggers(False) == False:
    exit(1)

time_start = time.time()
for table_name in table_list:
    table_index += 1

    # Пропускаем таблицу, если надо
    if table_name[0] == '#':
        print("Skip table " + table_name)
        continue

    # Смотрим сколько записей в таблице
    try:
        cursor.execute("SELECT COUNT(*) FROM {}@{}"
                           .format(table_name, db_link))
        cnt = cursor.fetchone()[0]
        print("[{}] Table ({} of {}) {} has {} rows. Start copy... "
              .format(datetime.datetime.now(), table_index, len(table_list), table_name, cnt), end='', flush=True)
    except Exception as e:
        print("Can't select count from table {}. {}".format(table_name, e))
        continue

    # Копируем данные
    t_msec = time.time()
    cursor.execute("INSERT INTO {} SELECT * FROM {}@{}"
                   .format(table_name, table_name, db_link))
    t_msec = time.time() - t_msec
    print("OK. {} msec ({} min)".format(f'{t_msec:.3f}', int(t_msec / 60)))
time_diff = time.time() - time_start

print("Enable tiggers...")
if set_triggers(True) == False:
    print("But I will continue...")

print("\nFinish for {} msec ({} min)"
      .format(f'{time_diff:.3f}', int(time_diff / 60)))
