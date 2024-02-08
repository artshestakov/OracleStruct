import oracledb
import time
import re
import os

db_user = "ASSERVER"
db_password = "NCTASSERVER"
db_alias = "AS_STK_TEST_4"
object_global_cnt = 0
object_map = dict()
current_dir = os.path.abspath(__file__).replace(os.path.basename(__file__), "")

# ---------------------------------------------------------------------------------------
def export(cursor, type, sql_for_objects, file):
    global object_global_cnt
    global object_map

    #Запрашиваем список объектов
    print("Select object list for {}...".format(type))
    string_list = []
    result = cursor.execute(sql_for_objects)
    for row in result:
        string_list.append(row[0])

    object_cnt = len(string_list)
    object_map[type] = object_cnt
    object_global_cnt += object_cnt
    idx = 0

    for object_name in string_list:
        idx += 1
        print("Getting DDL for {} ({} of {}) {}"
              .format(type, idx, object_cnt, object_name))
        r = cursor.execute("SELECT dbms_metadata.get_ddl('{}', '{}') AS sql_ddl FROM dual"
                           .format(type, object_name))
        sql_text = cursor.fetchone()[0]
        sql_text = str(sql_text)

        #Убираем имя пользовтаеля перед объектом. Например, CREATE TABLE "ASSERVER"."REFUSAL"
        sql_text = sql_text.replace("\"" + db_user + "\".", str())

        #Убираем включение триггеров
        if type == "TRIGGER":
            sql_text = re.sub("ALTER TRIGGER \".+\" .+", str(), sql_text)

        file.write("-- " + object_name)
        file.write(str(sql_text))
        file.write("\n/")
        file.write("\n\n")
        file.flush()
# ---------------------------------------------------------------------------------------
def write_db_link(file):
    sql = ("CREATE DATABASE LINK {}\n"
           "CONNECT TO {} IDENTIFIED BY {}\n"
           "USING '{}'\n"
           "/\n"
           .format(db_alias, db_user, db_password, db_alias))
    file.write(sql)
# ---------------------------------------------------------------------------------------
def ask_continue():
    res = True
    while True:
        letter = input("You connected to the database {} AS '{}'. Do you want to continue? (y/n): "
                       .format(db_alias, db_user))
        letter = str(letter.lower())

        if letter != 'y' and letter != 'n':
            print("Invalid answer! You can use either 'y' or 'n'")
            continue
        res = letter == 'y'
        break
    return res
# ---------------------------------------------------------------------------------------

#Подключаемся к БД
print("Connecting...")
try:
    connection = oracledb.connect(user=db_user, password=db_password, dsn=db_alias)
except Exception as e:
    print("Can't connect to the database: " + str(e))
    exit(1)

#Уточним у пользователя, хотим ли мы продолжать
if not ask_continue():
    print("Exit...")
    exit(0)

cursor = connection.cursor()
file_path = current_dir + "struct.sql"
file = open(file_path, 'w', encoding='utf-8')

time_start = time.time()
#export(cursor, "TABLE","SELECT table_name FROM user_tables ORDER BY table_name", file)
export(cursor, "VIEW","SELECT view_name FROM user_views ORDER BY view_name", file)
#export(cursor, "INDEX", "SELECT i.index_name FROM user_indexes i WHERE i.index_name NOT IN (SELECT p.constraint_name FROM user_constraints p WHERE p.table_name = i.table_name AND p.constraint_type IN ('P', 'U')) ORDER BY i.index_name", file)
#export(cursor, "TYPE", "SELECT type_name, dbms_metadata.get_ddl('TYPE', type_name) FROM user_types WHERE typecode = 'OBJECT' ORDER BY type_name", file)
#export(cursor, "TYPE", "SELECT type_name, dbms_metadata.get_ddl('TYPE', type_name) FROM user_types WHERE typecode = 'COLLECTION' ORDER BY type_name", file)
#export(cursor, "PACKAGE_SPEC", "SELECT object_name FROM user_objects WHERE object_type = 'PACKAGE' ORDER BY object_name", file)
#export(cursor, "PACKAGE_BODY", "SELECT object_name FROM user_objects WHERE object_type = 'PACKAGE' ORDER BY object_name", file)
#export(cursor, "TRIGGER", "SELECT object_name FROM user_objects WHERE object_type = 'TRIGGER' AND object_name != 'TRG_INSTALL_LOG_DDL_ONL' ORDER BY object_name", file)
#export(cursor, "SEQUENCE", "SELECT sequence_name FROM user_sequences ORDER BY sequence_name", file)
write_db_link(file)
time_diff = time.time() - time_start

file.close()
print("Finish. Exported objects {} for {} msec"
      .format(object_global_cnt, f'{time_diff:.3f}'))

for map_key in object_map:
    print("{}: {}".format(map_key, object_map[map_key]))
print("File path: " + file_path)
