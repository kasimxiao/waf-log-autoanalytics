import mysql.connector
import configparser

# 读取配置文件
def read_config():
    cf = configparser.ConfigParser()
    cf.read('config.ini', encoding="utf-8")
    return cf

cf = read_config()

# 获取MySQL配置
host = cf.get('mysql-config', 'host')
user = cf.get('mysql-config', 'user')
pwd = cf.get('mysql-config', 'pwd')
database = cf.get('mysql-config', 'database')

def get_connection():
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=pwd,
            database=database
        )
        return connection
    except Exception as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def execute_query(query, params=None):
    connection = get_connection()
    if not connection:
        return None

    try:
        cursor = connection.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        if query.strip().upper().startswith('SELECT'):
            result = cursor.fetchall()
            return result
        else:
            connection.commit()
            return cursor.rowcount

    except Exception as e:
        print(f"Error executing query: {e}")
        return None

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def insert_record(table, data):
    # 构建INSERT语句
    columns = ', '.join(data.keys())
    values = ', '.join(['%s'] * len(data))
    query = f"INSERT INTO {table} ({columns}) VALUES ({values})"

    return execute_query(query, tuple(data.values()))

def update_record(table, data, condition):
    # 构建UPDATE语句
    set_clause = ', '.join([f"{k} = %s" for k in data.keys()])
    where_clause = ' AND '.join([f"{k} = %s" for k in condition.keys()])
    query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"

    # 合并参数
    params = tuple(list(data.values()) + list(condition.values()))
    return execute_query(query, params)

def delete_record(table, condition):
    # 构建DELETE语句
    where_clause = ' AND '.join([f"{k} = %s" for k in condition.keys()])
    query = f"DELETE FROM {table} WHERE {where_clause}"

    return execute_query(query, tuple(condition.values()))