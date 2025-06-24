import mysql.connector
import configparser
from datetime import datetime

# 读取配置文件 
def read_config():
    cf = configparser.ConfigParser()
    cf.read('config.ini', encoding="utf-8")
    return cf

cf = read_config()
cf_tag = 'mysql-config'
host = cf.get(cf_tag, 'host')
user = cf.get(cf_tag, 'user')
pwd = cf.get(cf_tag, 'pwd')
database = cf.get(cf_tag, 'database')

mysql_conn = mysql.connector.connect(
    host=host,
    user=user,
    password=pwd,
    database=database
)

def insert_block_history(datalist):
    """log写入mysql block_count_history表"""
    try:
        cursor = mysql_conn.cursor()
        sql = "INSERT INTO block_count_history (ip, ja3, country, ruleid, ruledetail, block_count, insert_time) VALUES (%s, %s, %s, %s,  %s, %s, %s)"
        cursor.execute(sql, (datalist[0],datalist[1],datalist[2],datalist[3],datalist[4],datalist[5],datetime.now()))
        mysql_conn.commit()
        cursor.close()
        return True
    except Exception as e:
        print(f"Error inserting block history: {str(e)}")
        return False


def insert_new_blockips(ip, ja3):
    """ip写入/更新 mysql block_ip_set表"""
    try:
        cursor = mysql_conn.cursor()
        now = datetime.now()
        sql = """
        INSERT INTO block_ip_set (ip, ja3, block_value, insert_time, update_time) 
        VALUES (%s, %s, 1, %s, %s)
        ON DUPLICATE KEY UPDATE block_value = 1, update_time = %s
        """
        cursor.execute(sql, (ip, ja3, datetime.now(), datetime.now(), datetime.now()))
        mysql_conn.commit()
        cursor.close()
        return True
    except Exception as e:
        print(f"Error updating block IP set: {str(e)}")
        return False

def update_expire_blockips():
    """将对N天的移出block IP set"""
    try:
        cursor = mysql_conn.cursor()
        now = datetime.now()
        sql = """
        update block_ip_set set block_value = 0 where update_time < date_sub(now(), interval 3 day)
        """
        cursor.execute(sql)
        mysql_conn.commit()
        cursor.close()
        return True
    except Exception as e:
        print(f"Error updating block IP set: {str(e)}")
        return False


def get_allblock_ips():
    """获取mysql block ip 3天内的被阻止的 ip"""
    try:
        cursor = mysql_conn.cursor()
        sql = "SELECT ip FROM block_ip_set WHERE block_value = 1 AND update_time > DATE_SUB(CURDATE(), INTERVAL 3 DAY)"
        cursor.execute(sql)
        results = cursor.fetchall()
        cursor.close()
        return results
    except Exception as e:
        print(f"Error getting block IPs: {str(e)}")
        return []


def insert_exception_detail(datalist):
    """log写入mysql allow_exception_detail"""
    try:
        cursor = mysql_conn.cursor()
        sql = "INSERT INTO allow_exception_detail (request_value, type, soure_value, exception_des, exception_type, opt_suggest, insert_time) VALUES (%s, %s, %s, %s,  %s, %s, %s)"
        cursor.execute(sql, (datalist[0],datalist[1],datalist[2],datalist[3],datalist[4],datalist[5],datetime.now()))
        mysql_conn.commit()
        cursor.close()
        return True
    except Exception as e:
        print(f"Error inserting exception detail: {str(e)}")
        return False

def get_ja3_exception_list():
    """获取X天内 异常请求的JA3"""
    try:
        cursor = mysql_conn.cursor()
        sql = "SELECT distinct request_value FROM allow_exception_detail WHERE type = 'ja3' AND insert_time > DATE_SUB(CURDATE(), INTERVAL 3 DAY)"
        cursor.execute(sql)
        results = cursor.fetchall()
        cursor.close()
        return results
    except Exception as e:
        print(f"Error getting block IPs: {str(e)}")
        return []


def close_mysql_connection():
    try:
        if mysql_conn.is_connected():
            mysql_conn.close()
    except Exception as e:
        print(f"Error closing MySQL connection: {str(e)}")
